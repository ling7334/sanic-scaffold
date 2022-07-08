import os

import pytest
from pydantic import BaseSettings, ValidationError
from settings import Settings, json_config_settings_source


class TestSettings:
    def test_default(self) -> None:
        os.environ["APP_DATABASE_MASTER"] = "postgresql+asyncpg://postgres:123456@localhost:5432/postgres"
        conf = Settings()
        assert conf.HOST == "127.0.0.1"
        assert conf.PORT == 5050
        assert conf.DEBUG is True
        assert conf.WORKER == 1
        assert conf.NAME == "scaffold"
        assert conf.DATABASE_MASTER.host == "localhost"
        assert conf.DATABASE_MASTER.port == "5432"
        assert conf.DATABASE_MASTER.user == "postgres"
        assert conf.DATABASE_MASTER.password == "123456"

    def test_empty(self) -> None:
        os.environ.clear()
        with pytest.raises(ValidationError):
            _ = Settings()

    def test_wrong_driver(self) -> None:
        os.environ.clear()
        os.environ["APP_DATABASE_MASTER"] = "wrong_driver"
        with pytest.raises(ValidationError):
            _ = Settings()

    def test_wrong_type(self) -> None:
        os.environ.clear()
        os.environ["APP_DATABASE_MASTER"] = "postgresql+asyncpg://postgres:123456@localhost:5432/postgres"
        os.environ["APP_DEBUG"] = "wrong_type"
        with pytest.raises(ValidationError):
            _ = Settings()


class TestConfigFile:
    class A(BaseSettings):
        class Config:
            env_file_encoding = "utf-8"

    a: A = A()

    def test_default(self) -> None:
        res = json_config_settings_source("tests/test.json", self.a)
        assert res["name"] == "test_config_file"

    def test_not_exitst(self) -> None:
        res = json_config_settings_source("tests/test_not_exist.json", self.a)
        assert res == {}
