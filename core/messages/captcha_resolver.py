import typing

from .response import ResponseMessageBody, ResponseBody
from .task import TaskMessageBody, TaskRequestBody

RE_CAPTCHA = 're_captcha'
FUN_CAPTCHA = 'fun_captcha'
TEXT_CAPTCHA = 'text_captcha'


class CaptchaResolverTaskMessageBody(TaskMessageBody):
    request: 'CaptchaResolverRequestBody' = None


class CaptchaResolverResponseMessageBody(ResponseMessageBody):
    request: CaptchaResolverTaskMessageBody = None
    response: 'CaptchaResolverResponseBody' = None


class CaptchaResolverRequestBody(TaskRequestBody):
    url: str
    captcha_identifier: str
    captcha_type: str = RE_CAPTCHA

    def __init__(
            self,
            url: str,
            captcha_identifier: str,
            captcha_type: str = RE_CAPTCHA,
            **kwargs: typing.Any
    ):
        kwargs['captcha_type'] = captcha_type
        kwargs['captcha_identifier'] = captcha_identifier
        kwargs['url'] = url
        super().__init__(**kwargs)


class CaptchaResolverResponseBody(ResponseBody):
    url: str
    result_string: str


CaptchaResolverResponseMessageBody.update_forward_refs()
CaptchaResolverTaskMessageBody.update_forward_refs()
