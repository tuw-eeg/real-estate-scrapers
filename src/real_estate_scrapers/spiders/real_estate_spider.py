"""Real Estate Spider to handle the actual crawling of various websites"""
from itertools import chain
from typing import List, Type

import scrapy  # type: ignore
from scrapy_poet import callback_for  # type: ignore

from real_estate_scrapers.items import RealEstateListPage, RealEstatePage


class RealEstateSpider(scrapy.Spider):  # type: ignore
    """Real Estate Spider to handle the actual crawling of various websites"""

    name = "real_estate_spider"
    concrete_items: List[Type[RealEstateListPage]] = []

    # Aggregate the urls returned by the ``start_urls`` static method
    # of each concrete ``RealEstateListPage``
    start_urls: List[str] = list(
        chain.from_iterable(
            [getattr(item, "start_urls")() for item in concrete_items]
        )
    )

    # Configuring different page objects for different domains
    custom_settings = {
        "SCRAPY_POET_OVERRIDES": {
            "toscrape.com": {
                RealEstateListPage: RealEstateListPage,
                RealEstatePage: RealEstatePage,
            },
        },
    }

    def parse(self, response, page: RealEstateListPage):  # type: ignore
        yield from response.follow_all(
            page.real_estate_urls, callback_for(RealEstatePage)
        )
