"""Pipeline to persist items to a Postgres database."""
import scrapy  # type: ignore
import scrapy.crawler  # type: ignore
from loguru import logger

from real_estate_scrapers.database import DatabaseHandler, db_handler
from real_estate_scrapers.models import RealEstate, RealEstateDBItem


class PostgresPipeline:
    """Pipeline to persist items to a Postgres database."""

    # Batches of items to persist to the database
    batch_size = 100

    @classmethod
    def from_crawler(cls, _: scrapy.crawler.Crawler) -> "PostgresPipeline":
        """Create an instance of the pipeline from a crawler."""
        logger.debug("Creating PostgresPipeline...")
        return cls(handler=db_handler)

    def __init__(self, handler: DatabaseHandler):
        self.num_items = 0
        self.handler = handler
        self.session = self.handler.create_session()

    def open_spider(self, _: scrapy.Spider) -> None:
        """
        Hook called when the spider is opened.

        Args:
            _: The spider that is being opened.
        """
        logger.debug("PostgresPipeline open_spider hook...")

    def close_spider(self, _: scrapy.Spider) -> None:
        """
        Hook called when the spider is closed. Closes the database connection.

        Args:
            _: The spider that is being closed.
        """
        logger.debug("PostgresPipeline close_spider hook...")
        # Commit the remaining items
        self.session.commit()
        self.session.close_all()
        self.handler.close()

    def process_item(self, item: RealEstate, _: scrapy.Spider) -> RealEstate:
        """
        Hook called for each item in the pipeline. Persists the item to the database.

        Args:
            item: the item to persist.
            _: the spider that is processing the item.
        """
        self.num_items += 1
        db_item = RealEstateDBItem.from_dict(item)
        self.session.add(db_item)
        # Commit every 100 items
        if self.num_items % PostgresPipeline.batch_size == 0:
            self.session.commit()
        return item
