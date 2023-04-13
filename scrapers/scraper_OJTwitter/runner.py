from core.sync_client.publisher import Publisher
from scrapers.scraper_OJTwitter.config import *
from scrapers.scraper_OJTwitter.db.db import Database


def run_scraper(
        keyword: str,
        session_id: int = None,
):
    if not session_id:
        db = Database()
        session_id = db.create_session()

    task = {
        'request':
            {
                'callback': 'start',
                'keyword': keyword,
                'session_id': session_id,
            },
    }
    publisher = Publisher()
    publisher.publish(
        task=task,
        destination=SERVICE_NAME,
    )


if __name__ == '__main__':
    run_scraper(
        keyword='ArKit'
    )
