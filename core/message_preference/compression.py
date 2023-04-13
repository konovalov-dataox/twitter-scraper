import base64
import json
import zlib
from typing import Dict, Union

from core.messages.message import Message


class MessageCompressorHandler:

    def compress_message(self, message: Message) -> Message:
        json_message_body = message.get_body_as_json()
        body = self.compress_message_body(json_message_body)
        message.body = body

        return message

    def decompress_message(self, message: Message) -> Message:
        try:
            compressed_body = message.body
            decompress_body = self.decompress_message_body(compressed_body)
            message.body = decompress_body
        except Exception:
            print(f'Can not decompress message {message}')

        return message

    @staticmethod
    def compress_message_body(origin_body: Union[Dict, str], level=-1) -> str:
        data = origin_body
        if isinstance(origin_body, dict):
            data = json.dumps(origin_body).encode('utf-8')

        if isinstance(origin_body, str):
            data = origin_body.encode('utf-8')

        return base64.b64encode(zlib.compress(data, level))

    @staticmethod
    def decompress_message_body(compressed_body: str) -> str:
        compressed_data = base64.b64decode(compressed_body)
        data = zlib.decompress(compressed_data)
        return data.decode('utf-8')
