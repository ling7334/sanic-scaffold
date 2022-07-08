from typing import Any, Callable, Optional

try:
    from orjson import dumps, loads
except ImportError:
    from json import dumps as json_dumps
    from json import loads

    def dumps(__obj: Any, default: Optional[Callable[[Any], Any]] = None, option: Optional[int] = None) -> bytes:
        return json_dumps(__obj, default=default).encode("utf-8")


from sanic import Sanic

import controllers
from settings import Settings
from setup import setup
from utils.autodiscovery import autodiscover


def init_app(conf: Optional[Settings] = None) -> Sanic:
    conf = conf or Settings()
    app = Sanic(name=conf.NAME, dumps=dumps, loads=loads)

    autodiscover(
        app,
        controllers,
        recursive=True,
    )
    setup(app, conf)

    return app


def main(app: Optional[Sanic] = None, conf: Optional[Settings] = None) -> None:
    conf = conf or Settings()
    app = app or init_app(conf)
    app.run(
        host=conf.HOST,
        port=conf.PORT,
        dev=conf.DEBUG,
        workers=conf.WORKER,
    )


app = init_app()

if __name__ == "__main__":
    from os import environ
    from pprint import pprint

    pprint(environ.__dict__, indent=2)
    main()
