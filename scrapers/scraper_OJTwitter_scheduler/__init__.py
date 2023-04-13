from core.module import AcceleratorModule

module = AcceleratorModule.declare_module(
    name='scrapers.ScraperOJTScheduler',
    requirements=[
        'schedule',
        'parsel',
        'sqlalchemy',
        'pyppeteer',
        'pyppeteer-stealth',
        'psycopg2-binary',
        'yagmail',
        'nest_asyncio',
        'httpx',
        'pytz',
        'fake-useragent',
        'requests',
        'google-api-python-client',
        'gspread',
        'nest-asyncio',
        'asyncio',
        'tzlocal',
    ]
)

if module:
    from .scraper_OJTwitter_scheduler import ScraperOJTScheduler

    module.module_class = ScraperOJTScheduler
