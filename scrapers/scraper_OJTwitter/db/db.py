import datetime
from typing import List

from sqlalchemy import create_engine, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from scrapers.scraper_OJTwitter.config import DB_CONNECTION_URL
from scrapers.scraper_OJTwitter.db.models import Base, ParentTweet, ChildTweet, Session as ScraperSession
from scrapers.scraper_OJTwitter.utils.logger import logging


class Database:

    def __init__(self):
        self.engine = create_engine(DB_CONNECTION_URL)
        Base.metadata.create_all(self.engine)
        self.session = Session(bind=self.engine)
        self.logger = logging.getLogger('[DATABASE]')

    def save_parent_tweet(
            self,
            parent_tweet: ParentTweet,
    ) -> None:
        base_parent_tweet = self.session.query(ParentTweet).filter_by(
            tweet_id=parent_tweet.tweet_id,
        ).first()

        if not base_parent_tweet:
            self.session.add(parent_tweet)
            self.commit()
            self.logger.info(
                msg=f'Saved parent tweet. '
                    f'Tweet id: {parent_tweet.tweet_id} '
                    f'Tweet url: {parent_tweet.tweet_url} ',
            )

    def save_child_tweet(
            self,
            child_tweet: ChildTweet,
    ) -> None:
        base_child_tweet = self.session.query(ChildTweet).filter(
            and_(
                ChildTweet.tweet_id == child_tweet.tweet_id,
                ChildTweet.parent_tweet_id == child_tweet.parent_tweet_id,
            ),
        ).first()

        if not base_child_tweet:
            self.session.add(child_tweet)
            self.commit()
            self.logger.info(
                msg=f'Saved child tweet. '
                    f'Tweet id: {child_tweet.tweet_id} '
                    f'Tweet url: {child_tweet.tweet_url} ',
            )

    def get_min_date(
            self,
            keyword: str,
    ) -> datetime.datetime:
        min_date = self.session \
            .query(ParentTweet.tweet_timestamp) \
            .filter_by(tweet_keyword=keyword) \
            .order_by(
            ParentTweet.tweet_timestamp.desc()
        ).first()

        if min_date:
            min_date, = min_date

        return min_date - datetime.timedelta(days=1) if min_date \
            else datetime.datetime.strptime('2006-01-01', '%Y-%m-%d')

    def create_session(self) -> int:
        session = ScraperSession(
            creation_date=datetime.datetime.utcnow(),
        )
        self.session.add(session)
        self.commit()
        return session.session_id

    def get_data_by_session(
            self,
            session_id: int,
    ) -> dict:
        data = dict()
        session_keywords = self.session \
            .query(ParentTweet.tweet_keyword) \
            .filter_by(session_id=session_id) \
            .distinct() \
            .all()

        for keyword in session_keywords:
            keyword, = keyword
            data[keyword] = list()
            parent_tweets: List[ParentTweet] = self.session \
                .query(ParentTweet) \
                .filter(
                and_(
                    ParentTweet.session_id == session_id,
                    ParentTweet.tweet_keyword == keyword,
                ),
            ) \
                .order_by(ParentTweet.tweet_timestamp.desc()) \
                .all()

            for parent_tweet in parent_tweets:
                tweet_dict = dict()
                tweet_dict['parent_tweet'] = {
                    'tweet_keyword': parent_tweet.tweet_keyword,
                    'tweet_url': parent_tweet.tweet_url,
                    'tweet_body': parent_tweet.tweet_body,
                    'tweet_timestamp': parent_tweet.tweet_timestamp,
                    'who_twitted_handlename': parent_tweet.who_twitted_user_handlename,
                    'who_twitted_user_url': parent_tweet.who_twitted_user_url,
                    'who_twitted_user_bio': parent_tweet.who_twitted_user_bio,
                    'who_twitted_user_location': parent_tweet.who_twitted_user_location,
                    'who_twitted_user_website_url': parent_tweet.who_twitted_user_website_url,
                    'who_twitted_user_join_date': parent_tweet.who_twitted_user_join_date,
                    'scraping_date': parent_tweet.scraping_date,
                }
                tweet_dict['child_tweets'] = self.get_child_tweets_data(
                    session_id=session_id,
                    parent_tweet_id=parent_tweet.tweet_id,
                )
                data[keyword].append(tweet_dict)

        return data

    def get_child_tweets_data(
            self,
            session_id: int,
            parent_tweet_id: int,
    ) -> list:
        child_tweets = list()
        child_tweets_from_db: List[ChildTweet] = self.session.query(ChildTweet).filter(
            and_(
                ChildTweet.session_id == session_id,
                ChildTweet.parent_tweet_id == parent_tweet_id,
            ),
        ).all()

        for child_tweet in child_tweets_from_db:
            tweet_dict = {
                'who_twitted_handlename': child_tweet.who_twitted_user_handlename,
                'who_twitted_user_url': child_tweet.who_twitted_user_url,
                'tweet_body': child_tweet.tweet_body,
                'who_twitted_user_bio': child_tweet.who_twitted_user_bio,
                'who_twitted_user_website_url': child_tweet.who_twitted_user_website_url,
                'who_twitted_user_join_date': child_tweet.who_twitted_user_join_date,
                'scraping_date': child_tweet.scraping_date,
            }
            child_tweets.append(tweet_dict)

        return child_tweets

    def commit(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as e:
            self.logger.error(e)
            self.session.rollback()
        except Exception as e:
            self.session.rollback()
            raise e
