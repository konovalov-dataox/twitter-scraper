import typing

from .response import ResponseMessageBody, ResponseBody
from .task import TaskMessageBody, TaskRequestBody


class MediaDownloaderTaskMessageBody(TaskMessageBody):
    request: 'MediaDownloaderRequestBody' = None


class MediaDownloaderResponseMessageBody(ResponseMessageBody):
    request: MediaDownloaderTaskMessageBody = None
    response: 'MediaDownloaderResponseBody' = None


class MediaDownloaderRequestBody(TaskRequestBody):
    root_dir: str
    file_name: typing.Optional[str] = None
    video_url: typing.Optional[str] = None
    unix_time: typing.Optional[str] = None
    gamer_id: typing.Optional[str] = None
    video_id: typing.Optional[str] = None
    transcript: typing.Optional[str] = ''
    chat_info: typing.Optional[str] = None
    video_meta: typing.Optional[str] = None
    proxy: typing.Optional[str] = None
    s3_upload: bool = True
    tasks: typing.Optional[typing.List] = None

    def __init__(
            self,
            root_dir: str,
            file_name: typing.Optional[str] = None,
            video_url: typing.Optional[str] = None,
            unix_time: typing.Optional[str] = None,
            gamer_id: typing.Optional[str] = None,
            video_id: typing.Optional[str] = None,
            transcript: typing.Optional[str] = '',
            chat_info: typing.Optional[str] = None,
            video_meta: typing.Optional[str] = None,
            proxy: typing.Optional[str] = None,
            s3_upload: bool = True,
            tasks: typing.Optional[typing.List] = None,
            **kwargs: typing.Any
    ):
        kwargs['root_dir'] = root_dir
        kwargs['file_name'] = file_name
        kwargs['video_url'] = video_url
        kwargs['unix_time'] = unix_time
        kwargs['gamer_id'] = gamer_id
        kwargs['video_id'] = video_id
        kwargs['transcript'] = transcript
        kwargs['video_meta'] = video_meta
        kwargs['chat_info'] = chat_info
        kwargs['proxy'] = proxy
        kwargs['s3_upload'] = s3_upload
        kwargs['tasks'] = tasks

        super().__init__(**kwargs)


class MediaDownloaderResponseBody(ResponseBody):
    video_url: str
    status_code: int


MediaDownloaderResponseMessageBody.update_forward_refs()
MediaDownloaderTaskMessageBody.update_forward_refs()
