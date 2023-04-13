import os

from settings import RMQ_EXCHANGE

PREFETCH_COUNT = 20
PROJECT_ID = 'OJTwitter'
SERVICE_NAME = RMQ_EXCHANGE + '.scrapers.OJTwitter'
DB_CONNECTION_URL = os.getenv(
    'DB_CONNECTION_URL',
)
REQUEST_TIMEOUT = int(
    os.getenv(
        'REQUEST_TIMEOUT',
        30,
    )
)
REQUEST_NUMBER_OF_RETRIES = int(
    os.getenv(
        'REQUEST_NUMBER_OF_RETRIES',
        15,
    )
)
PROXIES = os.getenv(
    'PROXIES',
)
BROWSER_PROXIES = os.getenv(
    'BROWSER_PROXIES',
)
PROXIES_LOGIN = os.getenv(
    'PROXIES_LOGIN',
)
PROXIES_PASSWORD = os.getenv(
    'PROXIES_PASSWORD',
)
HEADERS = {
  'authority': 'twitter.com',
  'pragma': 'no-cache',
  'cache-control': 'no-cache',
  'sec-ch-ua': '" Not;A Brand";v="99", "Opera";v="79", "Chromium";v="93"',
  'x-twitter-client-language': 'en',
  'sec-ch-ua-mobile': '?0',
  'x-twitter-active-user': 'yes',
  'sec-ch-ua-platform': '"Windows"',
  'accept': '*/*',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://twitter.com/search?q=apple&src=typed_query&l=en',
  'accept-language': 'en-US;q=0.9,en;q=0.8',
}
QUERY_IDS_HEADERS = {
  'sec-ch-ua': '" Not;A Brand";v="99", "Opera";v="79", "Chromium";v="93"',
  'Referer': 'https://twitter.com/',
  'Origin': 'https://twitter.com',
  'sec-ch-ua-mobile': '?0',
}
EXCLUDED_LOCATIONS = [
    ' mac',
    ' iphone',
    'iphone ',
    ' ipad',
    'ipad ',
]
MAX_NUMBER_OF_REPLIES_TO_SCRAPE = int(
    os.getenv(
        'MAX_NUMBER_OF_REPLIES_TO_SCRAPE',
        7,
    )
)
MAX_NUMBERS_OF_CREDENTIALS_ERRORS = int(
    os.getenv(
        'MAX_NUMBERS_OF_CREDENTIALS_ERRORS',
        5,
    )
)
