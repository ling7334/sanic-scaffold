try:
    from aio_pika.abc import (
        AbstractChannel,
        AbstractConnection,
        AbstractIncomingMessage,
        ConsumerTag,
    )
except ImportError:
    pass
else:
    from abc import ABC, abstractmethod
    from dataclasses import MISSING, dataclass, fields
    from typing import Sequence

    from settings import Settings

    @dataclass
    class ConsumerSetting:
        channel: int
        queue_name: str
        exchange_name: str
        routing_key: str
        no_ack: bool = True  # default auto ack

    class AbstractConsumer(ABC):
        """
        MQ Consumer
        """

        name: str
        settings: ConsumerSetting
        channel: AbstractChannel

        def __init__(self, conf: Settings):
            """
            `AbstractConsumer` get rabbitmq config from settings

            config keys are like `RABBITMQ_{consumer name}_{config name}`

            required config keys are `RABBITMQ_{consumer name}_CHANNEL`, `RABBITMQ_{consumer name}_QUEUE_NAME`,
            `RABBITMQ_{consumer name}_EXCHANGE_NAME` and `RABBITMQ_{consumer name}_ROUTING_KEY`
            """
            for slot in fields(self.settings):
                key = f"RABBITMQ_{self.name.upper()}_{slot.name.upper()}"
                if hasattr(conf, key):
                    setattr(self.settings, slot.name, getattr(conf, key))
                elif slot.default is MISSING:
                    raise KeyError(f"{key} is not defined in settings")

        async def close(self) -> None:
            return await self.channel.close()

        @abstractmethod
        async def on_message(self, message: AbstractIncomingMessage) -> None:
            """
            `on_message` handler the received message
            """
            raise NotImplementedError

        async def register(self, connection: AbstractConnection) -> ConsumerTag:
            """
            `register` register the consumer with the connection and return the consumer tag
            """
            async with connection:
                self.channel = await connection.channel(self.settings.channel)

                queue = await self.channel.declare_queue(self.settings.queue_name, durable=True)

                if self.settings.exchange_name:
                    await queue.bind(self.settings.exchange_name, routing_key=self.settings.routing_key)
                return await queue.consume(self.on_message, no_ack=self.settings.no_ack)

    __consumers__: Sequence[type[AbstractConsumer]] = []
