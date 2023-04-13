from core.module import AcceleratorModule

module = AcceleratorModule.declare_module(
    name='scrapers.OJTwitter',
    requirements=[
        'psycopg2-binary',
        'sqlalchemy',
        'pymysql',
        'fake-useragent',
        'requests',
        'google-api-python-client',
        'gspread',
        'pytz',
        'nest-asyncio',
        'asyncio',
        'pyppeteer',
        'pyppeteer-stealth',
    ],
)

if module:
    from .scraper_OJTwitter import ScraperOJTwitter

    module.module_class = ScraperOJTwitter
