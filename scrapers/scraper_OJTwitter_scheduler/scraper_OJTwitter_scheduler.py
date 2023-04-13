import time
from datetime import datetime

import nest_asyncio
import pytz
import schedule
from tzlocal import get_localzone

from scrapers.scraper_OJTwitter.db.db import Database
from scrapers.scraper_OJTwitter.runner import run_scraper
from scrapers.scraper_OJTwitter.utils.checker import Checker
from scrapers.scraper_OJTwitter.utils.google_sheet_writer.google_sheets_writer import GoogleSheetsWriter
from scrapers.scraper_OJTwitter.utils.logger import logging
from scrapers.scraper_OJTwitter_scheduler.config import (
    TIMES_TO_RUN,
    GOOGLE_SHEET_WRITER_MAIN_PATH,
    GOOGLE_SHEET_MAIN_ID,
)

nest_asyncio.apply()


class ScraperOJTScheduler:

    def __init__(self):
        self.logger = logging.getLogger('[SCHEDULER]')
        self.db = Database()
        self.checker = Checker()
        self.google_sheets_writer = GoogleSheetsWriter(
            main_path=GOOGLE_SHEET_WRITER_MAIN_PATH,
            google_spreadsheet_id=GOOGLE_SHEET_MAIN_ID,
        )
        self.queue_names = [
            'OJT.scrapers.OJTwitter',
            'OJT.fetcher',
        ]

    def run(self):
        self.logger.info(f'Scheduler is runned. Current server time is "{datetime.utcnow()}"')
        self.scheduler()

    def scheduler(self):
        for position, time_to_run in enumerate(TIMES_TO_RUN):
            self.show_running_time(
                time_to_run=time_to_run,
                position=position + 1,
            )
            schedule \
                .every() \
                .day \
                .at(self.from_new_york_tz_to_local_tz(time_to_run)) \
                .do(self.run_scraping_flow)

        while True:
            schedule.run_pending()
            time.sleep(60)

    def run_scraping_flow(self):
        self.logger.info(f'Running method "{self.run_scraping_flow.__name__}"')

        try:
            try:
                keywords = self.google_sheets_writer.get_keywords_from_spreadsheet()
                session_id = self.db.create_session()

                for keyword in keywords:
                    run_scraper(
                        keyword=keyword,
                        session_id=session_id,
                    )

            except Exception as e:
                self.logger.info('Exception while running the scraper')
                self.logger.exception(e)
                return

            # time to wait before scraping process completion check
            time.sleep(1800)

            try:
                self.checker.check(
                    queue_names_list=self.queue_names,
                )
            except Exception:
                self.logger.info('Exception while checking the scraping process completion')
                return

            try:
                data = self.db.get_data_by_session(
                    session_id=session_id,
                )
            except Exception as e:
                self.logger.info('Exception while getting the data from the db')
                self.logger.exception(e)
                return

            try:
                self.google_sheets_writer.write_to_google_spreadsheets(
                    data=data,
                    keywords=keywords,
                )
            except Exception as e:
                self.logger.info('Exception while writing the data to the spreadsheets')
                self.logger.exception(e)
                return

        except BaseException as e:
            self.logger.exception(e)

    def show_running_time(
            self,
            time_to_run: str,
            position: int,
    ) -> None:
        self.logger.info(
            f'Scraper running time: '
            f'{position}. {time_to_run} EST. '
            f'{self.from_new_york_tz_to_local_tz(time_to_run)} IN LOCAL TZ'
        )

    @staticmethod
    def from_new_york_tz_to_local_tz(
            time_in_string: str,
    ) -> str:
        hour, minute = time_in_string.split(':')
        new_york_tz = pytz.timezone('America/New_York')
        local_tz = pytz.timezone(str(get_localzone()))
        new_york_time = datetime.now(tz=new_york_tz)
        new_york_time_for_run = new_york_time.replace(
            hour=int(hour),
            minute=int(minute),
            second=0,
        )
        local_time_for_run = new_york_time_for_run.astimezone(local_tz)
        return f'{local_time_for_run.hour:02}:{local_time_for_run.minute:02}'
