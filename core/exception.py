class SessionBlockException(Exception):
    pass


class ResourceOffline(Exception):
    def __init__(self, error_message: str = ''):
        self._error_message: str = error_message

    def __repr__(self):
        return self._error_message

    def __str__(self):
        return self._error_message
