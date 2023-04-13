import json
from abc import ABC

from core.async_client.async_client import AcceleratorAsyncClient, AsyncAcceleratorIncomingMessage
from core.messages.error import ErrorMessageBody
from core.messages.types import MessageType


class AsyncScraper(AcceleratorAsyncClient, ABC):
    async def process_message(self, message: AsyncAcceleratorIncomingMessage):
        message_body = json.loads(message.body)
        if message.headers.message_type == MessageType.ERROR:
            error_message = ErrorMessageBody(**message_body)
            error_message_body = json.loads(error_message.message_body)
            assert 'on_error_callback' in error_message_body, '"on_error_callback" not in error message body'
            on_error_callback = error_message_body['on_error_callback']
            self.logger.info(
                f'Scraper receive error message: on_error_callback="{on_error_callback}", {repr(message)}'
            )
            await getattr(self, on_error_callback)(message, message_body)
        else:
            assert 'callback' in message_body['request'], '"callback" not in message body'
            callback = message_body['request']['callback']
            self.logger.info(
                f'Scraper receive message: callback="{callback}", {repr(message)}'
            )
            await getattr(self, callback)(message, message_body)
