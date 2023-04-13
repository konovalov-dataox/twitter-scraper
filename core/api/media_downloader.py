import base64
import typing
import functools
from typing import TYPE_CHECKING

from settings import RMQ_MEDIA_DOWNLOADER
from core.messages.media_downloader import MediaDownloaderRequestBody
from core.messages.media_downloader import MediaDownloaderResponseBody
from core.messages.media_downloader import MediaDownloaderResponseMessageBody
from core.messages.media_downloader import MediaDownloaderTaskMessageBody
from .client import BaseAcceleratorAsyncClient

if TYPE_CHECKING:
    from core.async_client.async_client import AsyncAcceleratorIncomingMessage


class Request(MediaDownloaderRequestBody):
    @classmethod
    def from_dict(cls, body: dict):
        return Request(**body)


class Response(MediaDownloaderResponseBody):
    def video_meta(self):
        return base64.b64decode(self.video_meta).decode("utf-8", "ignore")

    def chat_info(self):
        return base64.b64decode(self.chat_info).decode("utf-8", "ignore")


class MediaDownloaderResponse(MediaDownloaderResponseMessageBody):
    response: Response = None

    @classmethod
    def from_dict(cls, body: dict):
        return MediaDownloaderResponse(**body)


class AsyncMediaDownloaderClient(BaseAcceleratorAsyncClient):
    SERVICE_NAME = RMQ_MEDIA_DOWNLOADER

    async def send(self, task: MediaDownloaderTaskMessageBody,
                   context_message: 'AsyncAcceleratorIncomingMessage',
                   rate_limit_tag: str = '', priority: int = 0):
        await self.context.send_task(
            context_message, task.json(),
            self.SERVICE_NAME, rate_limit_tag, priority)

    async def send_response(self, response: MediaDownloaderResponse,
                            context_message: 'AsyncAcceleratorIncomingMessage'):
        await self.context.send_response(context_message, response.dict())


def media_downloader_response(callback: typing.Callable):
    @functools.wraps(callback)
    async def transform_response_to_media_downloader_response(
            message: 'AsyncAcceleratorIncomingMessage', message_body: dict):
        _media_downloader_response = \
            MediaDownloaderResponse.from_dict(message_body)
        return await callback(message, _media_downloader_response)

    return transform_response_to_media_downloader_response
