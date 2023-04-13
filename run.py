import argparse
import importlib
import re

from core.module import AcceleratorModule
from settings import *

logging.basicConfig(level=LOGGING_LEVEL,
                    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
                    handlers=[logging.StreamHandler()])


class AcceleratorApp:
    def __init__(self):
        self.is_init = None
        self.logger = logging.getLogger('[accelerator]')
        self.parse_args()
        self.modules = None

    def parse_args(self):
        parser = argparse.ArgumentParser(description='Accelerator')
        parser.add_argument('--module', '-m', type=str, help='module name')
        parser.add_argument('--init', '-i', type=bool, help='init')

        args = parser.parse_args()
        self.is_init = args.init

    def run(self):
        module_name = os.environ['ACC_MODULE_NAME']
        accelerator_module = self.init(module_name)
        if not self.is_init:
            self.start(accelerator_module)

    def start(self, accelerator_module: AcceleratorModule):
        self.logger.info(f'Running Accelerator module: {accelerator_module}')
        accelerator_module_instance = accelerator_module.module_class()
        accelerator_module_instance.run()

    def init(self, accelerator_module_name: str):
        self._log_accelerator_setting()
        accelerator_module = self.get_accelerator_module(accelerator_module_name)
        self.logger.info(f'Initializing Accelerator module: {accelerator_module}')
        accelerator_module.init()
        accelerator_module.is_init = False
        accelerator_module = self.get_accelerator_module(accelerator_module_name, reload=True)
        return accelerator_module

    def get_accelerator_module(self, module_name: str, reload: bool = False) -> AcceleratorModule:
        self.load_accelerator_modules('modules', reload)
        self.load_accelerator_modules('scrapers', reload)
        self.modules = AcceleratorModule.modules
        return self.modules.get(module_name)

    @staticmethod
    def load_accelerator_modules(folder_name: str, reload: bool = False):
        for name in os.listdir(folder_name):
            if name.endswith('.py') or name in ['__pycache__', '.DS_Store']:
                continue
            module = importlib.import_module(f'{folder_name}.{name}')
            if reload:
                importlib.reload(module)

    def _log_accelerator_setting(self):
        rmq_url_connection_str = self.__remove_credentials_from_string(
            RMQ_URL_CONNECTION_STR)
        mongo_url_connection_str = self.__remove_credentials_from_string(
            MONGO_URL_CONNECTION_STR)
        accelerator_db_url = self.__remove_credentials_from_string(
            ACCELERATOR_DB_URL)
        redis_host = self.__remove_credentials_from_string(REDIS_HOST)
        self.logger.info(f'STAGE={STAGE}, EXCHANGE={RMQ_EXCHANGE}, '
                         f'RMQ={rmq_url_connection_str}, '
                         f'MONGO={mongo_url_connection_str}, '
                         f'ACC_DB={accelerator_db_url}, '
                         f'REDIS_HOST={redis_host}')

    @staticmethod
    def __remove_credentials_from_string(secure_string: str) -> str:
        return re.sub(r'://.*@', '://...@', secure_string)


# modules = {
#     'fetcher': {'package_name': 'modules.fetcher', 'module_class': 'AsyncFetcher'},
#     'scrapers.DKWS': {'package_name': 'modules.scraper_DKWS', 'module_class': 'ScraperDKWS'},
#     'scrapers.DDW': {'package_name': 'modules.scraper_DDW', 'module_class': 'ScraperDDW'},
#     'notifier': {'package_name': 'modules.notifier', 'module_class': 'Notifier'},
#     'storage_exporter': {'package_name': 'modules.storage_exporter', 'module_class': 'AsyncStorageExporter'},
#     'event_trigger': {'package_name': 'modules.event_trigger', 'module_class': 'AsyncEventTrigger'},
#     'site_links_extractor': {'package_name': 'modules.site_links_extractor', 'module_class': 'AsyncSiteLinksExtractor'},
#     'uploader': {'package_name': 'modules.uploader', 'module_class': 'AsyncUploader'},
#     'scrapers.BC': {'package_name': 'modules.scraper_BC', 'module_class': 'ScraperBC'},
# }

if __name__ == '__main__':
    accelerator_app = AcceleratorApp()
    accelerator_app.run()
