import json

from core.RMQ.RMQ import RMQ
from settings import *


class Publisher:
    def __init__(self):
        self.rmq = RMQ(RMQ_URL_CONNECTION_STR)

    def __call__(self, task: dict, destination: str):
        self.publish(task, destination)

    def _publish(self, message: str, headers: dict):
        properties = self.rmq.properties({
            'headers': headers,
            'delivery_mode': DELIVERY_MODE
        })
        self.rmq.publish(
            exchange=RMQ_EXCHANGE,
            routing_key=headers['to'],
            body=message,
            properties=properties
        )

    def publish(self,
                task: dict,
                destination: str,
                *,
                session_id: str = 'publisher',
                from_name: str = RMQ_EXCHANGE + '.publisher',
                rate_limit_tag: str = ''):
        message = json.dumps(task)
        headers = self.create_headers(destination, session_id,
                                      from_name, rate_limit_tag)
        self._publish(message, headers)

    @staticmethod
    def create_headers(destination: str, session_id: str,
                       from_name: str, rate_limit_tag: str) -> dict:
        return {
            'from': from_name,
            'to': destination,
            'type': 'TASK',
            'session_id': session_id,
            'rate_limit_tag': rate_limit_tag
        }
