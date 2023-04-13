import typing

from .response import ResponseMessageBody, ResponseBody
from .task import TaskMessageBody, TaskRequestBody


class EngineDDLTaskMessageBody(TaskMessageBody):
    request: 'EngineDDLRequestBody' = None


class EngineDDLSelfTaskMessageBody(TaskMessageBody):
    request: 'EngineDDLRequestBody' = None


class EngineDDLResponseMessageBody(ResponseMessageBody):
    request: EngineDDLTaskMessageBody = None
    response: 'EngineDDLResponseBody' = None


class EngineDDLRequestBody(TaskRequestBody):

    ddl: dict
    project_id: typing.Optional[str] = None
    result_recipient: typing.Optional[str] = None
    service_mode: typing.Optional[str] = ''
    url: typing.Optional[str] = ''
    method: typing.Optional[str] = ''
    referrer: typing.Optional[str] = None
    proxies: typing.Optional[typing.Dict[str, str]] = {}
    data: typing.Optional[typing.Dict[str, str]] = None
    cookies: typing.Optional[typing.Dict[str, str]] = {}
    header: typing.Optional[typing.Dict[str, str]] = {}
    task_meta: typing.Optional[typing.Dict[str, str]] = {}
    timeout: typing.Optional[float] = 30
    timeouts: typing.Optional[typing.Dict[str, float]] = None
    verify: typing.Optional[bool] = False
    status_code_allowed: typing.Optional[typing.List[int]] = None
    status_code_disallowed: typing.Optional[typing.List[int]] = None
    document: typing.Optional[str] = None
    follow_document_links: typing.Optional[bool] = False

    def __init__(self, **kwargs):
        super(EngineDDLRequestBody, self).__init__(**kwargs)


class EngineDDLResponseBody(ResponseBody):
    url: typing.Optional[str]
    task_reference: typing.Optional[str]
    referrer: typing.Optional[str]
    status_code: typing.Optional[int]
    headers: typing.Optional[dict]
    cookies: typing.Optional[dict]
    content: typing.Optional[str]


EngineDDLResponseMessageBody.update_forward_refs()
EngineDDLSelfTaskMessageBody.update_forward_refs()
EngineDDLTaskMessageBody.update_forward_refs()
