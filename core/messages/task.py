import typing

from pydantic import BaseModel

CallbackType = typing.Optional[str]
MetaType = typing.Optional[typing.Union[str, dict, list]]


class TaskMessageFields:
    ARGS = 'request'
    CALLBACK = 'callback'
    META = 'meta'


class TaskMessageBody(BaseModel):
    request: 'TaskRequestBody' = None
    callback: CallbackType = None
    meta: MetaType = None
    on_error_callback: CallbackType = None

    def __init__(self, request: 'TaskRequestBody' = None, callback: CallbackType = None, meta: MetaType = None,
                 on_error_callback: CallbackType = None, **data: typing.Any):
        data['request'] = request
        data['callback'] = callback
        data['meta'] = meta
        data['on_error_callback'] = on_error_callback
        super().__init__(**data)


class TaskRequestBody(BaseModel):
    pass


TaskMessageBody.update_forward_refs()
