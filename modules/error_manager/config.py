from settings import *

TABLE_PREFIX = 'error_log_'
SERVICE_NAME = RMQ_ERROR_MANAGER
PREFETCH_COUNT = int(os.environ.get('PREFETCH_COUNT', 1))
