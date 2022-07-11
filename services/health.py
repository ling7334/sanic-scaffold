try:
    from orjson import __version__ as orjson_version
except ImportError:
    pass
try:
    from aio_pika import __version__ as aio_pika_version
except ImportError:
    pass
try:
    from sentry_sdk.consts import VERSION as sentry_sdk_version
except ImportError:
    pass
try:
    from asyncpg import __version__ as asyncpg_version
    from sqlalchemy import __version__ as sqlalchemy_version
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:
    pass
try:
    from redis import Connection
    from redis import __version__ as redis_version
except ImportError:
    pass
from typing import Union

from pydantic import __version__ as pydantic_version
from sanic import Request
from sanic import __version__ as sanic_version

from version import __version__


async def health(request: Request) -> dict[str, Union[str, list[str]]]:
    modules = []
    if sanic_version:
        modules.append(f"sanic: {sanic_version}")
    if redis_version:
        modules.append(f"redis {redis_version}")
    if pydantic_version:
        modules.append(f"pydantic {pydantic_version}")
    if asyncpg_version:
        modules.append(f"asyncpg {asyncpg_version}")
    if sqlalchemy_version:
        modules.append(f"sqlalchemy {sqlalchemy_version}")
    if orjson_version:
        modules.append(f"orjson {orjson_version}")
    if aio_pika_version:
        modules.append(f"aio_pika {aio_pika_version}")
    if sentry_sdk_version:
        modules.append(f"sentry_sdk {sentry_sdk_version}")

    connections = []
    if hasattr(request.app.ctx, "rabbitmq") and request.app.ctx.rabbitmq and not request.app.ctx.rabbitmq.is_closed:
        connections.append("rabbitmq: connected")
    else:
        connections.append("rabbitmq: disconnected")
    if hasattr(request.app.ctx, "redis") and request.app.ctx.redis:
        connections.append(f"redis pool: {request.app.ctx.redis._created_connections} connected")
        if request.ctx.redis:
            conn: Connection = request.ctx.redis
            connections.append(f'redis connection: {"Ready" if not await conn.can_read() else "In use"}')
    else:
        connections.append("redis: disconnected")
    if hasattr(request.ctx, "db_session") and request.ctx.db_session:
        session: AsyncSession = request.ctx.db_session
        connections.append(f"database: {'connected' if session.is_active else 'disconnected'}")
    else:
        connections.append("database: disconnected")
    return {"status": "ok", "version": __version__, "modules": modules, "connections": connections}
