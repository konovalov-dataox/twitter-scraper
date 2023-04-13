import logging
import os

LOGGING_LEVEL = logging.INFO

RMQ_EXCHANGE: str = os.environ.get('EXCHANGE', 'accelerator')
'''
Rabbit queues names by services definitions.
Exchange name added to queue name as prefix for two reasons
 - it allow to modify routing keys
 - makes relations between queue name and exchange name more clear and visible
'''
RMQ_API_BUFFER_RESULT: str = RMQ_EXCHANGE + '.api_buffer_result'
RMQ_BOT_PROTECTION_TESTER: str = RMQ_EXCHANGE + '.bot_protection_tester'
RMQ_BROWSERLESS_FETCHER: str = RMQ_EXCHANGE + '.browserless_fetcher'
RMQ_EVENT_TRIGGER: str = RMQ_EXCHANGE + '.event_trigger'
RMQ_FACEBOOK_EXTRACTOR: str = RMQ_EXCHANGE + '.facebook_extractor'
RMQ_GOOGLE_PLACES_EXTRACTOR: str = RMQ_EXCHANGE + '.google_places_extractor'
RMQ_FETCHER: str = RMQ_EXCHANGE + '.fetcher'
RMQ_NOTIFIER: str = RMQ_EXCHANGE + '.notifier'
RMQ_SITE_LINK_EXTRACTOR: str = RMQ_EXCHANGE + '.site_links_extractor'
RMQ_STORAGE_EXPORTER: str = RMQ_EXCHANGE + '.storage_exporter'
RMQ_UPLOADER: str = RMQ_EXCHANGE + '.uploader'
RMQ_CAPTCHA_RESOLVER: str = RMQ_EXCHANGE + '.captcha_resolver'
RMQ_ERROR_MANAGER: str = RMQ_EXCHANGE + '.error_messages'
RMQ_ENGINE_DDL: str = RMQ_EXCHANGE + '.engine_ddl'
RMQ_STORAGE: str = RMQ_EXCHANGE + '.storage'
RMQ_MEDIA_DOWNLOADER: str = RMQ_EXCHANGE + '.media_downloader'
RMQ_GOOGLE_NEWS_EXTRACTOR: str = RMQ_EXCHANGE + '.google_news_extractor'


# Java services
RMQ_FETCHER_WEBDRIVER: str = RMQ_EXCHANGE + '.fetcher.webdriver'

'''
The half-automatic map that declare relations
between real module name to its queue name.
It should be executed after all queues names wos defined.

Don't forget add your module name and queue relations in
this dictionary if you're create new one !!!
'''
QUEUE_MODULE_MAP: dict = {
    RMQ_API_BUFFER_RESULT: 'api_buffer_result',
    RMQ_BOT_PROTECTION_TESTER: 'bot_protection_tester',
    RMQ_BROWSERLESS_FETCHER: 'browserless_fetcher',
    RMQ_EVENT_TRIGGER: 'event_trigger',
    RMQ_FACEBOOK_EXTRACTOR: 'facebook_extractor',
    RMQ_FETCHER: 'fetcher',
    RMQ_NOTIFIER: 'notifier',
    RMQ_SITE_LINK_EXTRACTOR: 'site_links_extractor',
    RMQ_STORAGE_EXPORTER: 'storage_exporter',
    RMQ_UPLOADER: 'uploader',
    RMQ_CAPTCHA_RESOLVER: 'captcha_resolver',
    RMQ_ERROR_MANAGER: 'error_manager',
    RMQ_FETCHER_WEBDRIVER: 'fetcher_webdriver',
    RMQ_ENGINE_DDL: 'engine_ddl',
    RMQ_STORAGE: 'storage'
}

NOT_COMPRESSED_MESSAGE_QUEUES: set = {
    RMQ_ERROR_MANAGER,
    RMQ_CAPTCHA_RESOLVER,
    RMQ_FETCHER_WEBDRIVER,
    RMQ_EXCHANGE + '.publisher'
}

'''
Delivery mode responses for messages persistent
Persistent messages are saved in hard disk, so they can be restored
1 - not persistent (by default in rabbit)
2 - persistent
'''
DELIVERY_MODE = 2

RMQ_URL_CONNECTION_STR: str = ''
MONGO_URL_CONNECTION_STR: str = ''
ACCELERATOR_DB_URL: str = ''
LOG_DB_LOCATOR: str = ''
REDIS_HOST: str = ''
REDIS_PORT: int = 7  # Echo port
REDIS_PASS: str = ''
CACHING_PROXY_ADDRESS: str = ''

'''
STAGE is DEV by default 
You should set STAGE environment variable to one of
TEST DEV or PROD to redefine environment.
It should help avoid collisions with determinations of environments types.
'''

STAGE: str = os.environ.get('STAGE', 'DEV')

ACCELERATOR_DB_URL = os.environ.get('ACCELERATOR_DB_URL', ACCELERATOR_DB_URL)
RMQ_URL_CONNECTION_STR = os.environ.get('RMQ_URL', RMQ_URL_CONNECTION_STR)
MONGO_URL_CONNECTION_STR = os.environ.get('MONGO_URL', MONGO_URL_CONNECTION_STR)
LOG_DB_LOCATOR = os.environ.get('LOG_DB_LOCATOR', LOG_DB_LOCATOR)

REDIS_HOST = os.environ.get('REDIS_HOST', REDIS_HOST)
REDIS_PORT = os.environ.get('REDIS_PORT', REDIS_PORT)
REDIS_PASS = os.environ.get('REDIS_PASS', REDIS_PASS)
REDIS_SESSION_BLACK_LIST = os.environ.get('REDIS_SESSION_BLACK_LIST', 'session_black_list')
CACHING_PROXY_ADDRESS = os.environ.get('CACHING_PROXY_ADDRESS', CACHING_PROXY_ADDRESS)

'''
Mapping of redis db's
'''
REDIS_DB_CORE = 0
REDIS_DB_API_BUFFER_RESULT = 1
REDIS_DB_EVENT_TRIGGER = 2
REDIS_DB_SITE_LINK_EXTRACTOR = 3
REDIS_DB_DDL = 4
