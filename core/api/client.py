from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.messages.task import TaskMessageBody

if TYPE_CHECKING:
    from core.async_client import AcceleratorAsyncClient


class BaseAcceleratorAsyncClient(ABC):
    def __init__(self, context: 'AcceleratorAsyncClient'):
        self.context: 'AcceleratorAsyncClient' = context

    @abstractmethod
    async def send(self, task: TaskMessageBody, context_message: 'AsyncAcceleratorIncomingMessage',
                   rate_limit_tag: str = '', priority: int = 0):
        pass
