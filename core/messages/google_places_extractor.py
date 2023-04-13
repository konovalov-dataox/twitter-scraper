import typing

from .response import ResponseMessageBody, ResponseBody
from .task import TaskMessageBody, TaskRequestBody


class GooglePlacesExtractorTaskMessageBody(TaskMessageBody):
    request: 'GooglePlacesExtractorRequestBody' = None


class GooglePlacesExtractorResponseMessageBody(ResponseMessageBody):
    request: GooglePlacesExtractorTaskMessageBody = None
    response: 'GooglePlacesExtractorResponseBody' = None


class GooglePlacesExtractorRequestBody(TaskRequestBody):
    keyword_string: str
    extract_reviews: bool
    expected_title: typing.Union[str, None]
    proxies: typing.Union[str, None]

    def __init__(
            self,
            keyword_string: str,
            extract_reviews: bool = True,
            expected_title: typing.Union[str, None] = None,
            proxies: typing.Union[str, None] = None,
            **kwargs: typing.Any
    ):
        kwargs['keyword_string'] = keyword_string
        kwargs['extract_reviews'] = extract_reviews
        kwargs['expected_title'] = expected_title
        kwargs['proxies'] = proxies
        super().__init__(**kwargs)


class GooglePlacesExtractorResponseBody(ResponseBody):
    keyword_string: str
    result_dict: dict


GooglePlacesExtractorResponseMessageBody.update_forward_refs()
GooglePlacesExtractorTaskMessageBody.update_forward_refs()
