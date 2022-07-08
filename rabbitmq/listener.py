try:
    import aio_pika
    from aio_pika.abc import AbstractRobustConnection
except ImportError:
    pass
else:
    import asyncio
    from asyncio import AbstractEventLoop
    from typing import Optional

    from settings import Settings

    from .consumers import __consumers__

    async def setup_rabbitmq(
        conf: Settings, loop: Optional[AbstractEventLoop] = None
    ) -> Optional[AbstractRobustConnection]:
        if not (
            conf.RABBITMQ_HOST
            and conf.RABBITMQ_PORT
            and conf.RABBITMQ_USERNAME
            and conf.RABBITMQ_PASSWORD
            and conf.RABBITMQ_VHOST
        ):
            return None
        loop = loop or asyncio.get_event_loop_policy().get_event_loop()

        conn = await aio_pika.connect_robust(
            host=conf.RABBITMQ_HOST,
            port=conf.RABBITMQ_PORT,
            login=conf.RABBITMQ_USERNAME,
            password=conf.RABBITMQ_PASSWORD,
            virtualhost=conf.RABBITMQ_VHOST,
            loop=loop,
        )
        consumer_names = set()
        for consumer in __consumers__:
            if consumer.name in consumer_names:
                raise ValueError(f"Duplicate consumer: {consumer.name}")
            instance = consumer(conf)
            consumer_names.add(instance.name)
            await instance.register(conn)

        return conn
