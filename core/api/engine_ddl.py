import typing
import base64
import functools
from urllib.parse import urljoin

from settings import RMQ_ENGINE_DDL
from .client import BaseAcceleratorAsyncClient
from core.async_client.async_client import AsyncAcceleratorIncomingMessage
from core.messages.engine_ddl import EngineDDLRequestBody
from core.messages.engine_ddl import EngineDDLTaskMessageBody
from core.messages.engine_ddl import EngineDDLResponseMessageBody
from core.messages.engine_ddl import EngineDDLResponseBody


class Request(EngineDDLRequestBody):
    @classmethod
    def from_dict(cls, body: dict):
        return Request(**body)


class Response(EngineDDLResponseBody):
    def text(self):
        return base64.b64decode(self.content).decode("utf-8", "ignore")

    def urljoin(self, url: str):
        urljoin(self.url, url)


class EngineDDLResponse(EngineDDLResponseMessageBody):
    response: Response = None

    @classmethod
    def from_dict(cls, body: dict):
        return EngineDDLResponse(**body)


class AsyncProcessorDDLClient(BaseAcceleratorAsyncClient):
    SERVICE_NAME = RMQ_ENGINE_DDL

    async def send(self, task: EngineDDLTaskMessageBody,
                   context_message: 'AsyncAcceleratorIncomingMessage',
                   rate_limit_tag: str = '', priority: int = 0):
        await self.context.send_task(context_message, task.json(),
                                     self.SERVICE_NAME, rate_limit_tag,
                                     priority)

    async def send_response(
            self, response: EngineDDLResponse,
            context_message: 'AsyncAcceleratorIncomingMessage'):

        await self.context.send_response(context_message, response.dict())


def processor_ddl_response(callback: typing.Callable):
    @functools.wraps(callback)
    async def transform_response_to_processor_ddl_response(
            message: 'AsyncAcceleratorIncomingMessage', message_body: dict):

        _fetcher_response = EngineDDLResponse.from_dict(message_body)
        return await callback(message, _fetcher_response)

    return transform_response_to_processor_ddl_response
