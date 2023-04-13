import logging
import datetime as dt
from sqlalchemy import create_engine
from sqlalchemy import text

from ..exceptions import EmptyTableName
from ..exceptions import TableCreate, TablePartitionCreate, TableNotFound


class LogDatabase(object):

    def __init__(self, db_locator, table_prefix, exchange_name):
        super(LogDatabase, self).__init__()
        self.logger = logging.getLogger(f'[accelerator.module.error_manager]')
        self._table_prefix = table_prefix
        self._exchange_name = exchange_name
        self._engine = create_engine(db_locator, echo=False,
                                     pool_size=5, max_overflow=0)
        self._tables: list = []
        self._load_table_names()

    def __del__(self):
        if hasattr(self, '_engine') and self._engine:
            self._engine.dispose()

    def _load_table_names(self):
        with self._engine.connect() as con:
            query = f'select table_name' \
                    f' from information_schema.tables' \
                    f' where table_schema = \'public\'' \
                    f' and table_name like \'{self._table_prefix}%\''

            table_names = con.execute(text(query)).fetchall()
            self._tables = [name for name, in table_names]

    def add_log_record(self, table_name, **kwargs):
        session_id: str = kwargs.get('session_id', '')
        error: str = kwargs.get('error', '')
        meta: str = kwargs.get('meta', '')
        message_headers: str = kwargs.get('message_headers', '')
        message_body: str = kwargs.get('message_body', '')

        if not table_name:
            raise EmptyTableName()

        if not self._create_table(table_name):
            raise TableCreate(table_name)

        if not self._create_table_partition(table_name):
            raise TablePartitionCreate(table_name)

        if table_name not in self._tables:
            raise TableNotFound(table_name)

        try:
            with self._engine.connect() as con:
                statement = text(
                    f'insert into {table_name}'
                    ' (session_id, error, meta, message_headers,'
                    ' message_body, exchange) values'
                    ' (:session_id, :error, :meta,'
                    ' :message_headers, :message_body,'
                    ' :exchange)'
                )
                values: dict = {
                    'session_id': session_id,
                    'error': error,
                    'meta': meta,
                    'message_headers': message_headers,
                    'message_body': message_body,
                    'exchange': self._exchange_name
                }

                con.execute(statement, **values)

        except Exception as e:
            self.logger.exception(e)
            return False

        else:
            return True

    def _create_table(self, table_name: str) -> bool:
        if table_name in self._tables:
            return True

        try:
            with self._engine.connect() as con:
                statement = text(
                    f'create table if not exists {table_name} ('
                    f'id serial,'
                    f' session_id varchar(100) not null,'
                    f' error text,'
                    f' message_headers json,'
                    f' meta json,'
                    f' message_body json,'
                    f' exchange varchar(30) not null,'
                    f' log_date date default current_date not null,'
                    f' log_time time default current_time not null'
                    f') partition by range (log_date)'
                )

                con.execute(statement)

        except Exception as e:
            self.logger.exception(e)
            return False

        else:
            return True

    def _create_table_partition(self, table_name: str) -> bool:
        srv_date = self._server_date()
        month: str = str(srv_date.month).rjust(2, '0')
        partition_name: str = f'{table_name}_{srv_date.year}_{month}'

        if partition_name in self._tables:
            return True

        next_year = srv_date.year if srv_date.month < 12 else srv_date.year + 1
        next_month: str = str(srv_date.month + 1).rjust(2, '0') \
            if srv_date.month < 12 else '01'

        date_to: str = f'{next_year}-{next_month}-01'
        date_from: str = f'{srv_date.year}-{month}-01'

        try:
            with self._engine.connect() as con:
                statement = text(
                    f'create table if not exists {partition_name}'
                    f' partition of {table_name}'
                    f' for values from (\'{date_from}\') to (\'{date_to}\')'
                )
                con.execute(statement)

                statement = text(
                    f'create index on {partition_name}'
                    f' (session_id, log_date, log_time, exchange)'
                )

                con.execute(statement)

        except Exception as e:
            self.logger.exception(e)
            return False

        else:
            self._load_table_names()
            return True

    def _server_date(self) -> dt.date:
        with self._engine.connect() as con:
            result = con.execute(text('select current_date')).fetchall()
            return result[0][0]
