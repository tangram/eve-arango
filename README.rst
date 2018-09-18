====================================
eve-arango – Eve ArangoDB data layer
====================================

.. image:: https://badge.fury.io/py/eve-arango.svg
    :target: https://badge.fury.io/py/eve-arango.svg

.. image:: https://travis-ci.org/tangram/eve-arango.svg?branch=master
    :target: https://travis-ci.org/tangram/eve-arango

Provides a data layer for ArangoDB to be used with Eve REST API framework.

Features
========

- CRUD operations for using ArangoDB as a document store
- Supports the same operations on edge documents for managing relations
- Filtering based on AQL syntax
- Pagination and sorting

Not supported (yet):

- Proper graph queries
- Versioning
- Projection
- Aggregation
- Etc.

Installation
============

.. code-block:: bash

    $ pip install eve-arango

Usage
=====

.. code-block:: python

    from eve import Eve
    from eve_arango import ArangoDB

    app = Eve(data=ArangoDB)
    app.run()

The following settings are processed:

.. code-block:: python

    # These are necessary for item lookups to work,
    # the regex is for the characters allowed in ArangoDB keys.
    ID_FIELD = '_key'
    ITEM_LOOKUP_FIELD = ID_FIELD
    ITEM_URL = 'regex("[\w\d\-:.@()+,=;$!*\'%]+")'

    # If a database named ARANGO_DB's value doesn't exist,
    # it will be created when the data layer is initialized.
    ARANGO_DB = 'database_name'
    ARANGO_HOST = 'localhost'
    ARANGO_PORT = 8529

    # If the keys in DOMAIN do not exist as collection names,
    # they will be created when the data layer is initialized.
    # There's no need to add '_id', '_key' or '_rev' fields,
    # they are added to the schema automatically.
    # If you specifiy 'edge_collection': True as below,
    # an edge collection will be created if it does not exist.
    DOMAIN = {
        'people': {
            'schema': {
                'name': {
                    'type': 'string'
                }
            }
        },
        'friends_with': {
            'edge_collection': True
        },
        # ...
    }

Filtering and sorting
=====================

eve-arango uses AQL syntax for filtering via the Eve `where` parameter. Mongo-style queries are not valid. Here are some examples of valid (url decoded) queries and their resulting AQL:

.. code-block::
    # Spaces are optional.
    ?where=foo == "bar"
    # FILTER doc.foo == "bar"

    # Use , as simple separator between FILTER expressions.
    ?where=numIN[1,2,3],present!=null
    # FILTER doc.num IN [1,2,3]
    # FILTER doc.present != null

    # AND, OR, NOT can be used to combine expressions.
    ?where=a=="a"ANDb=="b"ORc=="c"
    # FILTER doc.a == "a" AND doc.b == "b" OR doc.c == "c"

Sorting uses the regular Eve syntax. An example is given below:

.. code-block::
    ?sort=name,-age
    # SORT doc.name, doc.age DESC

Contributing
============

Contributions are welcome. Open an issue and send a pull request.

License
=======

`MIT License <LICENSE.txt>`_.
