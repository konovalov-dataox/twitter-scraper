from typing import TYPE_CHECKING

from core.messages.google_places_extractor import GooglePlacesExtractorRequestBody
from core.messages.google_places_extractor import GooglePlacesExtractorResponseBody
from core.messages.google_places_extractor import GooglePlacesExtractorResponseMessageBody
from core.messages.google_places_extractor import GooglePlacesExtractorTaskMessageBody
from settings import RMQ_GOOGLE_PLACES_EXTRACTOR
from .client import BaseAcceleratorAsyncClient

if TYPE_CHECKING:
    from core.async_client.async_client import AsyncAcceleratorIncomingMessage


class Request(GooglePlacesExtractorRequestBody):
    @classmethod
    def from_dict(cls, body: dict):
        return Request(**body)


class Response(GooglePlacesExtractorResponseBody):
    def get_keyword_string(self):
        return self.keyword_string

    def get_result_dict(self):
        return self.result_dict


class GooglePlacesExtractorTask(GooglePlacesExtractorResponseMessageBody):
    request: Request = None

    @classmethod
    def from_dict(cls, body: dict):
        return GooglePlacesExtractorRequestBody(**body)


class GooglePlacesExtractorResponse(GooglePlacesExtractorResponseMessageBody):
    response: Response = None

    @classmethod
    def from_dict(cls, body: dict):
        return GooglePlacesExtractorResponse(**body)


class AsyncGooglePlacesExtractorClient(BaseAcceleratorAsyncClient):

    async def send(self, task: GooglePlacesExtractorTaskMessageBody,
                   context_message: 'AsyncAcceleratorIncomingMessage',
                   rate_limit_tag: str = '', priority: int = 0):
        await self.context.send_task(context_message, task.json(),
                                     RMQ_GOOGLE_PLACES_EXTRACTOR,
                                     rate_limit_tag, priority)

    async def send_response(
            self, response: GooglePlacesExtractorResponse,
            context_message: 'AsyncAcceleratorIncomingMessage'):
        await self.context.send_response(context_message, response.dict())
