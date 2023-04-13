import typing

from .response import ResponseMessageBody, ResponseBody
from .task import TaskMessageBody, TaskRequestBody

PrimitiveData = typing.Optional[typing.Union[str, int, float, bool]]

AsyncRequestData = typing.Union[dict, str]

QueryParamTypes = typing.Union[
    typing.Mapping[str, PrimitiveData],
    typing.List[typing.Tuple[str, PrimitiveData]],
    str,
]

HeaderTypes = typing.Union[
    typing.Dict[str, str],
    typing.List[typing.Tuple[str, str]],
]

CookieTypes = typing.Dict[str, str]

AuthTypes = typing.Tuple[typing.Union[str, bytes], str]
# CertTypes = typing.Union[str, typing.Tuple[str, str], typing.Tuple[str, str, str]]
# VerifyTypes = typing.Union[str, bool, ssl.SSLContext]

VerifyTypes = typing.Union[str, bool]

TimeoutTypes = typing.Union[float, typing.Tuple[float, float, float]]

RequestFiles = typing.Dict[
    str,
    typing.Union[
        # file (str in base64)
        typing.AnyStr,
        # (filename, file (str in base64))
        typing.Tuple[
            typing.Optional[str], typing.AnyStr,
        ],
        # (filename, file (str in base64), content_type)
        typing.Tuple[
            typing.Optional[str],
            typing.AnyStr,
            typing.Optional[str],
        ],
    ],
]


class FetcherTaskMessageBody(TaskMessageBody):
    request: 'FetcherRequestBody' = None


class FetcherResponseMessageBody(ResponseMessageBody):
    request: FetcherTaskMessageBody = None
    response: 'FetcherResponseBody' = None


class FetcherRequestBody(TaskRequestBody):
    method: str
    url: str
    data: AsyncRequestData = None
    files: RequestFiles = None
    # json: typing.Any = None
    params: QueryParamTypes = None
    headers: HeaderTypes = None
    cookies: CookieTypes = None
    proxies: typing.Union[typing.Dict, str] = None
    # stream: bool = False
    auth: AuthTypes = None
    allow_redirects: bool = True
    # cert: CertTypes = None
    # verify: VerifyTypes = None
    timeout: TimeoutTypes = None

    allowed_http_codes: typing.List[int] = None
    disallowed_http_codes: typing.List[int] = None

    max_retries: int = 0
    retry_counter: int = 0
    # trust_env: bool = None

    raise_exceptions: bool = True

    def __init__(
            self,
            method: str,
            url: str,
            data: AsyncRequestData = None,
            # files: RequestFiles = None,
            # json: typing.Any = None,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            proxies: typing.Union[typing.Dict, str] = None,
            # stream: bool = False,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            # cert: CertTypes = None,
            # verify: VerifyTypes = None,
            timeout: TimeoutTypes = None,
            allowed_http_codes: typing.List[int] = None,
            disallowed_http_codes: typing.List[int] = None,
            max_retries: int = 0,
            retry_counter: int = 0,
            # trust_env: bool = None,
            **kwargs: typing.Any
    ):
        kwargs['method'] = method
        kwargs['url'] = url
        kwargs['data'] = data
        # kwargs['json'] = json
        kwargs['params'] = params
        kwargs['headers'] = headers
        kwargs['cookies'] = cookies
        kwargs['proxies'] = proxies
        kwargs['auth'] = auth
        kwargs['allow_redirects'] = allow_redirects
        # kwargs['verify'] = verify
        kwargs['timeout'] = timeout
        kwargs['allowed_http_codes'] = allowed_http_codes
        kwargs['disallowed_http_codes'] = disallowed_http_codes
        kwargs['max_retries'] = max_retries
        kwargs['retry_counter'] = retry_counter
        # kwargs['trust_env'] = trust_env

        super().__init__(**kwargs)


class FetcherResponseBody(ResponseBody):
    url: str
    content: str
    headers: HeaderTypes
    cookies: CookieTypes
    status_code: int


FetcherResponseMessageBody.update_forward_refs()
FetcherTaskMessageBody.update_forward_refs()
