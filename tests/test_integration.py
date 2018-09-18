import pytest

from eve import Eve
from eve_arango.arangodb import ArangoDB


@pytest.fixture(scope='module')
def test_client():
    app = Eve(settings='test_settings.py', data=ArangoDB)

    test_client = app.test_client()
    context = app.app_context()

    context.push()
    yield test_client
    context.pop()


def test_get_resource(test_client):
    result = test_client.get('/musicians')
    assert result.status_code == 200


def test_get_resource_where(test_client):
    result = test_client.get('/musicians?where=name=="Miles Davis"ORname=="Bill Evans"')
    assert result.status_code == 200
    assert result.json['_items'][0]['name'] == 'Miles Davis'
    assert result.json['_items'][1]['name'] == 'Bill Evans'


def test_get_resource_sort(test_client):
    result = test_client.get('/musicians?sort=name,-born')
    assert result.status_code == 200
    assert result.json['_items'][0]['name'] == 'Bill Evans'


def test_pagination(test_client):
    result = test_client.get('/musicians?page=2&max_results=1')
    assert result.status_code == 200
    assert result.json['_meta']['total'] > 1


def test_get_item(test_client):
    result = test_client.get('/musicians/1')
    assert result.status_code == 200


def test_post(test_client):
    data = {'name': 'Thelonious Monk'}
    result = test_client.post('/musicians', data=data)
    assert result.status_code == 201


def test_patch(test_client):
    result = test_client.get('/musicians/1')
    headers = {'If-Match': result.json['_etag']}
    data = {'name': 'Miles Dewey Davis III'}
    result = test_client.patch('/musicians/1', data=data, headers=headers)
    assert result.status_code == 200


def test_put(test_client):
    result = test_client.get('/musicians/1')
    headers = {'If-Match': result.json['_etag']}
    data = {
        'name': 'Miles Davis',
        'born': '1926-05-26'
    }
    result = test_client.put('/musicians/1', data=data, headers=headers)
    assert result.status_code == 200


def test_delete(test_client):
    result = test_client.get('/musicians/1')
    headers = {'If-Match': result.json['_etag']}
    result = test_client.delete('/musicians/1', headers=headers)
    assert result.status_code == 204
