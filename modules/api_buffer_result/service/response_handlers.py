import json
from abc import ABC, abstractmethod
from typing import Dict

from core.messages.response import ResponseMessageFields
from ..constans import ModuleName, RedisResponseKey


class ResponseHandler(ABC):
    URL_KEY = 'url'

    def __init__(self, module_prefix: str):
        self.module_prefix = module_prefix

    @abstractmethod
    def prepare_response_for_redis(self, message_body) -> Dict:
        pass

    def _get_redis_key_with_prefix(self, redis_key: str, module_prefix: str = None) -> str:
        if not module_prefix:
            module_prefix = self.module_prefix
        return f'{module_prefix}-{redis_key}'


class ContentResponseHandler(ResponseHandler):
    def prepare_response_for_redis(self, message_body: Dict) -> Dict:
        request_url = message_body[ResponseMessageFields.REQUEST][ResponseMessageFields.REQUEST][self.URL_KEY]
        redis_buffer_key = self._get_redis_key_with_prefix(request_url)
        redis_buffer_value = message_body[ResponseMessageFields.RESPONSE]

        return {
            RedisResponseKey.NAME: redis_buffer_key,
            RedisResponseKey.VALUE: json.dumps(redis_buffer_value),
        }


class FetcherResponseHandler(ResponseHandler, ABC):
    CONTENT_KEY = 'content'

    def __init__(self):
        super().__init__(module_prefix=ModuleName.FETCHER)

    def prepare_response_for_redis(self, message_body: Dict) -> Dict:
        request_url = message_body[ResponseMessageFields.REQUEST][ResponseMessageFields.REQUEST][self.URL_KEY]
        redis_buffer_key = self._get_redis_key_with_prefix(request_url)
        redis_buffer_value = message_body[ResponseMessageFields.RESPONSE][self.CONTENT_KEY]

        return {
            RedisResponseKey.NAME: redis_buffer_key,
            RedisResponseKey.VALUE: redis_buffer_value,
        }


class WebdriverFetcherResponseHandler(ResponseHandler):
    CONTENT_KEY = 'content'
    SCREEN_SHOT_KEY = 'screen_shot'

    def __init__(self):
        super().__init__(module_prefix=ModuleName.WEBDRIVER_FETCHER)

    def prepare_response_for_redis(self, message_body: Dict) -> Dict:
        request_url = message_body[ResponseMessageFields.REQUEST][ResponseMessageFields.REQUEST]['args'][self.URL_KEY]
        message_response = message_body[ResponseMessageFields.RESPONSE]

        if self._has_image(message_response):
            redis_buffer_key = self._get_redis_key_with_prefix(request_url, ModuleName.WEBDRIVER_FETCHER_IMAGE)
            redis_buffer_value = message_response[self.SCREEN_SHOT_KEY]
        else:
            redis_buffer_key = self._get_redis_key_with_prefix(request_url)
            redis_buffer_value = message_response[self.CONTENT_KEY]

        return {
            RedisResponseKey.NAME: redis_buffer_key,
            RedisResponseKey.VALUE: redis_buffer_value,
        }

    def _has_image(self, message_response) -> bool:
        if message_response.get(self.SCREEN_SHOT_KEY):
            return True
        else:
            return False


class CaptchaResolverResponseHandler(ResponseHandler):
    GOOGLE_TOKEN = 'google_token'

    def __init__(self):
        super().__init__(module_prefix=ModuleName.CAPTCHA_RESOLVER)

    def prepare_response_for_redis(self, message_body: Dict) -> Dict:
        request_url = message_body[ResponseMessageFields.REQUEST][ResponseMessageFields.REQUEST][self.GOOGLE_TOKEN]
        redis_buffer_key = self._get_redis_key_with_prefix(request_url)
        redis_buffer_value = message_body[ResponseMessageFields.RESPONSE]

        return {
            RedisResponseKey.NAME: redis_buffer_key,
            RedisResponseKey.VALUE: redis_buffer_value,
        }


class LinkExtractorResponseHandler(ContentResponseHandler):
    URL_KEY = 'init_url'

    def __init__(self):
        super().__init__(module_prefix=ModuleName.LINK_EXTRACTOR)


class FacebookExtractorResponseHandler(ContentResponseHandler):
    URL_KEY = 'url'

    def __init__(self):
        super().__init__(module_prefix=ModuleName.FACEBOOK_EXTRACTOR)
