import redis

from core.async_client.async_client import AcceleratorAsyncClient, \
    AsyncAcceleratorIncomingMessage
from core.messages.headers import HeadersField
from .config import REDIS_PASS, REDIS_HOST, REDIS_PORT, REDIS_DB, \
    PREFETCH_COUNT, SERVICE_NAME, REDIS_EXPIRATION_MESSAGE_SEC
from .service.response_handler_factory import ResponseHandlerFactory, \
    RedisResponseKey


class AsyncApiBufferResult(AcceleratorAsyncClient):

    def __init__(self, prefetch_count: int = PREFETCH_COUNT,
                 service_name: str = SERVICE_NAME, **kwargs):
        super().__init__(prefetch_count, service_name, **kwargs)
        self.redis_client = self.init_redis_client()
        self.response_handler_factory = ResponseHandlerFactory()

    async def process_message(
            self, incoming_message: AsyncAcceleratorIncomingMessage) -> None:
        module_queue = incoming_message.headers[HeadersField.FROM]
        factory = self.response_handler_factory
        response_handler = \
            factory.get_response_handler_by_module_name(module_queue)

        message_body = incoming_message.get_body_as_dict()
        redis_response = \
            response_handler.prepare_response_for_redis(message_body)

        self.redis_client.set(
            name=redis_response[RedisResponseKey.NAME],
            value=redis_response[RedisResponseKey.VALUE],
            ex=REDIS_EXPIRATION_MESSAGE_SEC
        )

    @staticmethod
    def init_redis_client():
        return redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASS,
            db=REDIS_DB
        )
