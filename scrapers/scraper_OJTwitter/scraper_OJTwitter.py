import asyncio
import datetime
import json
import re
from asyncio import sleep
from copy import deepcopy
from typing import Optional

import pytz
import requests
from fake_useragent import UserAgent

from core.api.fetcher import AsyncFetcherClient, Request, FetcherResponse
from core.async_client.async_client import AsyncAcceleratorIncomingMessage
from core.messages.fetcher import FetcherTaskMessageBody
from core.scrapers.scraper import AsyncScraper
from scrapers.scraper_OJTwitter.config import (
    PREFETCH_COUNT,
    SERVICE_NAME,
    PROXIES,
    HEADERS,
    QUERY_IDS_HEADERS,
    REQUEST_TIMEOUT,
    REQUEST_NUMBER_OF_RETRIES,
    EXCLUDED_LOCATIONS,
    MAX_NUMBER_OF_REPLIES_TO_SCRAPE,
    BROWSER_PROXIES,
    PROXIES_LOGIN,
    PROXIES_PASSWORD,
)
from scrapers.scraper_OJTwitter.constants import (
    QUERY_IDS_URL,
    SEARCH_URL_CONTAINER,
    CURSOR_CONTAINER,
    TWEET_URL_CONTAINER,
    TWEET_DETAILS_QUERY_ID_PATTERN,
    USER_DETAILS_QUERY_ID_PATTERN,
    TWEET_BROWSER_URL_CONTAINER,
    USER_URL_CONTAINER,
    USER_BROWSER_URL_CONTAINER,
    CHILD_TWEETS_URL_CONTAINER,
)
from scrapers.scraper_OJTwitter.db.db import Database
from scrapers.scraper_OJTwitter.db.models import ParentTweet, ChildTweet
from scrapers.scraper_OJTwitter.utils.logger import logging
from scrapers.scraper_OJTwitter.utils.login_manager import LoginManager


