# pip uninstall httpx
# pip install httpx=0.13.3

import base64
import io
import json
import typing

import httpx

from core.api.fetcher import FetcherResponse, Request, FetcherTaskMessageBody
from core.async_client.async_client import AcceleratorAsyncClient, \
    AsyncAcceleratorIncomingMessage
from core.messages.fetcher import FetcherResponseBody
from .config import SERVICE_NAME, PREFETCH_COUNT


# DEFAULT_TIMEOUT = httpx.Timeout(connect_timeout=60.0)
DEFAULT_TIMEOUT = httpx.Timeout(connect_timeout=10, read_timeout=10.0, pool_timeout=10.0)


class AsyncFetcher(AcceleratorAsyncClient):
    def __init__(self, prefetch_count: int = PREFETCH_COUNT, service_name: str = SERVICE_NAME, **kwargs):
        super().__init__(prefetch_count=prefetch_count, service_name=service_name, **kwargs)

    async def process_message(self, incoming_message: AsyncAcceleratorIncomingMessage) -> None:
        incoming_message_body = json.loads(incoming_message.body)
        incoming_request = Request.from_dict(incoming_message_body['request'])
        proxies = self.generate_proxies_settings_for_request(incoming_request.proxies)
        timeout = self.generate_timeout_settings_for_request(incoming_request.timeout)
        raise_exceptions = incoming_request.raise_exceptions
        self.logger.info(f'Receive new request: <Request: method="{incoming_request.method}", '
                         f'url="{incoming_request.url}", proxies={proxies}, timeout={timeout}>')
        try:
            async with httpx.AsyncClient(proxies=proxies, verify=False, timeout=timeout) as client:
                files = incoming_request.files
                if files:
                    files = self.load_files_from_request(files)
                response = await client.request(**self.args_for_request_to_dict(incoming_request), files=files)
                self.validate_allowed_response_http_codes(response=response, request=incoming_request)
        except Exception as e:
            self.logger.exception(e)
            if incoming_request.max_retries - incoming_request.retry_counter >= 1:
                incoming_request.retry_counter += 1
                retry_request = FetcherTaskMessageBody(**incoming_message_body)
                retry_request.request = incoming_request
                self.logger.debug(f'Resend request: <Request: method="{incoming_request.method}", '
                                  f'retry={incoming_request.retry_counter}'
                                  f'url="{incoming_request.url}", proxies={proxies}, timeout={timeout}>')
                await self.send_message(
                    AsyncAcceleratorIncomingMessage(headers=incoming_message.headers, body=retry_request.dict()))
                return
            elif raise_exceptions:
                raise MaxRetriesExceededException(f'Retries: {incoming_request.max_retries}. Last error: "{e}"')
            else:
                response = None
        await self.create_response(request=incoming_request, response=response, incoming_message=incoming_message)

    async def create_response(self,
                              request: Request,
                              response: httpx.Response,
                              incoming_message: AsyncAcceleratorIncomingMessage) -> None:
        status_code = response.status_code if response else None
        self.logger.debug(f'Get response for request: <Response: status_code={status_code}, '
                          f'method="{request.method}", '
                          f'url="{request.url}", proxies={request.proxies}, timeout={request.timeout}>')
        incoming_message_body = json.loads(incoming_message.body)
        fetcher_response = FetcherResponse()
        fetcher_response.request = incoming_message_body
        fetcher_response.response = self.generate_response_body(response)
        await self.send_response(incoming_message, fetcher_response.dict())

    @staticmethod
    def validate_allowed_response_http_codes(response: httpx.Response, request: Request):
        if request.allowed_http_codes:
            assert response.status_code in request.allowed_http_codes, f'HTTP response status code ' \
                                                                       f'[{response.status_code}] not in allowed HTTP codes {request.allowed_http_codes}'
        if request.disallowed_http_codes:
            assert response.status_code not in request.disallowed_http_codes, f'HTTP response status code ' \
                                                                              f'[{response.status_code}] in disallowed HTTP codes {request.allowed_http_codes}'

    @staticmethod
    def generate_proxies_settings_for_request(proxies: typing.Union[str, dict]) -> typing.Union[httpx.Proxy]:
        if proxies:
            if isinstance(proxies, str):
                proxies = httpx.Proxy(proxies)
            elif isinstance(proxies, dict):
                if 'http' in proxies:
                    proxies = httpx.Proxy(proxies['http'])
        return proxies

    @staticmethod
    def generate_timeout_settings_for_request(timeout: typing.Union[float]) -> typing.Union[httpx.Timeout]:
        if timeout:
            return httpx.Timeout(timeout)
        return DEFAULT_TIMEOUT

    @staticmethod
    def load_files_from_request(files: dict) -> dict:
        for file_name in files:
            if len(files[file_name]) >= 2:
                files[file_name] = list(files[file_name])
                files[file_name][1] = io.BytesIO(base64.b64decode(files[file_name][1]))
                files[file_name] = tuple(files[file_name])
            else:
                files[file_name] = io.BytesIO(base64.b64decode(files[file_name]))
        return files

    @staticmethod
    def generate_response_body(response: httpx.Response) -> FetcherResponseBody:
        if response is None:
            return None
        return FetcherResponseBody(
            url=str(response.url),
            content=base64.b64encode(response.content).decode(),
            headers=dict(response.headers),
            cookies=AsyncFetcher.response_cookies_to_dict(response.cookies),
            status_code=response.status_code
        )

    @staticmethod
    def args_for_request_to_dict(request: Request) -> dict:
        return request.dict(
            exclude={
                'proxies', 'verify', 'trust_env', 'timeout', 'files',
                'allowed_http_codes', 'disallowed_http_codes', 'max_retries',
                'retry_counter', 'raise_exceptions'
            }
        )

    @staticmethod
    def response_cookies_to_dict(cookies: httpx.Cookies) -> dict:
        cookies_dict = {}
        for cookie in cookies.jar:
            cookies_dict[cookie.name] = cookie.value
        return cookies_dict


class MaxRetriesExceededException(Exception):
    pass


if __name__ == '__main__':
    fetcher = AsyncFetcher(PREFETCH_COUNT, SERVICE_NAME)
    fetcher.run()
