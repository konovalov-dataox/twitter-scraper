import os
import json

from settings import RMQ_EXCHANGE

SERVICE_NAME = RMQ_EXCHANGE + '.scrapers.ScraperOJTScheduler'
PROJECT_ID = 'ScraperOJTScheduler'

SCRAPER_RUNNING_TIME_1 = os.environ.get(
    'SCRAPER_RUNNING_TIME_1',
    '06:00',
)
SCRAPER_RUNNING_TIME_2 = os.environ.get(
    'SCRAPER_RUNNING_TIME_2',
    '09:00',
)
SCRAPER_RUNNING_TIME_3 = os.environ.get(
    'SCRAPER_RUNNING_TIME_3',
    '12:00',
)
SCRAPER_RUNNING_TIME_4 = os.environ.get(
    'SCRAPER_RUNNING_TIME_4',
    '15:00',
)
SCRAPER_RUNNING_TIME_5 = os.environ.get(
    'SCRAPER_RUNNING_TIME_5',
    '18:00',
)
TIMES_TO_RUN = json.loads(
    os.environ.get(
        'TIMES_TO_RUN',
        [
            SCRAPER_RUNNING_TIME_1,
            SCRAPER_RUNNING_TIME_2,
            SCRAPER_RUNNING_TIME_3,
            SCRAPER_RUNNING_TIME_4,
            SCRAPER_RUNNING_TIME_5,
        ]
    )
)
GOOGLE_SHEET_WRITER_MAIN_PATH = os.environ.get(
    'GOOGLE_SHEET_WRITER_MAIN_PATH',
    'scrapers/scraper_OJTwitter/utils/google_sheet_writer/',
)
GOOGLE_SHEET_MAIN_ID = os.environ.get(
    'GOOGLE_SHEET_MAIN_ID',
)
