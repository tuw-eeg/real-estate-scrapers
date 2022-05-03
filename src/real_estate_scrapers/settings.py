# pylint: disable-all
# type: ignore
from shutil import which

from fake_useragent import UserAgent

BOT_NAME = "real_estate_scrapers"

SPIDER_MODULES = ["real_estate_scrapers.spiders"]
NEWSPIDER_MODULE = "real_estate_scrapers.spiders"

# Ignore robots.txt rules
ROBOTSTXT_OBEY = False
USER_AGENT = UserAgent(verify_ssl=False).firefox

SELENIUM_DRIVER_NAME = "firefox"
SELENIUM_DRIVER_EXECUTABLE_PATH = which("geckodriver")
SELENIUM_DRIVER_ARGUMENTS = ["-headless"]

DOWNLOADER_MIDDLEWARES = {
    # Enabling scrapy_poet downloader middleware so that
    # the ``page`` kwargs get injected into the ``parse`` method automatically
    "scrapy_poet.InjectionMiddleware": 543,
    # Use SeleniumMiddleware to handle JavaScript
    "scrapy_selenium.SeleniumMiddleware": 800,
}

ITEM_PIPELINES = {
    # Skip duplicate items
    "real_estate_scrapers.pipelines.DuplicatesPipeline": 300,
    # Persist scraped items to the database
    "real_estate_scrapers.pipelines.PostgresPipeline": 400,
}

# Maximum concurrent requests performed by Scrapy
CONCURRENT_REQUESTS = 64

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 1.0
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16
DOWNLOAD_TIMEOUT = 30

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

AUTOTHROTTLE_ENABLED = False
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 0.5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = True

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
