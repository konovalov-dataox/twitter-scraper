from sqlalchemy import Column, BigInteger, String, DateTime, func, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ParentTweet(Base):
    __tablename__ = 'parent_tweet'
    tweet_id = Column(
        BigInteger,
        unique=True,
        index=True,
    )
    session_id = Column(
        BigInteger,
        nullable=False,
        index=True,
    )
    tweet_url = Column(
        String,
        unique=True,
        nullable=False,
        primary_key=True,
    )
    tweet_keyword = Column(
        String,
    )
    tweet_body = Column(
        String,
    )
    tweet_timestamp = Column(
        DateTime,
        nullable=False,
    )
    who_twitted_user_handlename = Column(
        String,
    )
    who_twitted_user_url = Column(
        String,
    )
    who_twitted_user_bio = Column(
        String,
    )
    who_twitted_user_location = Column(
        String,
    )
    who_twitted_user_website_url = Column(
        String,
    )
    who_twitted_user_join_date = Column(
        DateTime,
        nullable=True,
    )
    scraping_date = Column(
        DateTime,
        nullable=False,
        default=func.utcnow(),
    )


class ChildTweet(Base):
    __tablename__ = 'child_tweet'
    tweet_id = Column(
        BigInteger,
        unique=True,
        nullable=False,
        primary_key=True,
    )
    parent_tweet_id = Column(
        BigInteger,
    )
    session_id = Column(
        BigInteger,
        nullable=False,
        index=True,
    )
    tweet_url = Column(
        String,
        unique=True,
        nullable=False,
        primary_key=True,
    )
    tweet_keyword = Column(
        String,
    )
    tweet_body = Column(
        String,
    )
    tweet_timestamp = Column(
        DateTime,
        nullable=False,
    )
    who_twitted_user_handlename = Column(
        String,
    )
    who_twitted_user_url = Column(
        String,
    )
    who_twitted_user_bio = Column(
        String,
    )
    who_twitted_user_location = Column(
        String,
    )
    who_twitted_user_website_url = Column(
        String,
    )
    who_twitted_user_join_date = Column(
        DateTime,
        nullable=True,
    )
    scraping_date = Column(
        DateTime,
        nullable=False,
        default=func.utcnow(),
    )

    __table_args__ = (
        UniqueConstraint(
            'parent_tweet_id',
            'tweet_id',
            name='child_tweet_unique',
        ),
    )


class Session(Base):
    __tablename__ = 'session'
    session_id = Column(
        BigInteger,
        unique=True,
        nullable=False,
        primary_key=True,
    )
    creation_date = Column(
        DateTime,
        nullable=False,
        default=func.utcnow(),
    )
