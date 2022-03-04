"""Real Estate Spider to handle the actual crawling of various websites"""
from typing import Any, Dict, Generator, List, Optional

import scrapy  # type: ignore
from loguru import logger
from scrapy_poet import callback_for  # type: ignore

from real_estate_scrapers.concrete_items import get_scrapy_poet_overrides, get_start_urls
from real_estate_scrapers.items import RealEstateListPage, RealEstatePage


class RealEstateSpider(scrapy.Spider):  # type: ignore
    """Real Estate Spider to handle the actual crawling of various websites"""

    name = "real_estate_spider"
    all_urls: List[str] = get_start_urls()
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
        urls_to_consider: List[str] = RealEstateSpider.all_urls
        if self.only_domain is not None:
            logger.debug(f"Only crawling pages from {self.only_domain}")
            urls_to_consider = [url for url in urls_to_consider if self.only_domain in url]
        for url in urls_to_consider:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, page: RealEstateListPage):  # type: ignore
        for url in page.real_estate_urls:
            yield response.follow(url, callback_for(RealEstatePage))
