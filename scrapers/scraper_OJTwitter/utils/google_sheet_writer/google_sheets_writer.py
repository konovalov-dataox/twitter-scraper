from typing import Tuple

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
from gspread import Worksheet, Client

from scrapers.scraper_OJTwitter.utils.logger import logging


class GoogleSheetsWriter:
    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://spreadsheets.google.com/feeds',
    ]

    def __init__(
            self,
            google_spreadsheet_id: str,
            main_path: str = None,
    ):
        self.main_path = main_path
        self.logger = logging.getLogger('[GOOGLE_SHEETS_WRITER]')
        self.__creds = self.__read_creds()
        gc = Client(auth=self.__creds)
        gc.session = AuthorizedSession(self.__creds)
        self._spreadsheet = gc.open_by_key(google_spreadsheet_id)

    def write_to_google_spreadsheets(
            self,
            data: dict,
            keywords: list,
    ) -> None:
        try:
            for keyword in keywords:
                self.logger.info(f'KEYWORD: {keyword}')
                worksheet, is_new = self._get_worksheet(
                    title=keyword,
                )

                if is_new:
                    self.write_columns_names_to_created_sheet(
                        worksheet=worksheet,
                    )

                keyword_data = data.get(keyword)

                if keyword_data:
                    self.write_keyword_data_to_google_sheet(
                        worksheet=worksheet,
                        data=keyword_data,
                    )

        except BaseException as e:
            self.logger.info('Exception when writing to Google spreadsheet')
            raise e

    def write_columns_names_to_created_sheet(
            self,
            worksheet: Worksheet,
    ) -> None:
        try:
            worksheet.insert_row(
                [
                    'Keyword',
                    'URL to Tweet/Comment',
                    'Body of Tweet',
                    'Timestamp of Tweet',
                    'Handlename of who twitted',
                    'URL of the User Profile of who tweeted',
                    'Full text of Bio of User who tweeted',
                    'Location',
                    'Website URL',
                    'Joined Twitter Date',
                    'Date of scraping',
                    'Handle names of everyone who commented',
                    'IndividualURLs to the User Profiles of everyone who commented on the post',
                    'Body of Comment',
                    'Full Bios of all User Profiles who commented on the post',
                    'Website URL',
                    'Joined Twitter Date',
                ]
            )
        except Exception:
            return self.write_columns_names_to_created_sheet(
                worksheet=worksheet,
            )

    def write_keyword_data_to_google_sheet(
            self,
            worksheet: Worksheet,
            data: list,
    ) -> None:
        rows = list()
        self.logger.info('STARTED PARSING THE DATA FROM DICTS TO GOOGLE SHEET ROWS')
        for tweet_batch_data in data:
            rows.extend(
                self.parse_tweet_batch_to_rows(
                    tweet_batch=tweet_batch_data,
                )
            )
        self.logger.info('PARSING COMPLETED')

        self.logger.info(f'STARTED WRITING THE DATA ROWS TO THE SPREADSHEET: {worksheet.url}')
        for rows_part in self.split_list(rows):
            self.write_to_worksheet(
                worksheet=worksheet,
                rows=rows_part,
            )
        self.logger.info('WRITING COMPLETED')

    @staticmethod
    def parse_tweet_batch_to_rows(
            tweet_batch: dict,
    ) -> list:
        values = list()

        if len(tweet_batch['child_tweets']) > 0:
            values.append(
                [
                    tweet_batch['parent_tweet']['tweet_keyword'],
                    tweet_batch['parent_tweet']['tweet_url'],
                    tweet_batch['parent_tweet']['tweet_body'],
                    str(tweet_batch['parent_tweet']['tweet_timestamp'])
                    if tweet_batch['parent_tweet']['tweet_timestamp']
                    else tweet_batch['parent_tweet']['tweet_timestamp'],
                    tweet_batch['parent_tweet']['who_twitted_handlename'],
                    tweet_batch['parent_tweet']['who_twitted_user_url'],
                    tweet_batch['parent_tweet']['who_twitted_user_bio'],
                    tweet_batch['parent_tweet']['who_twitted_user_location'],
                    tweet_batch['parent_tweet']['who_twitted_user_website_url'],
                    str(tweet_batch['parent_tweet']['who_twitted_user_join_date'])
                    if tweet_batch['parent_tweet']['who_twitted_user_join_date']
                    else tweet_batch['parent_tweet']['who_twitted_user_join_date'],
                    str(tweet_batch['child_tweets'][0]['scraping_date']),
                    tweet_batch['child_tweets'][0]['who_twitted_handlename'],
                    tweet_batch['child_tweets'][0]['who_twitted_user_url'],
                    tweet_batch['child_tweets'][0]['tweet_body'],
                    tweet_batch['child_tweets'][0]['who_twitted_user_bio'],
                    tweet_batch['child_tweets'][0]['who_twitted_user_website_url'],
                    str(tweet_batch['child_tweets'][0]['who_twitted_user_join_date'])
                    if tweet_batch['child_tweets'][0]['who_twitted_user_join_date']
                    else tweet_batch['child_tweets'][0]['who_twitted_user_join_date'],
                ]
            )
        else:
            values.append(
                [
                    tweet_batch['parent_tweet']['tweet_keyword'],
                    tweet_batch['parent_tweet']['tweet_url'],
                    tweet_batch['parent_tweet']['tweet_body'],
                    str(tweet_batch['parent_tweet']['tweet_timestamp'])
                    if tweet_batch['parent_tweet']['tweet_timestamp']
                    else tweet_batch['parent_tweet']['tweet_timestamp'],
                    tweet_batch['parent_tweet']['who_twitted_handlename'],
                    tweet_batch['parent_tweet']['who_twitted_user_url'],
                    tweet_batch['parent_tweet']['who_twitted_user_bio'],
                    tweet_batch['parent_tweet']['who_twitted_user_location'],
                    tweet_batch['parent_tweet']['who_twitted_user_website_url'],
                    str(tweet_batch['parent_tweet']['who_twitted_user_join_date'])
                    if tweet_batch['parent_tweet']['who_twitted_user_join_date']
                    else tweet_batch['parent_tweet']['who_twitted_user_join_date'],
                    str(tweet_batch['parent_tweet']['scraping_date']),
                ]
            )

            for _ in range(6):
                values[0].append('')

            return values

        for child_tweet_data in tweet_batch['child_tweets'][1:]:
            child_tweet_parsed_entry = ['' for _ in range(10)]
            child_tweet_parsed_entry.extend(
                [
                    str(child_tweet_data['scraping_date']),
                    child_tweet_data['who_twitted_handlename'],
                    child_tweet_data['who_twitted_user_url'],
                    child_tweet_data['tweet_body'],
                    child_tweet_data['who_twitted_user_bio'],
                    child_tweet_data['who_twitted_user_website_url'],
                    str(child_tweet_data['who_twitted_user_join_date']) if
                    child_tweet_data['who_twitted_user_join_date']
                    else child_tweet_data['who_twitted_user_join_date'],
                ]
            )
            values.append(
                child_tweet_parsed_entry
            )

        return values

    def write_to_worksheet(
            self,
            worksheet: Worksheet,
            rows: list,
    ) -> None:
        try:
            worksheet.insert_rows(
                values=rows,
                row=2,
            )
        except Exception:
            return self.write_to_worksheet(
                worksheet=worksheet,
                rows=rows,
            )

    def get_keywords_from_spreadsheet(self) -> list:
        try:
            keywords = list()

            for keyword in self._spreadsheet.values_get('A:B')['values']:
                keywords.extend(keyword)

            return keywords
        except BaseException as e:
            self.logger.info('Exception when writing to Google spreadsheet')
            raise e

    def __read_creds(self) -> dict:
        try:
            path = self.main_path + 'google_credentials.json' \
                if self.main_path else './google_credentials.json'
            return service_account.Credentials.from_service_account_file(
                path,
                scopes=self.SCOPES,
            )
        except BaseException as e:
            self.logger.exception('Cannot read the google credentials!')
            raise e

    def _get_worksheet(self, title: str) -> Tuple[Worksheet, bool]:
        is_new = False

        for existing_worksheet in self._spreadsheet.worksheets():
            if existing_worksheet.title == title:
                return existing_worksheet, is_new

        is_new = True
        return self._spreadsheet.add_worksheet(title, rows=100, cols=20), is_new

    @staticmethod
    def split_list(
            list_to_split: list,
            batch_size: int = 1000,
    ) -> list:
        splitted_list = list()

        for step in range(0, len(list_to_split), batch_size):
            splitted_list.append(list_to_split[step:step + batch_size])

        return splitted_list[::-1]
