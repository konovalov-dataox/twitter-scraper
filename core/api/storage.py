from core.api.client import BaseAcceleratorAsyncClient
from core.messages.storage import StorageRequestBody, StorageTaskMessageBody
from typing import TYPE_CHECKING
from settings import RMQ_STORAGE

if TYPE_CHECKING:
    from core.async_client.async_client import AsyncAcceleratorIncomingMessage


class Data(StorageRequestBody):
    pass


class AsyncStorageClient(BaseAcceleratorAsyncClient):
    SERVICE_NAME = RMQ_STORAGE

    async def send(self, task: StorageTaskMessageBody, context_message: 'AsyncAcceleratorIncomingMessage',
                   rate_limit_tag: str = ''):
        delattr(task, 'callback')
        delattr(task, 'meta')
        delattr(task, 'on_error_callback')
        await self.context.send_task(context_message, task.json(), self.SERVICE_NAME, rate_limit_tag)
