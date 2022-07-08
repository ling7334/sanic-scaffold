try:
    from orjson import loads
except ImportError:
    from json import loads

from functools import partial
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseSettings, HttpUrl, PostgresDsn, RedisDsn
from pydantic.env_settings import SettingsSourceCallable


def json_config_settings_source(file: str, settings: BaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a JSON file
    at the project's root.
    """
    file = file or "config.json"
    if not Path(file).exists():
        return {}
    encoding = settings.__config__.env_file_encoding
    return loads(Path(file).read_text(encoding))


class Settings(BaseSettings):
    NAME: str = "scaffold"
    HOST: str = "127.0.0.1"
    PORT: int = 5050
    DEBUG: bool = True
    WORKER: int = 1
    ENV_NAME: str = "production"

    RABBITMQ_HOST: Optional[str]
    RABBITMQ_PORT: Optional[int]
    RABBITMQ_USERNAME: Optional[str]
    RABBITMQ_PASSWORD: Optional[str]
    RABBITMQ_VHOST: Optional[str] = "/"

    DATABASE_MASTER: PostgresDsn
    DATABASE_READER: Optional[PostgresDsn]
    UPDATE_DATABASE: bool = False
    POPULATE_DATABASE: bool = False

    REDIS_DSN: Optional[RedisDsn]

    SENTRY_DSN: Optional[HttpUrl]

    class Config:
        env_prefix = "APP_"
        config_file = "config.json"
        env_file_encoding = "utf-8"
        secrets_dir = "/run/secrets"

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            # add support for json config files
            return (
                init_settings,
                env_settings,
                partial(json_config_settings_source, cls.config_file),
                file_secret_settings,
            )
