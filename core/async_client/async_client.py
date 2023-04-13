import asyncio
import json
import logging
import typing
import traceback
from abc import ABC, abstractmethod

import redis
from aio_pika import IncomingMessage

from core.messages.error import generate_error_response_headers, ErrorMessageBody
from core.messages.headers import HeadersField, Headers
from core.messages.message import Message
from core.messages.types import MessageType
from settings import RMQ_URL_CONNECTION_STR, \
    REDIS_HOST, REDIS_PORT, REDIS_PASS, REDIS_DB_CORE, \
    NOT_COMPRESSED_MESSAGE_QUEUES, RMQ_EXCHANGE
from .basic_async_rmq import BasicAsyncRMQ
from .session_breaker import SessionBreakerThread
from ..exception import SessionBlockException, ResourceOffline
from ..message_preference.compression import MessageCompressorHandler


class AsyncAcceleratorIncomingMessage(Message):
    @classmethod
    def from_incoming_message(cls, incoming_message: IncomingMessage):
        return AsyncAcceleratorIncomingMessage(
            Headers.from_dict(AsyncAcceleratorIncomingMessage.incoming_message_headers_to_dict(incoming_message)),
            incoming_message.body,
            incoming_message.priority
        )

    @staticmethod
    def incoming_message_headers_to_dict(message: IncomingMessage) -> typing.Dict[str, str]:
        return {key: message.headers_raw[key].decode() for key in message.headers_raw}


