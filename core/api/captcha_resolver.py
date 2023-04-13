from typing import TYPE_CHECKING

from core.messages.captcha_resolver import CaptchaResolverRequestBody
from core.messages.captcha_resolver import CaptchaResolverResponseBody
from core.messages.captcha_resolver import CaptchaResolverResponseMessageBody
from core.messages.captcha_resolver import CaptchaResolverTaskMessageBody
from settings import RMQ_CAPTCHA_RESOLVER
from .client import BaseAcceleratorAsyncClient

if TYPE_CHECKING:
    from core.async_client.async_client import AsyncAcceleratorIncomingMessage


class Request(CaptchaResolverRequestBody):
    @classmethod
    def from_dict(cls, body: dict):
        return Request(**body)


class Response(CaptchaResolverResponseBody):
    def get_resolving_string(self):
        return self.result_string


class CaptchaResolverTask(CaptchaResolverTaskMessageBody):
    request: Request = None

    @classmethod
    def from_dict(cls, body: dict):
        return CaptchaResolverRequestBody(**body)


class CaptchaResolverResponse(CaptchaResolverResponseMessageBody):
    response: Response = None

    @classmethod
    def from_dict(cls, body: dict):
        return CaptchaResolverResponse(**body)


class AsyncCaptchaResolverClient(BaseAcceleratorAsyncClient):

    async def send(self, task: CaptchaResolverTaskMessageBody,
                   context_message: 'AsyncAcceleratorIncomingMessage',
                   rate_limit_tag: str = '', priority: int = 0):

        await self.context.send_task(context_message, task.json(),
                                     RMQ_CAPTCHA_RESOLVER,
                                     rate_limit_tag, priority)

    async def send_response(
            self, response: CaptchaResolverResponse,
            context_message: 'AsyncAcceleratorIncomingMessage'):

        await self.context.send_response(context_message, response.dict())
