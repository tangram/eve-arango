import os


DEBUG = True

ARANGO_DB = os.getenv('ARANGO_DB', 'test_database_disposable')
ARANGO_HOST = os.getenv('ARANGO_HOST', 'localhost')
ARANGO_PORT = os.getenv('ARANGO_PORT', 8529)

ID_FIELD = '_key'
ITEM_LOOKUP_FIELD = ID_FIELD
ITEM_URL = 'regex("[\w\d\-:.@()+,=;$!*\'%]+")'

RENDERERS = ['eve.render.JSONRenderer']

RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']

DOMAIN = {
    'musicians': {
        'schema': {
            'name': {
                'type': 'string',
            },
            'born': {
                'type': 'string',
            }
        }
    },
    'instruments': {
        'schema': {
            'name': {
                'type': 'string',
            },
            'type': {
                'type': 'string',
            }
        }
    },
    'played': {},
    'albums': {}
}
