import base64
import functools
from urllib.parse import urljoin

import typing

from settings import RMQ_FETCHER
from .client import BaseAcceleratorAsyncClient
from core.messages.fetcher import FetcherRequestBody, FetcherTaskMessageBody, \
    FetcherResponseMessageBody, FetcherResponseBody
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.async_client.async_client import AsyncAcceleratorIncomingMessage


class Request(FetcherRequestBody):
    @classmethod
    def from_dict(cls, body: dict):
        return Request(**body)


class Response(FetcherResponseBody):
    def text(self):
        return base64.b64decode(self.content).decode("utf-8", "ignore")

    def urljoin(self, url: str):
        urljoin(self.url, url)


class FetcherResponse(FetcherResponseMessageBody):
    response: Response = None

    @classmethod
    def from_dict(cls, body: dict):
        return FetcherResponse(**body)


class AsyncFetcherClient(BaseAcceleratorAsyncClient):
    SERVICE_NAME = RMQ_FETCHER

    async def send(self, task: FetcherTaskMessageBody, context_message: 'AsyncAcceleratorIncomingMessage',
                   rate_limit_tag: str = '', priority: int = 0):
        await self.context.send_task(context_message, task.json(), self.SERVICE_NAME, rate_limit_tag, priority)

    async def send_response(self, response: FetcherResponse, context_message: 'AsyncAcceleratorIncomingMessage'):
        await self.context.send_response(context_message, response.dict())


def fetcher_response(callback: typing.Callable):
    @functools.wraps(callback)
    async def transform_response_to_fetcher_response(message: 'AsyncAcceleratorIncomingMessage', message_body: dict):
        _fetcher_response = FetcherResponse.from_dict(message_body)
        return await callback(message, _fetcher_response)

    return transform_response_to_fetcher_response
