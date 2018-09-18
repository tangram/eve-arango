import json
import re
from datetime import datetime

from eve.io.base import DataLayer
from eve.utils import str_to_date
from arango import ArangoClient


def date_hook(json_data):
    for key, value in json_data.items():
        try:
            json_data[key] = str_to_date(value)
        except:
            pass
    return json_data


def parse_where(where):
    arango_re = (
        r'([\w-]+?)([\s!=<>~NOTLIKE]+)(".+?"|[\d\s\[\]nul,.]+)([ANDORT,]*)'
    )
    result = re.findall(arango_re, where)
    return result


class ArangoResult(list):

    def __init__(self, cursor):
        self.cursor = cursor
        batch = list(cursor.batch())
        processed_result = json.loads(json.dumps(batch), object_hook=date_hook)
        super().__init__(processed_result)

    def count(self, with_limit_and_skip=False, **kwargs):
        return self.cursor.statistics().get('fullCount')


class ArangoDB(DataLayer):

    def init_app(self, app):
        db = app.config.get('ARANGO_DB', app.name)
        host = app.config.get('ARANGO_HOST', 'localhost')
        port = app.config.get('ARANGO_PORT', 8529)

        self.driver = ArangoClient(host=host, port=port)

        if not self.driver.db('_system').has_database(db):
            self.driver.db('_system').create_database(db)

        self.db = self.driver.db(db)

        for resource, settings in app.config['DOMAIN'].items():
            edge = settings.get('edge_collection', False)
            if not self.db.has_collection(resource):
                self.db.create_collection(resource, edge=edge)

    def find(self, resource, req, sub_resource_lookup):
        """ Retrieves a set of documents (rows), matching the current request.
        Consumed when a request hits a collection/document endpoint
        (`/people/`).
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve both
                         the db collection/table and base query (filter), if
                         any.
        :param req: an instance of ``eve.utils.ParsedRequest``. This contains
                    all the constraints that must be fulfilled in order to
                    satisfy the original request (where and sort parts, paging,
                    etc). Be warned that `where` and `sort` expressions will
                    need proper parsing, according to the syntax that you want
                    to support with your driver. For example ``eve.io.Mongo``
                    supports both Python and Mongo-like query syntaxes.
        :param sub_resource_lookup: sub-resource lookup from the endpoint url.
        """
        filters = ''
        if req and req.where:
            groups = parse_where(req.where)
            filters += 'FILTER '
            for group in groups:
                key, op, val, sep = group
                filters += f'doc.{key} {op} {val}'
                if sep == ',':
                    filters += '\nFILTER '
                elif sep:
                    filters += f' {sep} '

        sort = ''
        if req and req.sort:
            sorts = []
            fields = req.sort.split(',')
            for field in fields:
                if field[0] == '-':
                    sorts.append(f'doc.{field[1:]} DESC')
                else:
                    sorts.append(f'doc.{field}')
            sort += 'SORT '
            sort += ', '.join(sorts)

        skip = 0
        limit = req.max_results
        if req and req.page and req.max_results:
            skip = (req.page - 1) * req.max_results or 0

        collection, _, _, _ = self.datasource(resource)
        query = f'''
        FOR doc IN {collection}
            {filters}
            {sort}
            LIMIT {skip}, {limit}
            RETURN doc
        '''
        cursor = self.db.aql.execute(query, full_count=True)

        return ArangoResult(cursor)

    def find_one(self, resource, req, check_auth_value=True,
                 force_auth_field_projection=False, **lookup):
        """ Retrieves a single document/record. Consumed when a request hits an
        item endpoint (`/people/id/`).
        :param resource: resource being accessed. You should then use the
                         ``datasource`` helper function to retrieve both the
                         db collection/table and base query (filter), if any.
        :param req: an instance of ``eve.utils.ParsedRequest``. This contains
                    all the constraints that must be fulfilled in order to
                    satisfy the original request (where and sort parts, paging,
                    etc). As we are going to only look for one document here,
                    the only req attribute that you want to process here is
                    ``req.projection``.
        :param check_auth_value: a boolean flag indicating if the find
                                 operation should consider user-restricted
                                 resource access. Defaults to ``True``.
        :param force_auth_field_projection: a boolean flag indicating if the
                                            find operation should always
                                            include the user-restricted
                                            resource access field (if
                                            configured). Defaults to ``False``.
        :param **lookup: the lookup fields. This will most likely be a record
                         id or, if alternate lookup is supported by the API,
                         the corresponding query.
        """
        collection, _, _, _ = self.datasource(resource)
        result = self.db.collection(collection).get(lookup)
        processed_result = json.loads(json.dumps(result), object_hook=date_hook)
        return processed_result

    def find_one_raw(self, resource, **lookup):
        """ Retrieves a single, raw document. No projections or datasource
        filters are being applied here. Just looking up the document using the
        same lookup.
        :param resource: resource name.
        :param ** lookup: lookup query.
        """
        collection, _, _, _ = self.datasource(resource)
        result = self.db.collection(collection).get(lookup)
        return result

    def find_list_of_ids(self, resource, ids, client_projection=None):
        """ Retrieves a list of documents based on a list of primary keys
        The primary key is the field defined in `ID_FIELD`.
        This is a separate function to allow us to use per-database
        optimizations for this type of query.
        :param resource: resource name.
        :param ids: a list of ids corresponding to the documents
        to retrieve
        :param client_projection: a specific projection to use
        :return: a list of documents matching the ids in `ids` from the
        collection specified in `resource`
        """
        collection, _, _, _ = self.datasource(resource)
        result = self.db.collection(collection).get_many(ids)
        return result

    def insert(self, resource, doc_or_docs):
        """ Inserts a document into a resource collection/table.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve both
                         the actual datasource name.
        :param doc_or_docs: json document or list of json documents to be added
                            to the database.
        """
        if isinstance(doc_or_docs, dict):
            doc_or_docs = [doc_or_docs]

        data = json.loads(json.dumps(doc_or_docs, cls=self.json_encoder_class))

        collection, _, _, _ = self.datasource(resource)
        result = self.db.collection(collection).insert_many(data)
        return result

    def update(self, resource, id_, updates, original):
        """ Updates a collection/table document/row.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param id_: the unique id of the document.
        :param updates: json updates to be performed on the database document
                        (or row).
        :param original: definition of the json document that should be
        updated.
        :raise OriginalChangedError: raised if the database layer notices a
        change from the supplied `original` parameter.
        """
        if updates and '_key' not in updates:
            updates['_key'] = id_

        data = json.loads(json.dumps(updates, cls=self.json_encoder_class))

        collection, _, _, _ = self.datasource(resource)
        result = self.db.collection(collection).update(data)
        return result

    def replace(self, resource, id_, document, original):
        """ Replaces a collection/table document/row.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param id_: the unique id of the document.
        :param document: the new json document
        :param original: definition of the json document that should be
        updated.
        :raise OriginalChangedError: raised if the database layer notices a
        change from the supplied `original` parameter.
        """
        if document and '_key' not in document:
            document['_key'] = id_

        data = json.loads(json.dumps(document, cls=self.json_encoder_class))

        collection, _, _, _ = self.datasource(resource)
        result = self.db.collection(collection).replace(data)
        return result

    def remove(self, resource, lookup):
        """ Removes a document/row or an entire set of documents/rows from a
        database collection/table.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param lookup: a dict with the query that documents must match in order
                       to qualify for deletion. For single document deletes,
                       this is usually the unique id of the document to be
                       removed.
        """
        collection, _, _, _ = self.datasource(resource)
        result = self.db.collection(collection).delete_match(lookup)
        return result

    def is_empty(self, resource):
        """ Returns True if the collection is empty; False otherwise. While
        a user could rely on self.find() method to achieve the same result,
        this method can probably take advantage of specific datastore features
        to provide better performance.
        Don't forget, a 'resource' could have a pre-defined filter. If that is
        the case, it will have to be taken into consideration when performing
        the is_empty() check (see eve.io.mongo.mongo.py implementation).
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        """
        collection, _, _, _ = self.datasource(resource)
        return self.db.collection(collection).count() == 0
