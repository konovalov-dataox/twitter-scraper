import re
import typing

from core.exception import ResourceOffline
from core.async_client.async_client import AcceleratorAsyncClient, \
    AsyncAcceleratorIncomingMessage, Message, Headers, json

from .config import SERVICE_NAME, PREFETCH_COUNT, LOG_DB_LOCATOR
from .config import RMQ_EXCHANGE, TABLE_PREFIX
from .database import LogDatabase
from .exceptions import NoDbConnect
from .exceptions import EmptyTableName
from .exceptions import TableCreate, TablePartitionCreate, TableNotFound
from .exceptions import InsertLogMessage


class AsyncErrorManager(AcceleratorAsyncClient):

    def __init__(self, prefetch_count: int = PREFETCH_COUNT,
                 service_name: str = SERVICE_NAME, **kwargs):
        super(AsyncErrorManager, self).__init__(
            prefetch_count=prefetch_count,
            service_name=service_name, **kwargs)

        self._log_db: typing.Optional[LogDatabase] = None

    @property
    def _db_ready(self):
        try:
            if not self._log_db:
                self._log_db = LogDatabase(LOG_DB_LOCATOR,
                                           TABLE_PREFIX,
                                           RMQ_EXCHANGE)

        except Exception as e:
            self.logger.exception(e)
            return False

        else:
            return True if self._log_db else False

    @staticmethod
    def _get_table_name(producer: str) -> str:
        pattern = re.compile(f'{RMQ_EXCHANGE}\.')
        table_name = re.sub(pattern, '', producer)
        table_name = re.sub(r'\.', '_', table_name)
        return f'{TABLE_PREFIX}{table_name}'.lower()

    @staticmethod
    def _extract_meta(body: typing.Optional[dict]) -> str:
        try:
            meta = body.get('meta')

            if type(meta) is not dict:
                raise TypeError()

            meta = json.dumps(body.get('meta'))

        except TypeError:
            return '{}'

        except Exception:
            return '{}'

        else:
            return meta

    @staticmethod
    def _extract_on_error_callback(body: typing.Optional[dict]) -> str:
        try:
            callback_name = body.get('request').get('on_error_callback')

        except Exception:
            return ''

        else:
            return callback_name

    async def process_message(
            self, incoming_message: AsyncAcceleratorIncomingMessage) -> None:
        rmq_producer = incoming_message.headers.get('from')
        table_name = AsyncErrorManager._get_table_name(rmq_producer)
        message = incoming_message.get_body_as_dict()
        message_body = json.loads(message.get('message_body', ''))

        try:
            if not self._db_ready:
                raise NoDbConnect(LOG_DB_LOCATOR)

            data: dict = {
                'session_id': incoming_message.headers.get('session_id'),
                'message_headers':
                    json.dumps(message.get('message_headers', '{}')),
                'message_body': message.get('message_body', '{}'),
                'meta': AsyncErrorManager._extract_meta(message_body),
                'error': message.get('error', '')
            }

            if not self._log_db.add_log_record(table_name, **data):
                raise InsertLogMessage()

            on_error_callback = \
                AsyncErrorManager._extract_on_error_callback(message_body)

            if on_error_callback:
                headers = message['message_headers']
                outgoing_message = Message(Headers(
                    message_to=headers['from'],
                    message_from=headers['to'],
                    message_type=headers['type'],
                    message_session_id=headers['session_id'],
                    message_rate_limit_tag=headers['rate_limit_tag']),
                    message_body)
                await self.send_message(outgoing_message)

        except NoDbConnect as error:
            raise ResourceOffline(repr(error))

        except EmptyTableName as error:
            raise ResourceOffline(repr(error))

        except TableCreate as error:
            raise ResourceOffline(repr(error))

        except TablePartitionCreate as error:
            raise ResourceOffline(repr(error))

        except TableNotFound as error:
            raise ResourceOffline(repr(error))

        except InsertLogMessage as error:
            raise ResourceOffline(repr(error))
