import typing
import redis


class RedisDriver(object):

    def __init__(self, host: str, port: int, password: str, database: int):
        super(RedisDriver, self).__init__()
        self._session = redis.Redis(host=host,
                                    port=port,
                                    password=password,
                                    db=database)

    def __del__(self):
        self._session.close()

    def set_expire_time(self, name: str, time: int) -> None:
        self._session.expire(name, time)

    def is_exists(self, name: str) -> bool:
        return bool(self._session.exists(name))

    def set(self, name: typing.Union[str, int, float, bytes],
            value: typing.Union[str, int, float, bytes],
            expire: typing.Optional[int] = None) -> None:
        self._session.set(name, value)

        if expire is not None:
            self.set_expire_time(name, expire)

    def get(self, name: typing.Union[str, int, float, bytes],
            expire: typing.Optional[int] = None) -> str:

        if expire is not None:
            self.set_expire_time(name, expire)

        value = self._session.get(name)
        return value.decode() if value is not None else ''

    def hash_multi_set(
            self, hash_table: typing.Union[str, int, float, bytes],
            value: typing.Dict[typing.Union[str, int, float, bytes],
                               typing.Union[str, int, float, bytes]],
            expire: typing.Optional[int] = None) -> None:
        self._session.hmset(hash_table, value)

        if expire is not None:
            self.set_expire_time(hash_table, expire)

    def hash_get_all(
            self, hash_table: typing.Union[str, int, float, bytes],
            expire: typing.Optional[int] = None) -> dict:

        if expire is not None:
            self.set_expire_time(hash_table, expire)

        data = self._session.hgetall(hash_table)
        return {key.decode(): value.decode() for key, value in data.items()}

    def hash_get(self, hash_table: str,
                 key: typing.Union[str, int, float, bytes],
                 expire: typing.Optional[int] = None) -> str:

        if expire is not None:
            self.set_expire_time(hash_table, expire)

        value = self._session.hget(hash_table, key)
        return value.decode() if value is not None else ''

    def hash_set(self, hash_table: str,
                 key: typing.Union[str, int, float, bytes],
                 value: typing.Union[str, int, float, bytes],
                 expire: typing.Optional[int] = None) -> None:

        self._session.hset(hash_table, key, value)

        if expire is not None:
            self.set_expire_time(hash_table, expire)

    def set_add(self, set_name: str,
                set_value: typing.Union[str, int, float, bytes],
                expire: typing.Optional[int] = None) -> None:

        self._session.sadd(set_name, set_value)

        if expire is not None:
            self.set_expire_time(set_name, expire)

    def set_remove(self, set_name: str,
                   set_value: typing.Union[str, int, float, bytes],
                   expire: typing.Optional[int] = None):

        self._session.srem(set_name, set_value)

        if expire is not None:
            self.set_expire_time(set_name, expire)

    def set_pop(self, set_name: str,
                expire: typing.Optional[int] = None) -> None:
        self._session.spop(set_name)

        if expire is not None:
            self.set_expire_time(set_name, expire)

    def set_members(self, set_name: str,
                    expire: typing.Optional[int] = None) -> set:

        if expire is not None:
            self.set_expire_time(set_name, expire)

        data = self._session.smembers(set_name)
        return {value.decode() for value in data}

    def set_is_member(self, set_name: str,
                      set_value: typing.Union[str, int, float, bytes],
                      expire: typing.Optional[int] = None) -> bool:

        if expire is not None:
            self.set_expire_time(set_name, expire)

        return self._session.sismember(set_name, set_value)
