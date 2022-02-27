"""Pipeline to drop items which have been already persisted to the database."""
from typing import Set

import scrapy  # type: ignore
import scrapy.crawler  # type: ignore
from loguru import logger
from scrapy.exceptions import DropItem  # type: ignore

from real_estate_scrapers.database import DatabaseHandler, db_handler
from real_estate_scrapers.models import RealEstate, RealEstateDBItem


class DuplicatesPipeline:
    """
    Pipeline to drop items which have been already persisted to the database.
    Only considers items which have been persisted to the database before opening the current spider.
    """

    def __init__(self, handler: DatabaseHandler):
        self.handler = handler
        self.item_urls_seen: Set[str] = self.__fetch_scraped_item_urls()

    def __fetch_scraped_item_urls(self) -> Set[str]:
        logger.debug("Fetching already scraped item urls for DuplicatesPipeline...")
        session = self.handler.create_session()
        urls = session.query(RealEstateDBItem.scrape_metadata_url).all()
        session.close()
        return {url[0] for url in urls}

    @classmethod
    def from_crawler(cls, _: scrapy.crawler.Crawler) -> "DuplicatesPipeline":
        """Create an instance of the pipeline from a crawler."""
        logger.debug("Creating DuplicatesPipeline...")
        return cls(handler=db_handler)

    def open_spider(self, _: scrapy.Spider) -> None:
        """
        Hook called when the spider is opened.

        Args:
            _: The spider that is being opened.
        """
        logger.debug("DuplicatesPipeline open_spider hook...")

    def close_spider(self, _: scrapy.Spider) -> None:
        """
        Hook called when the spider is closed. Closes the database connection.

        Args:
            _: The spider that is being closed.
        """
        logger.debug("DuplicatesPipeline close_spider hook...")
        self.handler.close()

    def process_item(self, item: RealEstate, _: scrapy.Spider) -> RealEstate:
        """
        Hook called for each item in the pipeline.
        Checks whether the item has already been persisted to the database &
        drops the item if it has.

        Args:
            item: the item to be checked for being a duplicate.
            _: the spider that is processing the item.
        """
        if item["scrape_metadata"]["url"] in self.item_urls_seen:
            raise DropItem(f"Real estate item already scraped in a previous run: {item['scrape_metadata']['url']}")
        return item
