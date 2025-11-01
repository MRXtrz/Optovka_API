BOT_NAME = 'optoviki'

SPIDER_MODULES = ['parser_service.spiders']
NEWSPIDER_MODULE = 'parser_service.spiders'

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
ROBOTSTXT_OBEY = False

DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800,
}

SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = '/usr/bin/chromedriver'
SELENIUM_HEADLESS = True
SELENIUM_DRIVER_ARGUMENTS = [
    '--headless',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
]
SELENIUM_WINDOW_SIZE = '1920,1080'

CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 2
DOWNLOAD_TIMEOUT = 30
RETRY_TIMES = 2

LOG_LEVEL = 'INFO'
LOG_FILE = 'spider.log'
DUPEFILTER_DEBUG = True
