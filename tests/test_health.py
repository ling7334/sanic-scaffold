import json
import pytest
import os
from sanic import Sanic
from sanic_testing.testing import SanicASGITestClient


@pytest.fixture
def app() -> Sanic:
    os.environ["APP_DATABASE_MASTER"] = "postgresql+asyncpg://postgres:123456@localhost:5432/postgres"
    # IN test case, OAS cannot fetech server_info
    os.environ["SANIC_OAS"] = "False"
    from server import app as sanic_app

    return sanic_app


class TestHealth:
    @pytest.mark.asyncio
    async def test_basic_response(self, app: Sanic) -> None:
        client: SanicASGITestClient = app.asgi_client
        request, response = await client.get("/")

        assert request.method.lower() == "get"
        assert response.status == 200
        resp = json.loads(response.body)
        assert resp["status"] == "ok"
