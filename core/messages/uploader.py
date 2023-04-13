import typing

from .task import TaskMessageBody, TaskRequestBody
from pydantic import BaseModel

CredsType = typing.Dict[str, str]


class UploaderTaskMessageBody(TaskMessageBody):
    request: 'UploaderRequestBody' = None


class ManualFile(BaseModel):
    target_file_path: str = ''
    file_name: str = ''
    content: str = ''


class Credentials(BaseModel):
    type: str = ''
    creds: CredsType = {}


class UploaderRequestBody(TaskRequestBody):
    manual_file: ManualFile = ManualFile()
    buffer_file_path: str
    project_name: str
    credentials: Credentials = Credentials()

    def __init__(
            self,
            manual_file: ManualFile,
            buffer_file_path: str,
            project_name: str,
            credentials: Credentials,
            **kwargs: typing.Any
    ):
        kwargs['manual_file'] = manual_file
        kwargs['buffer_file_path'] = buffer_file_path
        kwargs['project_name'] = project_name
        kwargs['credentials'] = credentials
        super().__init__(**kwargs)


# FetcherResponseMessage.update_forward_refs()
UploaderTaskMessageBody.update_forward_refs()
