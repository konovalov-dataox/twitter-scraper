import json
import typing
from pydantic import BaseModel

from .headers import Headers

if typing.TYPE_CHECKING:
    from aio_pika import IncomingMessage
    from core.messages.error import ErrorMessageBody


class Message(BaseModel):
    headers: Headers
    body: typing.Union[typing.Dict, str, 'ErrorMessageBody']
    priority: int = 0
    _original_message: 'IncomingMessage' = None

    def __init__(self, headers: Headers, body: typing.Union[typing.Dict, str, 'ErrorMessageBody'],
                 priority: int = 0, **data: typing.Any):
        data['headers'] = headers
        data['body'] = body
        data['priority'] = priority
        super().__init__(**data)

    def get_body_as_json(self) -> str:
        return self.body.encode() if isinstance(self.body, str) else json.dumps(self.body).encode()

    def get_body_as_dict(self) -> dict:
        return json.loads(self.body) if isinstance(self.body, str) else self.body

    def __repr__(self):
        return (
            f'<Message: '
            f'to="{self.headers.message_to}"", '
            f'from="{self.headers.message_from}"", '
            f'type="{self.headers.message_type}", '
            f'priority={self.priority}, '
            f'session_id="{self.headers.message_session_id}", '
            f'rate_limit_tag="{self.headers.message_rate_limit_tag}"'
            f'>'
        )
