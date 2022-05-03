"""Real Estate Spider to handle the actual crawling of various websites"""
from typing import Any, Dict, Generator, Optional

import scrapy  # type: ignore
import scrapy.http  # type: ignore
import scrapy_selenium  # type: ignore
from loguru import logger
from scrapy_poet import callback_for  # type: ignore

from real_estate_scrapers.concrete_items import get_scrapy_poet_overrides, get_start_url_dict
from real_estate_scrapers.items import RealEstateHomePage, RealEstateListPage, RealEstatePage


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
        """
        Custom method to supply the spider with start requests from ``RealEstateHomePage`` implementations.
        Yields selenium requests if the ``RealEstateHomePage`` implementation is configured to use selenium.

        Returns: a generator of requests to start the spider.
        """
        for home_page_cls, urls in get_start_url_dict().items():
            urls_to_consider = [*urls]
            if self.only_domain is not None:
                logger.debug(f"Only crawling pages from {self.only_domain}")
                urls_to_consider = [url for url in urls_to_consider if home_page_cls.domain() == self.only_domain]
            for url in urls_to_consider:
                if home_page_cls.should_use_selenium():
                    logger.debug(f"Using selenium for {home_page_cls.__name__} - {url}")
                    yield scrapy_selenium.SeleniumRequest(
                        url=url, callback=self.parse_home_page, **home_page_cls.request_kwargs()
                    )
                else:
                    logger.debug(f"Using plain request for {home_page_cls.__name__} - {url}")
                    yield scrapy.Request(url=url, callback=self.parse_home_page, **home_page_cls.request_kwargs())

    def parse_home_page(self, response: scrapy.http.Response, page: RealEstateHomePage):  # type: ignore
        """
        Callback to extract urls from a ``RealEstateHomePage`` by invoking ``real_estate_list_urls``.
        Yields requests to parse paginated``RealEstateListPage``s from the extracted urls.

        Args:
            response: the response for a request yielded by ``start_requests``.
            page: the ``RealEstateHomePage`` object into which the response was injected.

        Returns: a generator of requests to parse ``RealEstateListPage``s.

        """
        for url in page.real_estate_list_urls:
            if page.should_use_selenium():
                yield scrapy_selenium.SeleniumRequest(url=url, callback=self.parse_pagination, **page.request_kwargs())
            else:
                yield response.follow(url=url, callback=self.parse_pagination, **page.request_kwargs())

    def parse_pagination(self, response: scrapy.http.Response, page: RealEstateListPage):  # type: ignore
        """
        Callback to extract paginated ``RealEstateListPage`` urls by invoking ``real_estate_list_urls``.
        Yields requests to parse paginated``RealEstateListPage``s from the extracted urls.

        Args:
            response: the response for a request yielded by ``start_requests``.
            page: the ``RealEstateHomePage`` object into which the response was injected.

        Returns: a generator of requests to parse ``RealEstateListPage``s.

        """
        for url in page.real_estate_list_urls_paginated:
            if page.parent_page_type().should_use_selenium():
                yield scrapy_selenium.SeleniumRequest(url=url, callback=self.parse, **page.request_kwargs())
            else:
                yield response.follow(url=url, callback=self.parse, **page.request_kwargs())

    def parse(self, response: scrapy.http.Response, page: RealEstateListPage):  # type: ignore
        """
        Callback to extract urls from a ``RealEstateListPage`` by invoking ``real_estate_urls``.
        Yields requests to parse ``RealEstatePage``s from the extracted urls,
        which will be the actual items we are collecting.

        Args:
            response: the response for a request yielded by ``parse_home_page``
            page: the ``RealEstateListPage`` object into which the response was injected.

        Returns: a generator of requests to parse ``RealEstatePage``s.
        """
        for url in page.real_estate_urls:
            if page.parent_page_type().should_use_selenium():
                yield scrapy_selenium.SeleniumRequest(
                    url=url, callback=callback_for(RealEstatePage), **page.request_kwargs()
                )
            else:
                yield response.follow(url=url, callback=callback_for(RealEstatePage), **page.request_kwargs())
