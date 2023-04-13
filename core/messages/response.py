import typing

from pydantic import BaseModel

from .task import TaskMessageBody


class ResponseMessageFields:
    REQUEST = 'request'
    RESPONSE = 'response'


class ResponseMessageBody(BaseModel):
    request: TaskMessageBody = None
    response: 'ResponseBody' = None

    def __init__(self, request: TaskMessageBody = None, response: 'ResponseBody' = None, **data: typing.Any):
        data['request'] = request
        data['response'] = response
        super().__init__(**data)


class ResponseBody(BaseModel):
    pass
