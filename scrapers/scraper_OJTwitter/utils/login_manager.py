from asyncio import sleep

import nest_asyncio
from pyppeteer import launch
from pyppeteer.page import Page
from pyppeteer_stealth import stealth

from scrapers.scraper_OJTwitter.utils.logger import logging

nest_asyncio.apply()
AUTH_TOKEN = None
CSRF_TOKEN = None
GUEST_TOKEN = None


def analyze(request):
    if request.headers.get('x-csrf-token'):
        global CSRF_TOKEN
        CSRF_TOKEN = request.headers['x-csrf-token']
    if request.headers.get('authorization'):
        global AUTH_TOKEN
        AUTH_TOKEN = request.headers['authorization']
    if request.headers.get('x-guest-token'):
        global GUEST_TOKEN
        GUEST_TOKEN = request.headers['x-guest-token']


class LoginManager:
    _LOGIN_URL = 'https://twitter.com/search?q=apple&src=typed_query'
    _LOAD_TIMEOUT = 30000
    _LOGIN_ACTION_TIME_S = 10

    def __init__(self):
        self.logger = logging.getLogger('[LOGIN_MANAGER]')
        self.browser = None
        self.page = None

    async def login(
            self,
            proxy: str = None,
            proxy_login: str = None,
            proxy_password: str = None,
    ) -> tuple:
        try:
            proxy = None
            self.logger.info('LOGIN START')
            await self._configurate_the_page(
                proxy=proxy,
                proxy_login=proxy_login,
                proxy_password=proxy_password,
            )
            # await self._check_page_hiding()
            self.logger.info('REQUESTING THE TWITTER PAGE')
            await self._goto(url=self._LOGIN_URL)
            await sleep(5)
            cookies = await self._extract_cookies()
            auth_token = AUTH_TOKEN
            csrf_token = CSRF_TOKEN
            guest_token = GUEST_TOKEN
            await self.__close_browser()

            if all([auth_token, csrf_token, guest_token, cookies]):
                self.logger.info('LOGIN SUCCEEDED')
                return AUTH_TOKEN, CSRF_TOKEN, GUEST_TOKEN, cookies
            else:
                self.logger.exception(
                    f'RETRY!\n'
                    f'Reason: not found any: [AUTH_TOKEN, CSRF_TOKEN, cookies]\n\n'
                    f'Actual values\n'
                    f'AUTH_TOKEN: {AUTH_TOKEN}\n'
                    f'CSRF_TOKEN: {CSRF_TOKEN}\n'
                    f'cookies len: {len(cookies)}'
                )
                return await self.login(
                    proxy=proxy,
                    proxy_login=proxy_login,
                    proxy_password=proxy_password,
                )
        except BaseException:
            await self.__close_browser()
            self.logger.exception(
                f'RETRY!\n'
                f'Reason: Exception in pyppeeter flow\n\n'
            )
            return await self.login(
                proxy=proxy,
                proxy_login=proxy_login,
                proxy_password=proxy_password,
            )

    async def _configurate_the_page(
            self,
            proxy: str,
            proxy_login: str = None,
            proxy_password: str = None,
    ) -> None:
        if proxy:
            self.browser = await launch(
                headless=True,
                timeout=120000,
                args=[
                    f'--proxy-server={proxy}',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-dev-shm-usage'
                ]
            )
            self.page = await self.browser.newPage()

            if proxy_login and proxy_password:
                self.logger.info('AUTHENTICATION')
                await self.page.authenticate({'username': f'{proxy_login}', 'password': f'{proxy_password}'})
        else:
            self.browser = await launch(
                headless=True,
                timeout=120000,
                args=[
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                ]
            )
            self.page: Page = await self.browser.newPage()

        await stealth(self.page)
        self.page.on('request', analyze)

    async def _goto(
            self,
            url: str,
            exceptions_count: int = 0
    ) -> None:
        try:
            await self.page.goto(
                url,
                timeout=self._LOAD_TIMEOUT,
            )
        except Exception:
            if exceptions_count < 3:
                await self._goto(
                    url=url,
                    exceptions_count=exceptions_count + 1,
                )

    async def _check_page_hiding(self) -> None:
        try:
            await self._goto(
                url='https://bot.sannysoft.com',
            )
            await sleep(2)
        except Exception:
            pass

    async def _extract_cookies(self) -> dict:
        cookies = dict()
        cookies_list = await self.page.cookies()
        for cookie in cookies_list:
            name = cookie['name']
            value = cookie['value']
            cookies[name] = value
        return cookies

    async def __close_browser(self):
        try:
            await self.browser.close()
        except BaseException:
            pass
