try:
    from aio_pika import ExchangeType
    from aio_pika.abc import AbstractMessage, AbstractConnection, TimeoutType
    from aiormq.abc import ConfirmationFrameType
except ImportError:
    pass
else:
    from abc import ABC, abstractmethod
    from typing import Any, Optional

    class BaseMessage(ABC):
        """MQ Message"""

        connection: Optional[AbstractConnection]
        exchange: str
        channel_number: int
        exchange_type: ExchangeType
        publisher_confirms: bool
        on_return_raises: bool
        kwargs: dict[str, Any]

        def __init__(
            self,
            connection: Optional[AbstractConnection],
            exchange: str = "",
            channel_number: int = 0,
            exchange_type: ExchangeType = ExchangeType.TOPIC,  # exchange type default to topic
            publisher_confirms: bool = True,
            on_return_raises: bool = False,
            **kwargs: dict[str, Any]
        ):
            self.connection = connection
            self.exchange = exchange
            self.channel_number = channel_number
            self.exchange_type = exchange_type
            self.publisher_confirms = publisher_confirms
            self.on_return_raises = on_return_raises
            self.kwargs = kwargs

        @property
        @abstractmethod
        def message(self) -> AbstractMessage:
            """
            `message` format the message to be sent

            ```python
            aio_pika.Message(body="Hello {}!".format("world").encode())
            ```
            """
            raise NotImplementedError

        async def send(
            self, routing_key: str = "", *, mandatory: bool = True, immediate: bool = False, timeout: TimeoutType = None
        ) -> Optional[ConfirmationFrameType]:
            if not self.connection:
                raise ValueError("Rabbitmq connection does not exist")
            async with self.connection:
                # Creating a channel
                channel = self.connection.channel(self.channel_number, self.publisher_confirms, self.on_return_raises)
                if self.exchange:
                    exchange = await channel.declare_exchange(self.exchange, type=self.exchange_type, **self.kwargs)

                    return await exchange.publish(
                        message=self.message,
                        routing_key=routing_key,
                        mandatory=mandatory,
                        immediate=immediate,
                        timeout=timeout,
                    )
                else:
                    return await channel.default_exchange.publish(
                        message=self.message,
                        routing_key=routing_key,
                        mandatory=mandatory,
                        immediate=immediate,
                        timeout=timeout,
                    )
