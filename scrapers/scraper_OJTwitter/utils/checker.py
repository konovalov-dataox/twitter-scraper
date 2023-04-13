import datetime
import json
import re
import time

import requests

from settings import RMQ_URL_CONNECTION_STR as RMQ_URL
from scrapers.scraper_OJTwitter.utils.logger import logging


class Checker:

    def __init__(self):
        self.logger = logging.getLogger('[CHEKER]')

    def check_if_scraping_process_completed(
            self,
            queue_names_list: list,
    ) -> bool:
        server_ip = requests.get('https://api.ipify.org').text
        http_port = '15671'
        self.logger.info(f'RMQ_URL amqp: {RMQ_URL}')
        amqp_port = re.findall(r':(\d+)/?', RMQ_URL)[0]
        prefix = RMQ_URL.replace('amqp', 'http').replace(amqp_port, http_port).split('/?')[0]
        prefix = prefix.replace('@rabbitmq:', f'@{server_ip}:')
        url = f'{prefix}/api/queues/%2f/'
        self.logger.info(f'RMQ_URL: {url}')

        for _ in range(3):

            response = requests.get(url)
            data = json.loads(response.text)

            for queue in data:

                if queue.get('name') in queue_names_list and queue.get('messages', 0) > 0:
                    return False

            time.sleep(10)

        self.logger.info(f'No more messages in the queues. Time: {datetime.datetime.utcnow()}')
        return True

    def check(
            self,
            queue_names_list: list,
    ) -> None:
        current_day = datetime.datetime.utcnow().strftime('%Y-%m-%d')

        try:
            scraping_process_completed = self.check_if_scraping_process_completed(queue_names_list)
        except Exception:
            self.logger.info('Exception while checking the completion of the scraping process. Retry')
            scraping_process_completed = False

        if not scraping_process_completed:
            self. logger.info(f' [{current_day}]SCRAPING STATUS: IN PROCESS.')
            time.sleep(600)
            self.check(queue_names_list)
            return

        self.logger.info(f' [{current_day}]SCRAPING STATUS: COMPLETED.')
