import typing

from pydantic import BaseModel

from settings import RMQ_ERROR_MANAGER
from .headers import Headers
from .message import Message
from .types import MessageType


class ErrorMessageBody(BaseModel):
    error: str
    message_headers: typing.Dict[str, str]
    message_body: str

    def __init__(self, error: str, message_headers: typing.Dict[str, str],
                 message_body: str, **data: typing.Any):
        data['error'] = error
        data['message_headers'] = message_headers
        data['message_body'] = message_body
        super().__init__(**data)

    @classmethod
    def from_headers_and_body(cls, headers: typing.Dict[str, str],
                              message_body: str, error: str) -> 'ErrorMessageBody':
        return ErrorMessageBody(error=error, message_headers=headers,
                                message_body=message_body)

    @classmethod
    def from_message(cls, message: Message, error: str) -> 'ErrorMessageBody':
        return ErrorMessageBody(error=error, message_headers=message.headers,
                                message_body=message.get_body_as_json())


def generate_error_response_headers(sender: str, session_id: str) -> Headers:
    return Headers(
        message_to=RMQ_ERROR_MANAGER,
        message_from=sender,
        message_session_id=session_id,
        message_type=MessageType.ERROR
    )
