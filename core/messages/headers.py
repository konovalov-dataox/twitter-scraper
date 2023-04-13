from core.utils import props
from .types import MessageType


class HeadersField:
    TO = 'to'
    FROM = 'from'
    SESSION_ID = 'session_id'
    TYPE = 'type'
    RATE_LIMIT_TAG = 'rate_limit_tag'


class Headers(dict):
    def __init__(self, message_to: str, message_from: str, message_type: str,
                 message_session_id: str, message_rate_limit_tag: str = ''):
        super().__init__({})
        self[HeadersField.TO] = message_to
        self[HeadersField.FROM] = message_from
        self[HeadersField.SESSION_ID] = message_session_id
        self[HeadersField.TYPE] = message_type
        self[HeadersField.RATE_LIMIT_TAG] = message_rate_limit_tag

    @property
    def message_to(self):
        return self[HeadersField.TO]

    @message_to.setter
    def message_to(self, value):
        self[HeadersField.TO] = value

    @property
    def message_from(self):
        return self[HeadersField.FROM]

    @message_from.setter
    def message_from(self, value):
        self[HeadersField.FROM] = value

    @property
    def message_session_id(self):
        return self[HeadersField.SESSION_ID]

    @message_session_id.setter
    def message_session_id(self, value):
        self[HeadersField.SESSION_ID] = value

    @property
    def message_type(self):
        return self[HeadersField.TYPE]

    @message_type.setter
    def message_type(self, value):
        self[HeadersField.TYPE] = value

    @property
    def message_rate_limit_tag(self):
        return self[HeadersField.RATE_LIMIT_TAG]

    @message_rate_limit_tag.setter
    def message_rate_limit_tag(self, value):
        self[HeadersField.RATE_LIMIT_TAG] = value

    @staticmethod
    def validate_message_headers(headers: 'Headers', recipient: str) -> None:
        assert headers.message_to == recipient, \
            f'Message was wrong directed, intended for "{headers.message_to}", received by "{recipient}"'
        assert headers.message_from, 'Empty "from" header filed'
        assert headers.message_session_id, 'Empty "session_id" header filed'
        assert headers.message_type in props(MessageType), \
            f'Message type not allowed, received "{headers.message_type}", allowed "{props(MessageType)}"'

    @classmethod
    def from_dict(cls, params):
        return Headers(params[HeadersField.TO], params[HeadersField.FROM], params[HeadersField.TYPE],
                       params[HeadersField.SESSION_ID], params[HeadersField.RATE_LIMIT_TAG])
