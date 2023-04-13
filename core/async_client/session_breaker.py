import logging
from threading import Thread
from time import sleep
from typing import Set

import redis

from settings import REDIS_SESSION_BLACK_LIST

STOP_SESSION_VALUE = 'STOP'


class SessionBreakerThread(Thread):

    def __init__(self, redis_client: redis.Redis):
        Thread.__init__(self, daemon=True)
        self.logger = logging.getLogger(f'[accelerator.session.breaker]')
        self.redis_client = redis_client
        self.black_list = set()

    def run(self) -> None:
        self.logger.info('Start daemon')
        while True:
            self.black_list = self._check_redis_session_black_list()
            sleep(1)

    def _check_redis_session_black_list(self) -> Set:
        session_black_list_entry = self.redis_client.hgetall(REDIS_SESSION_BLACK_LIST)
        session_black_list = set()

        for (key, value) in session_black_list_entry.items():
            session = key.decode()
            status = value.decode()
            if status == STOP_SESSION_VALUE:
                session_black_list.add(session)

        return session_black_list
