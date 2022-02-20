"""Real Estate Spider to handle the actual crawling of various websites"""
from typing import List

import scrapy  # type: ignore
from scrapy_poet import callback_for  # type: ignore

from real_estate_scrapers.concrete_items import (
    get_scrapy_poet_overrides,
    get_start_urls,
)
from real_estate_scrapers.items import RealEstateListPage, RealEstatePage


class RealEstateSpider(scrapy.Spider):  # type: ignore
    """Real Estate Spider to handle the actual crawling of various websites"""

    name = "real_estate_spider"
    start_urls: List[str] = get_start_urls()
    custom_settings = {"SCRAPY_POET_OVERRIDES": get_scrapy_poet_overrides()}

    def parse(self, response, page: RealEstateListPage):  # type: ignore
        yield from response.follow_all(
            page.real_estate_urls, callback_for(RealEstatePage)
        )
