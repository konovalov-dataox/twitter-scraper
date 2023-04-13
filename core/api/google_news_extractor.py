from typing import TYPE_CHECKING

from core.messages.google_news_extractor import GoogleNewsExtractorRequestBody
from core.messages.google_news_extractor import GoogleNewsExtractorResponseBody
from core.messages.google_news_extractor import GoogleNewsExtractorResponseMessageBody
from core.messages.google_news_extractor import GoogleNewsExtractorTaskMessageBody
from settings import RMQ_GOOGLE_NEWS_EXTRACTOR
from .client import BaseAcceleratorAsyncClient

if TYPE_CHECKING:
    from core.async_client.async_client import AsyncAcceleratorIncomingMessage


class Request(GoogleNewsExtractorRequestBody):
    @classmethod
    def from_dict(cls, body: dict):
        return Request(**body)


class Response(GoogleNewsExtractorResponseBody):
    def get_news_dict(self):
        return self.news_dict

    def get_keyword_string(self):
        return self.keyword_string


class GoogleNewsExtractorTask(GoogleNewsExtractorTaskMessageBody):
    request: Request = None

    @classmethod
    def from_dict(cls, body: dict):
        return GoogleNewsExtractorRequestBody(**body)


class GoogleNewsExtractorResponse(GoogleNewsExtractorResponseMessageBody):
    response: Response = None

    @classmethod
    def from_dict(cls, body: dict):
        return GoogleNewsExtractorResponse(**body)


class AsyncGoogleNewsExtractorClient(BaseAcceleratorAsyncClient):

    async def send(self, task: GoogleNewsExtractorTaskMessageBody,
                   context_message: 'AsyncAcceleratorIncomingMessage',
                   rate_limit_tag: str = '', priority: int = 0):
        await self.context.send_task(context_message, task.json(),
                                     RMQ_GOOGLE_NEWS_EXTRACTOR,
                                     rate_limit_tag, priority)

    async def send_response(
            self, response: GoogleNewsExtractorResponse,
            context_message: 'AsyncAcceleratorIncomingMessage'):
        await self.context.send_response(context_message, response.dict())
