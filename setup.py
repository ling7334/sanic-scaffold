from sanic import Request, Sanic
from sanic.response import BaseHTTPResponse, HTTPResponse
from sanic.log import logger
from sanic.errorpages import HTMLRenderer, RENDERERS_BY_CONFIG

from settings import Settings
from version import __version__


def setup_sentry(conf: Settings) -> None:
    """
    Setup sentry if dsn is provided and sentry-sdk is installed
    """
    if not conf.SENTRY_DSN:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.sanic import SanicIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    except ImportError:
        return
    # sample rate set to 10% if in production to imporve performance
    trace_sampler = 0.1 if conf.ENV_NAME.lower() == "production" else 1.0
    sentry_sdk.init(
        dsn=conf.SENTRY_DSN,
        debug=conf.DEBUG,
        environment=conf.ENV_NAME,
        integrations=[
            SanicIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
        ],
        release=__version__,
        traces_sample_rate=trace_sampler,
    )


def setup_redis(app: Sanic, conf: Settings) -> None:
    """
    Setup redis if DSN is provided and redis is installed
    """
    if not conf.REDIS_DSN:
        return None
    try:
        from redis import asyncio as aioredis
    except ImportError:
        return None

    async def before_server_start(app: Sanic) -> None:
        # setup redis if redis_dsn is provided
        app.ctx.redis = aioredis.ConnectionPool(aioredis.Connection, max_connections=10).from_url(
            conf.REDIS_DSN.__str__()
        )

    async def after_server_stop(app: Sanic) -> None:
        # close the redis connection pool
        conn: aioredis.Connection = app.ctx.redis
        if conn:
            await conn.disconnect()

    async def get_redis_connection(request: Request) -> None:
        # get a connection from the pool
        pool: aioredis.ConnectionPool = request.app.ctx.redis
        request.ctx.redis = await pool.get_connection(request.id)

    async def release_redis_connection(request: Request, _: BaseHTTPResponse) -> None:
        # release the connection to the pool
        conn: aioredis.Connection = request.ctx.redis
        pool: aioredis.ConnectionPool = app.ctx.redis
        if conn:
            await pool.release(conn)

    app.register_listener(before_server_start, "before_server_start")
    app.register_listener(after_server_stop, "after_server_stop")
    app.register_middleware(get_redis_connection, "request")
    app.register_middleware(release_redis_connection, "response")


def setup_database(app: Sanic, conf: Settings) -> None:
    """
    Setup database if DSN is provided and sqlalchemy is installed
    """
    if not conf.DATABASE_MASTER:
        return None

    try:
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
    except ImportError:
        return None

    async def before_server_start(app: Sanic) -> None:
        # setup database if database is provided
        engine = create_async_engine(conf.DATABASE_MASTER)
        app.ctx.db_engine = engine

    async def after_server_stop(app: Sanic) -> None:
        # dispose the database engine
        engine: AsyncEngine = app.ctx.db_engine
        if engine:
            await engine.dispose()

    async def get_session(request: Request) -> None:
        # get a session from the engine
        engine: AsyncEngine = app.ctx.db_engine
        request.ctx.db_session = sessionmaker(engine, AsyncSession, expire_on_commit=False)()

    async def close_session(request: Request, _: BaseHTTPResponse) -> None:
        # auto commit and close the session
        session: AsyncSession = request.ctx.db_session
        if session:
            try:
                await session.commit()
            except Exception as e:
                logger.exception(e)
                await session.rollback()
            finally:
                await session.close()

    app.register_listener(before_server_start, "before_server_start")
    app.register_listener(after_server_stop, "after_server_stop")
    app.register_middleware(get_session, "request")
    app.register_middleware(close_session, "response")


def global_exception_handler(request: Request, exception: Exception) -> HTTPResponse:
    """
    Global exception handler
    """
    format = request.app.config.FALLBACK_ERROR_FORMAT
    if format in RENDERERS_BY_CONFIG:
        render = RENDERERS_BY_CONFIG[format]
        return render(request, exception, request.app.debug).render()
    else:
        return HTMLRenderer(request, exception, request.app.debug).render()


def setup(app: Sanic, conf: Settings) -> None:
    """
    Setup all extensions
    """

    setup_sentry(conf)

    setup_redis(app, conf)

    setup_database(app, conf)

    app.error_handler.add(Exception, global_exception_handler)

    try:
        from aio_pika.abc import AbstractConnection

        from rabbitmq.listener import setup_rabbitmq
    except ImportError:
        pass
    else:

        async def before_server_start(app: Sanic) -> None:
            # setup rabbitmq if host, port and etc. are provided
            app.ctx.rabbitmq = await setup_rabbitmq(conf, loop=app.loop)

        async def after_server_stop(app: Sanic) -> None:
            # close the rabbitmq connection
            conn: AbstractConnection | None = app.ctx.rabbitmq
            if conn:
                await conn.close()

        app.register_listener(before_server_start, "before_server_start")
        app.register_listener(after_server_stop, "after_server_stop")
