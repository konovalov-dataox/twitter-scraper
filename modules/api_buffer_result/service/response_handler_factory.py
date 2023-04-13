from settings import RMQ_FETCHER, RMQ_FETCHER_WEBDRIVER, RMQ_CAPTCHA_RESOLVER,\
    RMQ_SITE_LINK_EXTRACTOR, RMQ_FACEBOOK_EXTRACTOR
from .response_handlers import *
from ..constans import ModuleName
from ..exception import InvalidApiResponseHandlerTypeException


class ResponseHandlerFactory(object):

    QUEUE_MODULE_MAP = {
        RMQ_FETCHER: ModuleName.FETCHER,
        RMQ_FETCHER_WEBDRIVER: ModuleName.WEBDRIVER_FETCHER,
        RMQ_CAPTCHA_RESOLVER: ModuleName.CAPTCHA_RESOLVER,
        RMQ_SITE_LINK_EXTRACTOR: ModuleName.LINK_EXTRACTOR,
        RMQ_FACEBOOK_EXTRACTOR: ModuleName.FACEBOOK_EXTRACTOR
    }

    RESPONSE_HANDLERS = {
        ModuleName.FETCHER: FetcherResponseHandler(),
        ModuleName.WEBDRIVER_FETCHER: WebdriverFetcherResponseHandler(),
        ModuleName.CAPTCHA_RESOLVER: CaptchaResolverResponseHandler(),
        ModuleName.LINK_EXTRACTOR: LinkExtractorResponseHandler(),
        ModuleName.FACEBOOK_EXTRACTOR: FacebookExtractorResponseHandler()
    }

    def __init__(self):
        super(ResponseHandlerFactory, self).__init__()

    @classmethod
    def get_response_handler_by_module_name(
            cls, module_queue: str) -> ResponseHandler:

        module_name = cls.QUEUE_MODULE_MAP[module_queue]
        api_response_handler = cls.RESPONSE_HANDLERS[module_name]

        if not api_response_handler:
            raise InvalidApiResponseHandlerTypeException(
                'Unknown api handler module ' + module_name)

        return api_response_handler
