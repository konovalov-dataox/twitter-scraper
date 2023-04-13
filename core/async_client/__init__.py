from setup_requirements import setup

requirements = ['aio_pika', 'redis']
setup(requirements)

from .async_client import AcceleratorAsyncClient
