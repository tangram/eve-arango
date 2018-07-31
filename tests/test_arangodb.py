import os
import json

import pytest

from arango import ArangoClient
from eve import Eve
from eve.utils import ParsedRequest
from eve_arango.arangodb import ArangoDB, ArangoResult


@pytest.fixture(scope='module')
def app():
    app = Eve(settings='test_settings.py')

    test_app = app.test_client()
    context = app.app_context()

    context.push()
    yield test_app.application
    context.pop()


@pytest.fixture(scope='module')
def data_layer(app):
    # DELETES the database before tests!
    db = 'test_database_disposable'
    host = app.config.get('ARANGO_HOST')
    port = app.config.get('ARANGO_PORT')
    client = ArangoClient(host=host, port=port)
    if client.db('_system').has_database(db):
        client.db('_system').delete_database(db)

    data_layer = ArangoDB(app)

    file_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(file_path, 'test_data.json')
    with open(json_path, 'r') as json_file:
        test_data = json.load(json_file)

        for collection, obj in test_data.items():
            data_layer.db.collection(collection).insert(obj)

    return data_layer


def test_init_app(app, data_layer):
    # init_app() called by ArangoDB.__init__()
    assert data_layer.driver is not None
    assert data_layer.db.name == 'test_database_disposable'
    assert data_layer.driver.host == app.config.get('ARANGO_HOST')
    assert data_layer.driver.port == app.config.get('ARANGO_PORT')


def test_find(data_layer):
    resource = 'musicians'
    sub_resource_lookup = None
    # test data has 3 musicians
    # filter defaults to None
    req = ParsedRequest()
    results = data_layer.find(resource, req, sub_resource_lookup)
    assert len(results) == 3
    assert results[0]['name'] == 'Miles Davis'
    assert results[1]['name'] == 'John Coltrane'
    assert results[2]['name'] == 'Bill Evans'


def test_find_where(data_layer):
    resource = 'musicians'
    sub_resource_lookup = None
    req = ParsedRequest()
    req.where = '{"name": "Bill Evans"}'
    results = data_layer.find(resource, req, sub_resource_lookup)
    assert len(results) == 1
    assert results[0]['name'] == 'Bill Evans'


def test_pagination(data_layer):
    resource = 'instruments'
    sub_resource_lookup = None
    req = ParsedRequest()
    req.max_results = 3
    req.page = 2
    results = data_layer.find(resource, req, sub_resource_lookup)
    assert len(results) == 2


def test_find_one(data_layer):
    resource = 'musicians'
    req = ParsedRequest()
    # test lookup by _key
    lookup = {'_key': '1'}
    result = data_layer.find_one(resource, req, **lookup)
    assert result['name'] == 'Miles Davis'


def test_find_one_raw(data_layer):
    resource = 'musicians'
    # test lookup by _id
    lookup = {'_id': 'musicians/2'}
    result = data_layer.find_one_raw(resource, **lookup)
    assert result['name'] == 'John Coltrane'


def test_find_list_of_ids(data_layer):
    resource = 'musicians'
    ids = ['1', '2', '3']
    results = data_layer.find_list_of_ids(resource, ids)
    assert results[0]['name'] == 'Miles Davis'
    assert results[1]['name'] == 'John Coltrane'
    assert results[2]['name'] == 'Bill Evans'


def test_insert(data_layer):
    resource = 'musicians'
    doc_or_docs = {'name': 'Thelonious Monk'}
    result = data_layer.insert(resource, doc_or_docs)
    assert len(result) == 1
    assert result[0].get('_id') is not None


def test_insert_many(data_layer):
    resource = 'musicians'
    doc_or_docs = [
        {'name': 'Herbie Hancock'},
        {'name': 'Chick Corea'},
    ]
    result = data_layer.insert(resource, doc_or_docs)
    assert len(result) == 2
    assert result[0].get('_id') is not None
    assert result[1].get('_id') is not None


def test_update(data_layer):
    resource = 'instruments'
    id_ = '3'
    updates = {'type': 'Stringed keyboard instrument'}
    original = {}
    result = data_layer.update(resource, id_, updates, original)
    assert result.get('_rev') is not None
    assert result.get('_old_rev') is not None
    assert result.get('_rev') != result.get('_old_rev')


def test_replace(data_layer):
    resource = 'instruments'
    id_ = '3'
    document = {
        'name': 'Rhodes electric piano',
        'type': 'Electromagnetic keyboard instument',
    }
    original = {}
    result = data_layer.replace(resource, id_, document, original)
    assert result.get('_rev') is not None
    assert result.get('_old_rev') is not None
    assert result.get('_rev') != result.get('_old_rev')


def test_remove(data_layer):
    resource = 'instruments'
    lookup = {'_key': '3'}
    result = data_layer.remove(resource, lookup)
    assert result == 1


def test_is_empty(data_layer):
    resource = 'instruments'
    result = data_layer.is_empty(resource)
    assert result == False

    resource = 'albums'
    result = data_layer.is_empty(resource)
    assert result == True


def test_arango_result():
    result = ArangoResult(['a', 'b', 'c'])
    assert len(result) == 3
    assert result.count() == 3
