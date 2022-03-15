"""Defines the Page Object Model for Real Estates to be scraped"""
from datetime import datetime
from typing import List, Optional

from web_poet import ItemWebPage, WebPage  # type: ignore

from real_estate_scrapers.format_checker import FormatChecker
from real_estate_scrapers.models import (
    EnergyData,
    EPCData,
    ListingType,
    Location,
    Price,
    RealEstate,
    RealEstateMetadata,
    ScrapeMetadata,
)


class RealEstateListPage(WebPage):  # type: ignore
    """Page Object Model for Real Estate List Pages"""

    @staticmethod
    def should_use_selenium() -> bool:
        """
        Returns: ``True`` if the page should be scraped
                 using Selenium.
        """
        return False

    @staticmethod
    def domain() -> str:
        """
        Returns: The base domain of the website
                 from which the scraping should take place
        """
        raise NotImplementedError

    @staticmethod
    def start_urls() -> List[str]:
        """
        Returns: The urls of the website
        from which ``RealEstatePage``s are scraped
        """
        raise NotImplementedError

    @property
    def real_estate_urls(self) -> List[str]:
        """
        Returns: A list of urls to be used
                 to scrape ``RealEstatePage`` objects
        """
        raise NotImplementedError


class RealEstatePage(ItemWebPage):  # type: ignore
    """Defines the Page Object Model for Real Estates to be scraped"""

    # Object to access utility functions
    format_checker = FormatChecker()

    @property
    def fmtckr(self) -> FormatChecker:
        """
        Returns: A ``FormatChecker`` object to facilitate raw string checking.
        """
        return RealEstatePage.format_checker

    @property
    def country(self) -> str:
        """
        Returns: The ISO 3166-1 alpha-3 country code
                 of the real estate item's location.
        """
        raise NotImplementedError

    @property
    def city(self) -> str:
        """
        Returns: The city where the real estate item is located
        """
        raise NotImplementedError

    @property
    def zip_code(self) -> str:
        """
        Returns: The ZIP code of the real estate item's location
        """
        raise NotImplementedError

    @property
    def listing_type(self) -> ListingType:
        """
        Returns: The ZIP code of the real estate item's location
        """
        raise NotImplementedError

    @property
    def area(self) -> Optional[float]:
        """
        Returns: The area of the real estate item in square meters
        """
        raise NotImplementedError

    @property
    def price_amount(self) -> Optional[float]:
        """
        Returns: The price of the real estate item
        """
        raise NotImplementedError

    @property
    def price_unit(self) -> str:
        """
        Returns: The currency in which the real estate item is priced
        """
        raise NotImplementedError

    @property
    def heating_demand(self) -> Optional[EnergyData]:
        """
        Returns: The heating demand ``EnergyData``
                 of the real estate item in kWh/(m²·a)
        """
        raise NotImplementedError

    @property
    def energy_efficiency(self) -> Optional[EnergyData]:
        """
        Returns: The energy efficiency ``EnergyData``
                 of the real estate item
        """
        raise NotImplementedError

    @property
    def epc_pdf_url(self) -> Optional[str]:
        """
        Returns: URL to the EPC PDF of the real estate item
        """
        raise NotImplementedError

    @property
    def epc_issued_date(self) -> Optional[datetime]:
        """
        Returns: The date on which the EPC was issued
        """
        raise NotImplementedError

    @property
    def date_of_building(self) -> Optional[datetime]:
        """
        Returns: The date on which the real estate item was built
        """
        raise NotImplementedError

    @property
    def object_type(self) -> str:
        """
        Returns: The type of the real estate item
        """
        raise NotImplementedError

    def to_item(self) -> RealEstate:
        return RealEstate(
            location=Location(country=self.country, city=self.city, zip_code=self.zip_code),
            listing_type=self.listing_type,
            area=self.area,
            price=self.price_amount and Price(amount=self.price_amount, unit=self.price_unit) or None,
            epc_data=EPCData(
                heating_demand=self.heating_demand,
                energy_efficiency=self.energy_efficiency,
                epc_pdf_url=self.epc_pdf_url,
                epc_issued_date=self.epc_issued_date,
            ),
            item_metadata=RealEstateMetadata(date_built=self.date_of_building, type=self.object_type),
            scrape_metadata=ScrapeMetadata(url=self.url, timestamp=datetime.now().timestamp()),
        )
