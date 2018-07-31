====================================
eve-arango – Eve ArangoDB data layer
====================================

.. image:: https://travis-ci.org/tangram/eve-arango.svg?branch=master
    :target: https://travis-ci.org/tangram/eve-arango

Provides a data layer for ArangoDB to be used with Eve REST API framework.

Features
========

- Supports CRUD operations for using ArangoDB as a document store
- Supports the same operations on edge documents for managing relations

Not supported (yet):

- Proper graph queries
- Sorting
- Versioning
- Projection
- Aggregation
- Etc.

Installation
============

.. code-block:: bash

    $ pip install -e git://github.com/tangram/eve-arango.git#egg=eve-arango

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

    # If a database with name as set by ARANGO_DB_NAME doesn't exist,
    # it will be created when the data layer is initialized.
    ARANGO_DB_NAME = 'database_name'
    ARANGO_HOST = 'localhost'
    ARANGO_PORT = 8529

    # If DOMAIN keys do not exist as collection names,
    # they will be created when the data layer is initialized.
    # There's no need to add '_id', '_key' or '_rev' fields,
    # they are added to the schema automatically.
    DOMAIN = {
        'people': {
            'schema': {
                'name': {
                    'type': 'string'
                }
            }
        }
        # ...
    }

Contributing
============

Contributions are welcome. Open an issue and send a pull request.

License
=======

`MIT License <LICENSE.txt>`_.