class AcceleratorAsyncClient(ABC):
    def __init__(self, prefetch_count: int, service_name: str,
                 connection_string: str = RMQ_URL_CONNECTION_STR):
        self.logger = logging.getLogger(f'[accelerator.module.{service_name}]')

        self.prefetch_count = prefetch_count
        self.service_name = service_name

        self.logger.info(f'Running Accelerator client: {self}')

        self.loop = asyncio.get_event_loop()
        basic_rmq = BasicAsyncRMQ()
        interface = basic_rmq(self.loop, connection_string,
                              RMQ_EXCHANGE,
                              self.service_name,
                              self.prefetch_count)

        self.connection = self.loop.run_until_complete(interface)
        self.session_breaker = self._create_session_breaker()
        self.message_compressor = MessageCompressorHandler()

    def __repr__(self):
        return f'<AcceleratorAsyncClient({self.service_name}):' \
               f' prefetch_count={self.prefetch_count}>'

    def _create_session_breaker(self) -> SessionBreakerThread:
        redis_client = self.__create_redis_connection()
        session_breaker = SessionBreakerThread(redis_client=redis_client)
        return session_breaker

    def run(self):
        self.session_breaker.start()
        self.declare_queue()
        self.loop.run_forever()
        self.loop.run_until_complete(self.connection.close())
        self.loop.close()

    def declare_queue(self):
        self.loop.run_until_complete(self.connection.listen(
            callback=self.receive_message)
        )

    async def receive_message(self, incoming_message: IncomingMessage) -> None:
        async with incoming_message.process(requeue=True):
            accelerator_incoming_message = None

            try:
                accelerator_incoming_message = \
                    AsyncAcceleratorIncomingMessage.from_incoming_message(
                        incoming_message)

                self.logger.debug(
                    f'Receive message: {accelerator_incoming_message}'
                )

                Headers.validate_message_headers(
                    accelerator_incoming_message.headers, self.service_name)

                await self.start_processing_massage(
                    incoming_message=accelerator_incoming_message)

            except ResourceOffline as error:
                incoming_message.reject(requeue=True)
                self.logger.exception(error)

            except Exception as error:
                self.logger.exception(error)
                error_msg = traceback.format_exc()

                if accelerator_incoming_message:
                    error_message = self._generate_error_message(
                        error_msg, accelerator_incoming_message)

                else:
                    error_message = self._generate_error_message(
                        error_msg, incoming_message)

                await self.send_message(error_message)

    async def send_error_message(self,
                                 error_message_body: typing.Union[dict, str],
                                 session_id: str) -> None:
        error_message_headers = \
            generate_error_response_headers(self.service_name, session_id)

        await self.send_message_raw(
            error_message_body, error_message_headers, 1)

    async def send_message_raw(self, message_body: typing.Union[dict, str],
                               message_headers: typing.Union[Headers, dict],
                               priority: int = 0) -> None:

        self.logger.debug(f'Sending message: <Message: to="{message_headers[HeadersField.TO]}"", '
                          f'type="{message_headers[HeadersField.TYPE]}", priority={priority}, '
                          f'session_id="{message_headers[HeadersField.SESSION_ID]}", '
                          f'rate_limit_tag="{message_headers[HeadersField.RATE_LIMIT_TAG]}">')

        msg = message_body.encode() \
            if isinstance(message_body, str) \
            else json.dumps(message_body).encode()

        await self.connection.publish(
            queue_name=message_headers[HeadersField.TO],
            msg=msg,
            headers=message_headers,
            priority=priority
        )

    async def send_message(self, message: Message):
        self.logger.debug(f'Sending message: {message}')

        if message.headers.get('to') in NOT_COMPRESSED_MESSAGE_QUEUES or \
                message.headers[HeadersField.TYPE] == MessageType.ERROR:
            message_body = message.get_body_as_json()
        else:
            message_body = self.message_compressor.compress_message_body(
                message.get_body_as_json())

        await self.connection.publish(
            queue_name=message.headers['to'],
            msg=message_body,
            headers=message.headers,
            priority=message.priority
        )

    async def send_task(self, context: AsyncAcceleratorIncomingMessage,
                        task_message_body: typing.Union[dict, str], recipient: str,
                        rate_limit_tag: str = '', priority: int = 0):
        task_message_headers = Headers(
            message_to=recipient,
            message_from=self.service_name,
            message_session_id=context.headers[HeadersField.SESSION_ID],
            message_type=MessageType.TASK,
            message_rate_limit_tag=rate_limit_tag
        )
        await self.send_message(Message(task_message_headers, task_message_body, priority))

    async def send_response(self, context: AsyncAcceleratorIncomingMessage,
                            response_message_body: typing.Union[dict, str]):

        response_message_headers = Headers(
            message_to=context.headers[HeadersField.FROM],
            message_from=self.service_name,
            message_session_id=context.headers[HeadersField.SESSION_ID],
            message_type=MessageType.RESPONSE
        )

        await self.send_message(Message(response_message_headers, response_message_body, 1))

    def _generate_error_message(self, error: str,
                                incoming_message: typing.Union[
                                    IncomingMessage,
                                    AsyncAcceleratorIncomingMessage
                                ]) -> Message:
        if isinstance(incoming_message, AsyncAcceleratorIncomingMessage):
            message_body = ErrorMessageBody.from_message(incoming_message, error)
            message_headers = generate_error_response_headers(
                self.service_name, incoming_message.headers.message_session_id
            )
        else:
            message_body = ErrorMessageBody.from_headers_and_body(
                incoming_message.headers_raw,
                incoming_message.body,
                repr(error)
            )
            if HeadersField.SESSION_ID in incoming_message.headers_raw:
                session_id = incoming_message.headers_raw[HeadersField.SESSION_ID]
            else:
                session_id = 'DEFAULT_ERROR_SESSION_ID'

            message_headers = generate_error_response_headers(
                self.service_name, session_id
            )
        return Message(message_headers, message_body, 1)

    async def check_session_for_black_list_entry(self, session_id: str) -> bool:
        black_list = self.session_breaker.black_list
        if session_id in black_list:
            is_session_blocked = True
        else:
            is_session_blocked = False

        return is_session_blocked

    async def start_processing_massage(
            self, incoming_message: AsyncAcceleratorIncomingMessage) -> None:

        session_id = incoming_message.headers.message_session_id
        is_blocked_session = await self.check_session_for_black_list_entry(session_id)
        if is_blocked_session:
            raise SessionBlockException(f'Session [{session_id}] was blocked!')
        else:
            incoming_message = self.message_compressor.decompress_message(incoming_message)
            await self.process_message(incoming_message)

    @abstractmethod
    async def process_message(self, incoming_message: AsyncAcceleratorIncomingMessage) -> None:
        pass

    @staticmethod
    def __create_redis_connection() -> redis.Redis:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASS,
            db=REDIS_DB_CORE)
        return redis_client
