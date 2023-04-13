from settings import *
from .redis_driver import RedisDriver


class Driver(object):

    def __init__(self):
        super(Driver, self).__init__()
        self._redis_driver: RedisDriver = RedisDriver(host=REDIS_HOST,
                                                      port=REDIS_PORT,
                                                      password=REDIS_PASS,
                                                      database=REDIS_DB_DDL)

    @property
    def redis(self) -> RedisDriver:
        return self._redis_driver