class ScraperOJTwitter(AsyncScraper):

    def __init__(
            self,
            prefetch_count: int = PREFETCH_COUNT,
            service_name: str = SERVICE_NAME
    ):
        super().__init__(prefetch_count, service_name)
        self.logger = logging.getLogger('[SCRAPER]')
        self.loop = asyncio.get_event_loop()
        self.fetcher_client = AsyncFetcherClient(self)
        self.db = Database()
        self.user_agent_randomizer = UserAgent()
        self.login_manager = LoginManager()
        credentials: tuple = self.loop.run_until_complete(
            self.login_manager.login(
                proxy=BROWSER_PROXIES,
                proxy_login=PROXIES_LOGIN,
                proxy_password=PROXIES_PASSWORD,
            )
        )
        self.auth_token = credentials[0]
        self.csrf_token = credentials[1]
        self.guest_token = credentials[2]
        self.cookies = credentials[3]
        query_ids: tuple = self.loop.run_until_complete(
            self.__get_query_ids()
        )
        self.tweet_details_query_id = query_ids[0]
        self.user_details_query_id = query_ids[1]
        self.relogin_in_process = False
        self.last_relogin_date = datetime.datetime.utcnow()

    async def start(
            self,
            message: AsyncAcceleratorIncomingMessage,
            message_body: dict,
    ) -> None:
        session_id = message_body['request']['session_id']
        keyword = message_body['request']['keyword']
        keyword = keyword.strip()
        min_date = self.db.get_min_date(
            keyword=keyword,
        )
        await self.start_search(
            message=message,
            keyword=keyword,
            min_date=min_date,
            session_id=session_id,
        )

    async def start_search(
            self,
            message: AsyncAcceleratorIncomingMessage,
            keyword: str,
            min_date: datetime.datetime,
            session_id: int,
    ) -> None:
        url = SEARCH_URL_CONTAINER.format(
            f'"{keyword.strip()}"',
            min_date.strftime('%Y-%m-%d'),
        )
        meta = {
            'request_url': url,
            'request_headers': await self.__get_headers(),
            'callback': 'handle_search_pages',
            'keyword': keyword,
            'min_date': min_date.strftime('%Y-%m-%d %X'),
            'session_id': session_id,
        }
        await self.__send_request(
            message=message,
            meta=meta,
            allowed_http_codes=[
                200,
                400,
                429,
                401,
                403,
            ],
        )

    async def handle_search_pages(
            self,
            message: AsyncAcceleratorIncomingMessage,
            message_body: dict,
    ) -> None:
        response = FetcherResponse.from_dict(message_body)

        try:
            if response.response.status_code != 200:
                raise Exception

            content = response.response.text()
            content_dict = json.loads(content)
        except BaseException:
            self.logger.exception(
                msg='Exception while converting page json-content to dict',
            )
            response.request.meta['error_count'] = response.request.meta.get('error_count', 0) + 1
            await self.__resend_request(
                message=message,
                meta=response.request.meta,
            )
            return

        found_tweets: dict = content_dict.get('globalObjects', {}).get('tweets')
        min_date = pytz.UTC.localize(
            datetime.datetime.strptime(
                response.request.meta['min_date'],
                '%Y-%m-%d %X',
            )
        )
        tweets_with_lower_date = 0

        if not found_tweets:
            self.logger.info(
                msg=f'THE {response.request.meta["keyword"]} KEYWORD SCRAPING COMPLETED: NO MORE TWEETS',
            )
            return

        for tweet_key in found_tweets.keys():
            tweet = content_dict['globalObjects']['tweets'][tweet_key]
            tweet_timestamp = datetime.datetime.strptime(
                tweet['created_at'],
                '%a %b %d %X %z %Y',
            )

            for user in tweet.get('entities', {}).get('user_mentions', []):
                tweet['full_text'] = tweet['full_text'].replace(user.get('screen_name', ''), '')

            if not await self.__check_if_tweet_body_contains_keyword(
                    keyword=response.request.meta['keyword'],
                    tweet_body=tweet['full_text'],
            ):
                continue

            if tweet_timestamp < min_date and tweets_with_lower_date < 5:
                tweets_with_lower_date += 1
                continue
            elif tweet_timestamp < min_date and tweets_with_lower_date >= 5:
                self.logger.info(
                    msg=f'THE {response.request.meta["keyword"]} KEYWORD SCRAPING COMPLETED: REACHED MIN DATE',
                )
                return

            tweet_url = TWEET_URL_CONTAINER.format(
                self.tweet_details_query_id,
                tweet['id_str'],
            )

            tweet_meta = {
                'request_url': tweet_url,
                'request_headers': response.request.request.headers,
                'callback': 'parse_tweet',
                'session_id': response.request.meta['session_id'],
                'keyword': response.request.meta['keyword'],
                'min_date': response.request.meta['min_date'],
                'current_tweet_id': tweet['id_str'],
            }
            await self.__send_request(
                message=message,
                meta=tweet_meta,
                allowed_http_codes=[
                    200,
                    400,
                    429,
                    401,
                    403,
                ],
            )

        next_page = await self.__extract_next_page_cursor(
            content_dict=content_dict,
        )

        if next_page:
            response.request.meta['request_url'] = ''.join(
                [
                    SEARCH_URL_CONTAINER.format(
                        response.request.meta['keyword'],
                        response.request.meta['min_date'].split()[0],
                    ),
                    CURSOR_CONTAINER.format(next_page),
                ]
            )
            await self.__send_request(
                message=message,
                meta=response.request.meta,
                allowed_http_codes=[
                    200,
                    400,
                    429,
                    401,
                    403,
                ],
            )

    async def parse_tweet(
            self,
            message: AsyncAcceleratorIncomingMessage,
            message_body: dict,
    ) -> None:
        response = FetcherResponse.from_dict(message_body)

        try:
            if response.response.status_code != 200:
                raise Exception

            content = response.response.text()
            content_dict = json.loads(content)
        except BaseException:
            self.logger.exception(
                msg='Exception while converting page json-content to dict',
            )
            response.request.meta['error_count'] = response.request.meta.get('error_count', 0) + 1
            await self.__resend_request(
                message=message,
                meta=response.request.meta,
            )
            return

        current_tweet_id = response.request.meta['current_tweet_id']
        current_tweet_position = await self.__get_tweet_position_by_id(
            tweet_id=current_tweet_id,
            content_dict=content_dict,
        )

        tweet_meta = dict()
        tweet_meta['parent_tweet_id'] = response.request.meta.get('parent_tweet_id')
        tweet_meta['session_id'] = response.request.meta['session_id']
        tweet_meta['who_twitted_user_handlename'] = await self.__extract_tweet_user(
            parent=True,
            content_dict=content_dict,
            tweet_position=current_tweet_position,
        )

        if not tweet_meta['who_twitted_user_handlename']:
            self.logger.info('Skipped tweet (Probably because of access lock)')
            return

        tweet_meta['tweet_id'] = await self.__extract_tweet_id(
            parent=True,
            content_dict=content_dict,
            tweet_position=current_tweet_position,
        )
        tweet_meta['tweet_url'] = TWEET_BROWSER_URL_CONTAINER.format(
            tweet_meta['who_twitted_user_handlename'],
            tweet_meta['tweet_id'],
        )
        tweet_meta['tweet_keyword'] = response.request.meta['keyword']
        tweet_meta['tweet_body'] = await self.__extract_tweet_body(
            parent=True,
            content_dict=content_dict,
            tweet_position=current_tweet_position,
        )

        if response.request.meta['keyword'].lower() not in tweet_meta.get('tweet_body', '').lower():
            self.logger.info('NOT FOUND KEYWORD IN THE TWEET BODY. SKIPPED')
            return

        tweet_meta['tweet_timestamp'] = await self.__extract_tweet_timestamp(
            parent=True,
            content_dict=content_dict,
            tweet_position=current_tweet_position,
        )
        tweet_user_url = USER_URL_CONTAINER.format(
            self.user_details_query_id,
            tweet_meta['who_twitted_user_handlename'],
        )
        tweet_meta['request_url'] = tweet_user_url
        tweet_meta['request_headers'] = response.request.request.headers
        tweet_meta['callback'] = 'parse_tweet_user'
        await self.__send_request(
            message=message,
            meta=tweet_meta,
            allowed_http_codes=[
                200,
                400,
                429,
                401,
                403,
            ],
        )

        if not tweet_meta['parent_tweet_id']:
            meta = deepcopy(response.request.meta)
            meta['parent_tweet_id'] = tweet_meta['tweet_id']
            meta['parent_tweet_position'] = current_tweet_position
            meta['content_dict'] = content_dict
            await self.parse_child_tweets(
                message=message,
                meta=meta,
            )

    async def parse_child_tweets(
            self,
            message: AsyncAcceleratorIncomingMessage,
            message_body: dict = None,
            meta: dict = None,
    ) -> None:
        if message_body:
            response = FetcherResponse.from_dict(message_body)

            try:
                if response.response.status_code != 200:
                    raise Exception

                content = response.response.text()
                content_dict = json.loads(content)
            except BaseException:
                self.logger.exception(
                    msg='Exception while converting page json-content to dict',
                )
                response.request.meta['error_count'] = response.request.meta.get('error_count', 0) + 1
                await self.__resend_request(
                    message=message,
                    meta=response.request.meta,
                )
                return

            meta = response.request.meta
            positions_to_skip = 0
        else:
            content_dict = meta['content_dict']
            positions_to_skip = meta['parent_tweet_position'] + 1

        tweets = content_dict['data']['threaded_conversation_with_injections']['instructions'][0]['entries']

        if len(tweets) <= positions_to_skip:
            return

        for tweet_number, tweet in enumerate(tweets[positions_to_skip:]):

            if tweet_number + meta.get('last_scraped_tweet_number', 0) == MAX_NUMBER_OF_REPLIES_TO_SCRAPE:
                return

            if 'cursor-bottom' in tweet['entryId']:
                next_page_url = CHILD_TWEETS_URL_CONTAINER.format(
                    self.tweet_details_query_id,
                    meta['parent_tweet_id'],
                    tweet['content']['itemContent']['value'],
                )
                last_scraped_tweet_number = tweet_number if not meta.get('last_scraped_tweet_number') \
                    else tweet_number + 1 + meta['last_scraped_tweet_number']
                next_page_meta = {
                    'request_url': next_page_url,
                    'request_headers': await self.__get_headers(),
                    'callback': 'parse_child_tweets',
                    'parent_tweet_id': meta['parent_tweet_id'],
                    'keyword': meta['keyword'],
                    'last_scraped_tweet_number': last_scraped_tweet_number,
                    'session_id': meta['session_id'],
                }
                await self.__send_request(
                    message=message,
                    meta=next_page_meta,
                    allowed_http_codes=[
                        200,
                        400,
                        429,
                        401,
                        403,
                    ],
                )
                return

            child_tweet_meta = dict()
            child_tweet_meta['parent_tweet_id'] = meta['parent_tweet_id']
            child_tweet_meta['session_id'] = meta['session_id']
            child_tweet_meta['who_twitted_user_handlename'] = await self.__extract_tweet_user(
                parent=False,
                content_dict=content_dict,
                tweet_position=positions_to_skip + tweet_number,
            )

            if not child_tweet_meta['who_twitted_user_handlename']:
                self.logger.info('Skipped tweet (Probably because of access lock)')
                continue

            child_tweet_meta['tweet_id'] = await self.__extract_tweet_id(
                parent=False,
                content_dict=content_dict,
                tweet_position=positions_to_skip + tweet_number,
            )
            child_tweet_meta['tweet_url'] = TWEET_BROWSER_URL_CONTAINER.format(
                child_tweet_meta['who_twitted_user_handlename'],
                child_tweet_meta['tweet_id'],
            )
            child_tweet_meta['tweet_keyword'] = meta['keyword']
            child_tweet_meta['tweet_body'] = await self.__extract_tweet_body(
                parent=False,
                content_dict=content_dict,
                tweet_position=positions_to_skip + tweet_number,
            )
            child_tweet_meta['tweet_timestamp'] = await self.__extract_tweet_timestamp(
                parent=False,
                content_dict=content_dict,
                tweet_position=positions_to_skip + tweet_number,
            )
            tweet_user_url = USER_URL_CONTAINER.format(
                self.user_details_query_id,
                child_tweet_meta['who_twitted_user_handlename'],
            )
            child_tweet_meta['request_url'] = tweet_user_url
            child_tweet_meta['request_headers'] = await self.__get_headers()
            child_tweet_meta['callback'] = 'parse_tweet_user'
            await self.__send_request(
                message=message,
                meta=child_tweet_meta,
                allowed_http_codes=[
                    200,
                    400,
                    429,
                    401,
                    403,
                ],
            )

    async def parse_tweet_user(
            self,
            message: AsyncAcceleratorIncomingMessage,
            message_body: dict,
    ) -> None:
        response = FetcherResponse.from_dict(message_body)

        try:
            if response.response.status_code != 200:
                raise Exception

            content = response.response.text()
            content_dict = json.loads(content)
        except BaseException:
            self.logger.exception(
                msg='Exception while converting page json-content to dict',
            )
            response.request.meta['error_count'] = response.request.meta.get('error_count', 0) + 1
            await self.__resend_request(
                message=message,
                meta=response.request.meta,
            )
            return

        tweet_data = deepcopy(response.request.meta)
        tweet_data['who_twitted_user_url'] = await self.__extract_who_twitted_user_url(
            content_dict=content_dict,
        )
        tweet_data['who_twitted_user_bio'] = await self.__extract_who_twitted_user_bio(
            content_dict=content_dict,
        )
        tweet_data['who_twitted_user_location'] = await self.__extract_who_twitted_user_location(
            content_dict=content_dict,
        )
        tweet_data['who_twitted_user_website_url'] = await self.__extract_who_twitted_user_website_url(
            content_dict=content_dict,
        )
        tweet_data['who_twitted_user_join_date'] = await self.__extract_who_twitted_user_join_date(
            content_dict=content_dict,
        )

        if tweet_data.get('parent_tweet_id'):
            await self.__save_child_tweet(
                tweet_data=tweet_data,
            )
        else:
            await self.__save_parent_tweet(
                tweet_data=tweet_data,
            )

    async def __save_parent_tweet(
            self,
            tweet_data: dict,
    ) -> None:
        parent_tweet = ParentTweet(
            tweet_id=int(tweet_data['tweet_id']),
            session_id=int(tweet_data['session_id']),
            tweet_url=tweet_data['tweet_url'],
            tweet_keyword=tweet_data['tweet_keyword'],
            tweet_body=tweet_data['tweet_body'],
            tweet_timestamp=tweet_data['tweet_timestamp'],
            who_twitted_user_handlename=tweet_data['who_twitted_user_handlename'],
            who_twitted_user_url=tweet_data['who_twitted_user_url'],
            who_twitted_user_bio=tweet_data['who_twitted_user_bio'],
            who_twitted_user_location=tweet_data['who_twitted_user_location'],
            who_twitted_user_website_url=tweet_data['who_twitted_user_website_url'],
            who_twitted_user_join_date=tweet_data['who_twitted_user_join_date'],
            scraping_date=datetime.datetime.utcnow(),
        )
        self.db.save_parent_tweet(
            parent_tweet=parent_tweet,
        )

    async def __save_child_tweet(
            self,
            tweet_data: dict,
    ) -> None:
        child_tweet = ChildTweet(
            tweet_id=int(tweet_data['tweet_id']),
            parent_tweet_id=int(tweet_data['parent_tweet_id']),
            session_id=int(tweet_data['session_id']),
            tweet_url=tweet_data['tweet_url'],
            tweet_keyword=tweet_data['tweet_keyword'],
            tweet_body=tweet_data['tweet_body'],
            tweet_timestamp=tweet_data['tweet_timestamp'],
            who_twitted_user_handlename=tweet_data['who_twitted_user_handlename'],
            who_twitted_user_url=tweet_data['who_twitted_user_url'],
            who_twitted_user_bio=tweet_data['who_twitted_user_bio'],
            who_twitted_user_location=tweet_data['who_twitted_user_location'],
            who_twitted_user_website_url=tweet_data['who_twitted_user_website_url'],
            who_twitted_user_join_date=tweet_data['who_twitted_user_join_date'],
            scraping_date=datetime.datetime.utcnow(),
        )
        self.db.save_child_tweet(
            child_tweet=child_tweet,
        )

    async def __send_request(
            self,
            message: AsyncAcceleratorIncomingMessage,
            meta: dict,
            allowed_http_codes: list = None,
    ) -> None:

        if allowed_http_codes is None:
            allowed_http_codes = [200]

        r = Request(
            method='GET',
            url=meta['request_url'],
            headers=meta['request_headers'],
            cookies=self.cookies,
            proxies=PROXIES,
            timeout=REQUEST_TIMEOUT,
            allowed_http_codes=allowed_http_codes,
            max_retries=REQUEST_NUMBER_OF_RETRIES,
        )
        task = FetcherTaskMessageBody(
            r,
            callback=meta['callback'],
            meta=meta
        )
        await self.fetcher_client.send(task, message)

    async def __resend_request(
            self,
            message: AsyncAcceleratorIncomingMessage,
            meta: dict,
    ) -> None:
        if meta['error_count'] > REQUEST_NUMBER_OF_RETRIES:
            return

        if not self.relogin_in_process \
                and self.last_relogin_date < datetime.datetime.utcnow() - datetime.timedelta(minutes=10):
            self.relogin_in_process = True
            await self.__refresh_credentials(
                proxy=BROWSER_PROXIES,
                proxy_login=PROXIES_LOGIN,
                proxy_password=PROXIES_PASSWORD,
            )
            await self.__refresh_query_ids()
            self.relogin_in_process = False
            self.last_relogin_date = datetime.datetime.utcnow()
        else:
            await sleep(60)

        meta['request_headers'] = await self.__get_headers()
        await self.__send_request(
            message=message,
            meta=meta,
            allowed_http_codes=[
                200,
                400,
                429,
                401,
                403,
            ],
        )

    async def __refresh_credentials(
            self,
            proxy: str = None,
            proxy_login: str = None,
            proxy_password: str = None,
    ) -> None:
        credentials = await self.login_manager.login(
            proxy=proxy,
            proxy_login=proxy_login,
            proxy_password=proxy_password,
        )
        self.auth_token = credentials[0]
        self.csrf_token = credentials[1]
        self.guest_token = credentials[2]
        self.cookies = credentials[3]

    async def __refresh_query_ids(
            self,
    ) -> None:
        query_ids = await self.__get_query_ids()
        self.tweet_details_query_id = query_ids[0]
        self.user_details_query_id = query_ids[1]

    async def __get_headers(self) -> dict:
        headers = deepcopy(HEADERS)
        headers['user-agent'] = self.user_agent_randomizer.random
        headers['authorization'] = self.auth_token
        headers['x-csrf-token'] = self.csrf_token
        headers['x-guest-token'] = self.guest_token
        return headers

    async def __get_query_ids(
            self,
            retry_number: int = 0,
    ) -> tuple:
        try:
            self.logger.info(
                msg='STARTED THE QUERY IDS EXTRACTION',
            )
            headers = deepcopy(QUERY_IDS_HEADERS)
            headers['User-Agent'] = self.user_agent_randomizer.random
            response = requests.get(
                url=QUERY_IDS_URL,
                timeout=10,
                headers=headers,
            )
            tweet_details_query_id = re.findall(
                pattern=TWEET_DETAILS_QUERY_ID_PATTERN,
                string=response.text,
            )[0]
            user_details_query_id = re.findall(
                pattern=USER_DETAILS_QUERY_ID_PATTERN,
                string=response.text,
            )[0]
            self.logger.info(
                msg='COMPLETED THE QUERY IDS EXTRACTION',
            )
            return tweet_details_query_id, user_details_query_id
        except BaseException as e:
            if retry_number < REQUEST_NUMBER_OF_RETRIES:
                self.logger.exception(
                    msg='ERROR DURING THE QUERY IDS EXTRACTION. RETRY...',
                )
                return await self.__get_query_ids(
                    retry_number=retry_number + 1,
                )
            raise e

    @staticmethod
    async def __extract_next_page_cursor(
            content_dict: dict,
    ) -> Optional[str]:
        for entry in content_dict['timeline']['instructions'][0]['addEntries']['entries']:
            if entry.get('content', {}).get('operation', {}).get('cursor', {}).get('cursorType') == 'Bottom':
                return entry['content']['operation']['cursor'].get('value')

        for entry in content_dict['timeline']['instructions']:
            if entry.get('replaceEntry', {}).get('entry', {}).get('content', {}).get('operation', {}) \
                    .get('cursor', {}).get('cursorType') == 'Bottom':
                return entry['replaceEntry']['entry']['content']['operation']['cursor']['value']

    @staticmethod
    async def __get_tweet_position_by_id(
            tweet_id: str,
            content_dict: dict,
    ) -> int:
        tweets = content_dict['data']['threaded_conversation_with_injections']['instructions'][0]['entries']
        for position, entry in enumerate(tweets):
            if tweet_id == entry.get('content', {}).get('itemContent', {}).get('tweet_results', {}) \
                    .get('result', {}).get('rest_id'):
                return position

    @staticmethod
    async def __extract_tweet_user(
            parent: bool,
            content_dict: dict,
            tweet_position: int = 0,
    ) -> Optional[str]:
        try:
            if parent:
                return content_dict['data']['threaded_conversation_with_injections']['instructions'][0] \
                    ['entries'][tweet_position]['content']['itemContent']['tweet_results']['result']['core'] \
                    ['user_results']['result']['legacy']['screen_name']
            else:
                return content_dict['data']['threaded_conversation_with_injections']['instructions'][0]['entries'] \
                    [tweet_position]['content']['items'][0]['item']['itemContent']['tweet_results']['result']['core'] \
                    ['user_results']['result']['legacy']['screen_name']
        except BaseException:
            return None

    @staticmethod
    async def __extract_tweet_id(
            parent: bool,
            content_dict: dict,
            tweet_position: int = 0,
    ) -> Optional[str]:
        try:
            if parent:
                return content_dict['data']['threaded_conversation_with_injections']['instructions'][0] \
                    ['entries'][tweet_position]['content']['itemContent']['tweet_results']['result']['rest_id']
            else:
                return content_dict['data']['threaded_conversation_with_injections']['instructions'][0]['entries'] \
                    [tweet_position]['content']['items'][0]['item']['itemContent']['tweet_results']['result']['rest_id']
        except BaseException:
            return None

    @staticmethod
    async def __extract_tweet_body(
            parent: bool,
            content_dict: dict,
            tweet_position: int = 0,
    ) -> Optional[str]:
        try:
            if parent:
                tweet_body = content_dict['data']['threaded_conversation_with_injections']['instructions'][0] \
                    ['entries'][tweet_position]['content']['itemContent']['tweet_results']['result'] \
                    ['legacy']['full_text']

                try:
                    for url_entry in content_dict['data']['threaded_conversation_with_injections']['instructions'] \
                            [0]['entries'][tweet_position]['content']['itemContent']['tweet_results']['result'] \
                            ['core']['user_results']['result']['legacy']['entities']['description']['urls']:
                        tweet_body = tweet_body.replace(
                            url_entry['url'],
                            url_entry['display_url'],
                        )
                except Exception:
                    pass

                try:
                    for media_entry in content_dict['data']['threaded_conversation_with_injections']['instructions'] \
                            [0]['entries'][tweet_position]['content']['itemContent']['tweet_results']['result'] \
                            ['legacy']['entities']['media']:
                        tweet_body = tweet_body.replace(
                            media_entry['url'],
                            media_entry['media_url_https'],
                        )
                except Exception:
                    pass
            else:
                tweet_body = content_dict['data']['threaded_conversation_with_injections']['instructions'][0] \
                    ['entries'][tweet_position]['content']['items'][0]['item']['itemContent']['tweet_results'] \
                    ['result']['legacy']['full_text']

                try:
                    for url_entry in content_dict['data']['threaded_conversation_with_injections']['instructions'][0] \
                            ['entries'][tweet_position]['content']['items'][0]['item']['itemContent'] \
                            ['tweet_results']['result']['core']['user_results']['result']['legacy'] \
                            ['entities']['description']['urls']:
                        tweet_body = tweet_body.replace(
                            url_entry['url'],
                            url_entry['display_url'],
                        )
                except Exception:
                    pass

                try:
                    for media_entry in content_dict['data']['threaded_conversation_with_injections']['instructions'] \
                            [0]['entries'][tweet_position]['content']['items'][0]['item']['itemContent'] \
                            ['tweet_results']['result']['legacy']['entities']['media']:
                        tweet_body = tweet_body.replace(
                            media_entry['url'],
                            media_entry['media_url_https'],
                        )
                except Exception:
                    pass

            return tweet_body.replace('&amp;', '&').strip()
        except BaseException:
            return None

    @staticmethod
    async def __extract_tweet_timestamp(
            parent: bool,
            content_dict: dict,
            tweet_position: int = 0,
    ) -> Optional[datetime.datetime]:
        try:
            if parent:
                return datetime.datetime.strptime(
                    content_dict['data']['threaded_conversation_with_injections']['instructions'][0]['entries'] \
                        [tweet_position]['content']['itemContent']['tweet_results']['result']['legacy']['created_at'],
                    '%a %b %d %X %z %Y',
                )
            else:
                return datetime.datetime.strptime(
                    content_dict['data']['threaded_conversation_with_injections']['instructions'][0]['entries'] \
                        [tweet_position]['content']['items'][0]['item']['itemContent']['tweet_results']['result'] \
                        ['legacy']['created_at'],
                    '%a %b %d %X %z %Y',
                )
        except BaseException:
            return None

    @staticmethod
    async def __extract_who_twitted_user_url(
            content_dict: dict,
    ) -> Optional[str]:
        try:
            return USER_BROWSER_URL_CONTAINER.format(
                content_dict['data']['user']['result']['legacy']['screen_name'],
            )
        except BaseException:
            return None

    @staticmethod
    async def __extract_who_twitted_user_bio(
            content_dict: dict,
    ) -> Optional[str]:
        try:
            user_bio: str = content_dict['data']['user']['result']['legacy']['description']

            try:
                for url_entry in content_dict['data']['user']['result']['legacy']['entities']['description']['urls']:
                    user_bio = user_bio.replace(
                        url_entry['url'],
                        url_entry['display_url'],
                    )
            except Exception:
                pass

            return user_bio.strip() if user_bio else None
        except BaseException:
            return None

    @staticmethod
    async def __extract_who_twitted_user_location(
            content_dict: dict,
    ) -> Optional[str]:
        try:
            location = content_dict['data']['user']['result']['legacy']['location']

            for excluded_location in EXCLUDED_LOCATIONS:
                if excluded_location.strip() == location.strip() or excluded_location in location:
                    return None

            return location if location else None

        except BaseException:
            return None

    @staticmethod
    async def __extract_who_twitted_user_website_url(
            content_dict: dict,
    ) -> Optional[str]:
        try:
            return content_dict['data']['user']['result']['legacy']['entities'] \
                ['url']['urls'][0]['display_url']
        except BaseException:
            return None

    @staticmethod
    async def __extract_who_twitted_user_join_date(
            content_dict: dict,
    ) -> Optional[datetime.datetime]:
        try:
            return datetime.datetime.strptime(
                content_dict['data']['user']['result']['legacy']['created_at'],
                '%a %b %d %X %z %Y',
            )
        except BaseException:
            return None

    @staticmethod
    async def __check_if_tweet_body_contains_keyword(
            keyword: str,
            tweet_body: str,
    ) -> bool:
        keyword_parts = [part.lower().strip() for part in keyword.split() if part.strip()]

        if tweet_body:
            for part in keyword_parts:
                if part not in tweet_body.lower():
                    return False

        return True
