# from tests import test_blueprint
from sanic import Sanic

from utils.autodiscovery import autodiscover


class TestAutodiscover:
    def test_default(self) -> None:
        app = Sanic(name="test_autodiscover")
        autodiscover(app, "tests.test_blueprint", recursive=True)
        assert "test" in app.blueprints
        assert len(app.blueprints["test"].routes) == 1
        assert app.blueprints["test"].routes[0].name == "test_autodiscover.test.test"
