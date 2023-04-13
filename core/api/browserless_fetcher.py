import base64
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from settings import RMQ_BROWSERLESS_FETCHER
from core.messages.browserless_fetcher import BrowserlessRequestBody
from core.messages.browserless_fetcher import BrowserlessResponseBody
from core.messages.browserless_fetcher import BrowserlessResponseMessageBody
from core.messages.browserless_fetcher import BrowserlessTaskMessageBody
from .client import BaseAcceleratorAsyncClient

if TYPE_CHECKING:
    from core.async_client.async_client import AsyncAcceleratorIncomingMessage


class Request(BrowserlessRequestBody):
    @classmethod
    def from_dict(cls, body: dict):
        return Request(**body)


class Response(BrowserlessResponseBody):
    def text(self):
        return base64.b64decode(self.content).decode("utf-8", "ignore")

    def urljoin(self, url: str):
        urljoin(self.url, url)


class BrowserlessTask(BrowserlessTaskMessageBody):
    request: Request = None

    @classmethod
    def from_dict(cls, body: dict):
        return BrowserlessRequestBody(**body)


class BrowserlessResponse(BrowserlessResponseMessageBody):
    response: Response = None

    @classmethod
    def from_dict(cls, body: dict):
        return BrowserlessResponse(**body)


class AsyncBrowserlessClient(BaseAcceleratorAsyncClient):
    SERVICE_NAME = RMQ_BROWSERLESS_FETCHER

    async def send(self, task: BrowserlessTaskMessageBody, context_message: 'AsyncAcceleratorIncomingMessage',
                   rate_limit_tag: str = '', priority: int = 0):
        await self.context.send_task(context_message, task.json(), self.SERVICE_NAME, rate_limit_tag, priority)

    async def send_response(self, response: BrowserlessResponse, context_message: 'AsyncAcceleratorIncomingMessage'):
        await self.context.send_response(context_message, response.dict())
