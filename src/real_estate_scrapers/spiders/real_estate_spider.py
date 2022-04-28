"""Real Estate Spider to handle the actual crawling of various websites"""
from typing import Any, Dict, Generator, Optional

import scrapy  # type: ignore
import scrapy_selenium  # type: ignore
from loguru import logger
from scrapy_poet import callback_for  # type: ignore

from real_estate_scrapers.concrete_items import get_scrapy_poet_overrides, get_start_url_dict
from real_estate_scrapers.items import RealEstateListPage, RealEstatePage


class RealEstateSpider(scrapy.Spider):  # type: ignore
    """Real Estate Spider to handle the actual crawling of various websites"""

    name = "real_estate_spider"
    custom_settings = {"SCRAPY_POET_OVERRIDES": get_scrapy_poet_overrides()}

    def __init__(self, only_domain: Optional[str] = None, **kwargs: Dict[str, Any]) -> None:
        """
        Initialize the spider.
        Args:
            only_domain: A string optionally passed as ``-a only_domain=<domain>`` via the CLI. If set, the spider
                         will only crawl pages from the specified domain.
            **kwargs: remaining keyword arguments passed to the superclass.
        """
        self.only_domain = only_domain
        super().__init__(**kwargs)

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        for page_cls, urls in get_start_url_dict().items():
            urls_to_consider = [*urls]
            if self.only_domain is not None:
                logger.debug(f"Only crawling pages from {self.only_domain}")
                urls_to_consider = [url for url in urls_to_consider if page_cls.domain() == self.only_domain]
            for url in urls_to_consider:
                if page_cls.should_use_selenium():
                    logger.debug(f"Using selenium for {page_cls.__name__} - {url}")
                    yield scrapy_selenium.SeleniumRequest(url=url, callback=self.parse)
                else:
                    logger.debug(f"Using plain request for {page_cls.__name__} - {url}")
                    yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, page: RealEstateListPage):  # type: ignore
        for url in page.real_estate_urls:
            if page.should_use_selenium():
                # Only works with absolute URLs
                logger.debug(f"Using selenium for {page.__class__.__name__} - {url}")
                yield scrapy_selenium.SeleniumRequest(url=url, callback=callback_for(RealEstatePage))
            else:
                # Works with relative URLs too
                logger.debug(f"Using plain request for {page.__class__.__name__} - {url}")
                yield response.follow(url, callback_for(RealEstatePage))
