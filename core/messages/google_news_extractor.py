import typing

from .response import ResponseMessageBody, ResponseBody
from .task import TaskMessageBody, TaskRequestBody


class GoogleNewsExtractorTaskMessageBody(TaskMessageBody):
    request: 'GoogleNewsExtractorRequestBody' = None


class GoogleNewsExtractorResponseMessageBody(ResponseMessageBody):
    request: GoogleNewsExtractorTaskMessageBody = None
    response: 'GoogleNewsExtractorResponseBody' = None


class GoogleNewsExtractorRequestBody(TaskRequestBody):
    keyword_string: str
    maximum_number_of_pages: int
    proxies: typing.Union[str, None]

    def __init__(
            self,
            keyword_string: str,
            maximum_number_of_pages: int = 5,
            proxies: typing.Union[str, None] = None,
            **kwargs: typing.Any
    ):
        kwargs['keyword_string'] = keyword_string
        kwargs['maximum_number_of_pages'] = maximum_number_of_pages
        kwargs['proxies'] = proxies
        super().__init__(**kwargs)


class GoogleNewsExtractorResponseBody(ResponseBody):
    keyword_string: str
    news_dict: dict


GoogleNewsExtractorResponseMessageBody.update_forward_refs()
GoogleNewsExtractorTaskMessageBody.update_forward_refs()
