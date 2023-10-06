from httpx import AsyncClient

base_url = "http://localhost:8080"


class TestApiBaseHandle:

    async def test_root_handler(self, test_app):
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('root_handler'))

        assert response.status_code == 200
        assert response.json() == {'version': 'v1'}

    async def test_ping(self, test_app):
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('ping'))

        assert response.status_code == 200


class TestApiFilesHandle:

    async def test_save_file_without_auth(self, test_app, get_test_session):
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.post(test_app.url_path_for('save_file'))
        assert response.status_code == 401

    async def test_get_files_without_auth(self, test_app, get_test_session):
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('get_files'))
        assert response.status_code == 401

    async def test_get_files_with_auth(self, test_app, get_test_session, headers_with_token, file):
        async with AsyncClient(
                app=test_app,
                base_url=base_url,
                headers=headers_with_token
        ) as ac:
            response = await ac.get(test_app.url_path_for('get_files'))
            response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == 1
        assert response_json[0].get('name') == file.name

    async def test_download_file_without_auth(self, test_app, get_test_session):
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('download_file'))
        assert response.status_code == 401

    async def test_usage_memory_without_auth(self, test_app, get_test_session):
        async with AsyncClient(app=test_app, base_url=base_url) as ac:
            response = await ac.get(test_app.url_path_for('usage_memory'))
        assert response.status_code == 401

    async def test_usage_memory_with_auth(
            self,
            test_app,
            get_test_session,
            headers_with_token,
            file
    ):
        async with AsyncClient(
                app=test_app,
                base_url=base_url,
                headers=headers_with_token
        ) as ac:
            response = await ac.get(test_app.url_path_for('usage_memory'))
            response_json = response.json()
        assert response.status_code == 200
        assert response_json == 100
