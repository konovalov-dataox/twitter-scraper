from typing import TYPE_CHECKING

from .client import BaseAcceleratorAsyncClient
from core.messages.uploader import UploaderRequestBody, UploaderTaskMessageBody
from settings import RMQ_UPLOADER

if TYPE_CHECKING:
    from core.async_client.async_client import AsyncAcceleratorIncomingMessage


class Request(UploaderRequestBody):
    @classmethod
    def from_dict(cls, body: dict):
        return Request(**body)


class AsyncUploaderClient(BaseAcceleratorAsyncClient):
    SERVICE_NAME = RMQ_UPLOADER

    async def send(self, task: UploaderTaskMessageBody, context_message: 'AsyncAcceleratorIncomingMessage',
                   rate_limit_tag: str = '', priority: int = 0):
        await self.context.send_task(context_message, task.dict(), self.SERVICE_NAME, rate_limit_tag, priority)
