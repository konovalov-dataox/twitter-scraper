import typing

from .response import ResponseMessageBody, ResponseBody
from .task import TaskMessageBody, TaskRequestBody

CONTENT_MODE = 'content'
JS_MODE = 'exec_js'
SCREENSHOT_MODE = 'screenshot'


class BrowserlessTaskMessageBody(TaskMessageBody):
    request: 'BrowserlessRequestBody' = None


class BrowserlessResponseMessageBody(ResponseMessageBody):
    request: BrowserlessTaskMessageBody = None
    response: 'BrowserlessResponseBody' = None


class BrowserlessRequestBody(TaskRequestBody):
    url: str
    task_mode: str = CONTENT_MODE
    proxy: str = None
    headers: typing.Dict = None
    cookies: typing.Any = None
    js_code: str = None

    def __init__(
            self,
            url: str,
            proxy: str = None,
            headers: typing.Dict = None,
            cookies: typing.Any = None,
            js_code: str = None,
            task_mode: str = CONTENT_MODE,
            **kwargs: typing.Any
    ):
        kwargs['task_mode'] = task_mode
        kwargs['url'] = url
        kwargs['proxy'] = proxy
        kwargs['headers'] = headers
        kwargs['cookies'] = cookies
        kwargs['js_code'] = js_code
        super().__init__(**kwargs)


class BrowserlessResponseBody(ResponseBody):
    url: str
    content: str
    # headers: HeaderTypes
    # cookies: CookieTypes
    status_code: int


BrowserlessResponseMessageBody.update_forward_refs()
BrowserlessTaskMessageBody.update_forward_refs()
