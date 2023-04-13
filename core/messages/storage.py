import json
import time
import typing

from .task import TaskMessageBody

DEFAULT = 'DEFAULT'


class StorageField:
    SAVING_TIMESTAMP = 'saving_timestamp'
    SAVE_AS_HISTORY = 'save_as_history'
    PROJECT_ID = 'project_id'
    SESSION_ID = 'session_id'
    ID = 'id'
    OBJECT = 'object'


class StorageTaskMessageBody(TaskMessageBody):
    request: 'StorageRequestBody' = None
    pass


class StorageRequestBody(dict):
    def __init__(
            self,
            project_id: str,
            item_id: typing.Union[str, int],
            item: typing.Union[typing.Dict, typing.List],
            json_item: str = None,
            session_id: str = DEFAULT,
            save_as_history: bool = False,
            saving_timestamp: str = None,
            **kwargs
    ):
        self[StorageField.SAVING_TIMESTAMP] = saving_timestamp if saving_timestamp else int(time.time())
        self[StorageField.SAVE_AS_HISTORY] = save_as_history
        self[StorageField.PROJECT_ID] = project_id
        self[StorageField.SESSION_ID] = session_id
        self[StorageField.ID] = item_id
        if item:
            self[StorageField.OBJECT] = json.dumps(item)
        elif json_item:
            self[StorageField.OBJECT] = item
        super().__init__(**kwargs)

    @property
    def project_id(self):
        return self[StorageField.PROJECT_ID]

    @project_id.setter
    def project_id(self, value: str):
        self[StorageField.PROJECT_ID] = value

    @property
    def item_id(self):
        return self[StorageField.ID]

    @item_id.setter
    def item_id(self, value: typing.Union[str, int]):
        self[StorageField.ID] = value

    @property
    def item(self):
        return self[StorageField.OBJECT]

    @item.setter
    def item(self, value: typing.Union[typing.Dict, typing.List]):
        self[StorageField.OBJECT] = json.dumps(value)

    @property
    def json_item(self):
        return self[StorageField.OBJECT]

    @json_item.setter
    def json_item(self, value: str):
        self[StorageField.OBJECT] = value

    @property
    def session_id(self):
        return self[StorageField.SESSION_ID]

    @session_id.setter
    def session_id(self, value: str):
        self[StorageField.SESSION_ID] = value

    @property
    def save_as_history(self):
        return self[StorageField.SAVE_AS_HISTORY]

    @save_as_history.setter
    def save_as_history(self, value: bool):
        self[StorageField.SAVE_AS_HISTORY] = value

    @property
    def saving_timestamp(self):
        return self[StorageField.SAVING_TIMESTAMP]

    @saving_timestamp.setter
    def saving_timestamp(self, value: int):
        self[StorageField.SAVING_TIMESTAMP] = value


StorageTaskMessageBody.update_forward_refs()
