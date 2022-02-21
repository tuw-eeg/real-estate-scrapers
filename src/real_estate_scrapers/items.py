"""Defines the Page Object Model for Real Estates to be scraped"""
from datetime import datetime
from typing import List, Optional

from web_poet import ItemWebPage, WebPage  # type: ignore

from real_estate_scrapers.models import (
    EnergyData,
    ListingType,
    Location,
    Price,
    RealEstate,
    ScrapeMetadata,
)


class RealEstateListPage(WebPage):  # type: ignore
    """Page Object Model for Real Estate List Pages"""

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
    def area(self) -> float:
        """
        Returns: The area of the real estate item in square meters
        """
        raise NotImplementedError

    @property
    def price_amount(self) -> float:
        """
        Returns: The price of the real estate item
        """
        raise NotImplementedError

    @property
    def price_currency(self) -> str:
        """
        Returns: The currency in which the real estate item is priced
        """
        raise NotImplementedError

    @property
    def epc_label(self) -> Optional[str]:
        """
        Returns: The EPC Label (Energy class) of the real estate item
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

    def to_item(self) -> RealEstate:
        return RealEstate(
            location=Location(
                country=self.country, city=self.city, zip_code=self.zip_code
            ),
            listing_type=self.listing_type,
            area=self.area,
            price=Price(amount=self.price_amount, currency=self.price_currency),
            heating_demand=self.heating_demand,
            energy_efficiency=self.energy_efficiency,
            scrape_metadata=ScrapeMetadata(
                url=self.url, timestamp=str(datetime.now().timestamp())
            ),
        )
