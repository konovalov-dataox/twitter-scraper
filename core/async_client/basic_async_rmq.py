from typing import Callable

import aio_pika

from settings import DELIVERY_MODE

QUEUE_ARGUMENTS = {'x-queue-type': 'classic', 'x-max-priority': 5}


class BasicAsyncRMQ:
    def __init__(self):
        self.connection = None
        self._channel = None
        self._exchange = None
        self._queue = None

    async def __call__(self, loop, connection_string: str,
                       exchange_name: str,
                       service_name: str,
                       prefetch_count: int = 5,
                       queue_arguments: dict = None) -> 'BasicAsyncRMQ':

        if queue_arguments is None:
            queue_arguments = QUEUE_ARGUMENTS

        if not connection_string:
            return self

        self.connection = await aio_pika.connect_robust(connection_string, loop=loop)
        self._channel = await self.connection.channel()
        self._exchange = await self._channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)

        self._queue = await self._channel.declare_queue(
            service_name, durable=True, arguments=queue_arguments)

        await self._channel.set_qos(prefetch_count=prefetch_count)
        await self._queue.bind(self._exchange, service_name)

        return self

    async def listen(self, callback: Callable) -> aio_pika.connection:
        await self._queue.consume(callback)
        return self.connection

    async def publish(self, queue_name: str,
                      msg: bytes, headers: dict = None,
                      priority: int = None) -> None:

        message = aio_pika.Message(
            delivery_mode=DELIVERY_MODE,
            body=msg,
            headers=headers,
            priority=priority
        )
        await self._exchange.publish(message, routing_key=queue_name)
