import pytest
from fastapi import HTTPException
from httpx import URL, AsyncClient

from services.history_service import history_crud
from services.request_service import request_crud
from services.url_service import url_crud

base_url = "http://localhost:8080"


class TestApiBaseHandle:

    async def test_root_handler(self, test_app):
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('root_handler'))

        assert response.status_code == 200
        assert response.json() == {'version': 'v1'}

    async def test_ping_db(self, test_app):
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('ping_db'))

        assert response.status_code == 200


class TestBlockedHostMiddleware:

    async def test_call_available(self, test_app):
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('root_handler'))
        assert response.status_code == 200
        assert response.json() == {'version': 'v1'}

    async def test_call_blocked0(self, test_app):
        async with AsyncClient(app=test_app, base_url=URL('http://example.com')) as ac:
            response = await ac.get(test_app.url_path_for('root_handler'))

        assert response.status_code == 400
        assert response.text == 'Invalid host header'

    async def test_call_blocked1(self, test_app):
        async with AsyncClient(app=test_app, base_url=URL('http://testserver.example.com')) as ac:
            response = await ac.get(test_app.url_path_for('root_handler'))
        assert response.status_code == 400
        assert response.text == 'Invalid host header'


class TestApiHistoryHandle:

    async def test_get_status_with_client(self, test_app, history_items, get_test_session):
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('get_status'))
            response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == 1
        assert response_json[0].get('id') == str(history_items.id)
        assert response_json[0].get('url_id') == str(history_items.url_id)
        assert response_json[0].get('method') == history_items.method

    async def test_get_status(self, history_items, get_test_session):
        response = await history_crud.get_multi(
            url_id=None,
            user_id=None,
            domen=None,
            method=None,
            db=get_test_session,
            skip=0,
            limit=100
        )
        assert len(response) == 1
        assert response[0].id == history_items.id
        assert response[0].url_id == history_items.url_id
        assert response[0].method == history_items.method


class TestApiRequestHandle:

    async def test_get_request_with_client_case0(self, test_app, history_items, url_items):
        url_obj, deleted_url_obj = url_items
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('get_request', url_id=url_obj.id))
        assert response.status_code == 307

    async def test_get_request_case0(self, url_items, get_test_session):
        url_obj, deleted_url_obj = url_items
        url = await request_crud.custom_request(
            url_id=url_obj.id,
            user_id=None,
            db=get_test_session,
            method='GET',
            host='http://testserver'
        )
        assert url == url_obj.url

    async def test_get_request_with_client_case1(self, test_app, history_items, url_items):
        url_obj, deleted_url_obj = url_items
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(
                test_app.url_path_for('get_request', url_id=deleted_url_obj.id))
        assert response.status_code == 404

    async def test_get_request_case1(self, url_items, get_test_session):
        url_obj, deleted_url_obj = url_items
        with pytest.raises(HTTPException):
            await request_crud.custom_request(
                url_id=deleted_url_obj.id,
                user_id=None,
                db=get_test_session,
                method='GET',
                host='http://testserver'
            )


class TestApiUrlHandle:

    async def test_read_urls_with_client(self, test_app, history_items):
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('read_urls'))
        assert response.status_code == 200

    async def test_read_urls(self, url_items, get_test_session):
        url_obj, _ = url_items
        response = await url_crud.get_multi(db=get_test_session, skip=0, limit=100)
        assert isinstance(response, list)
        assert len(response) == 1
        assert url_obj.id == response[0].id
        assert url_obj.url == response[0].url

    async def test_read_url_with_client(self, test_app, history_items, url_items):
        url_obj, _ = url_items
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('read_url', id=url_obj.id))
        assert response.status_code == 200

    async def test_read_url(self, url_items, get_test_session):
        url_obj, _ = url_items
        response = await url_crud.get(db=get_test_session, id=url_obj.id)
        assert url_obj.id == response.id
        assert url_obj.url == response.url

    async def test_read_url_is_delete_with_client(self, test_app, history_items, url_items):
        _, deleted_url_obj = url_items
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('read_url', id=deleted_url_obj.id))
        assert response.status_code == 404

    async def test_read_url_is_delete(self, url_items, get_test_session):
        _, deleted_url_obj = url_items
        response = await url_crud.get(db=get_test_session, id=deleted_url_obj.id)
        assert response is None

    async def test_create_url(self, get_test_session, new_test_url_schema):
        response = await url_crud.create(db=get_test_session, obj_in=new_test_url_schema)
        assert response.url == new_test_url_schema.url

    async def test_update_url(self, url_items, get_test_session, new_test_url_schema):
        url_obj, _ = url_items
        response = await url_crud.update(
            db=get_test_session,
            id=url_obj.id,
            obj_in=new_test_url_schema
        )
        assert response.url == new_test_url_schema.url

    async def test_delete_url_with_client(self, test_app, url_items):
        url_obj, _ = url_items
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.delete(test_app.url_path_for('delete_url', id=url_obj.id))
        response_json = response.json()
        assert response.status_code == 410
        assert response_json.get('is_delete') is True
