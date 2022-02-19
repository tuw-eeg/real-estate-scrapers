"""Defines the Page Object Model for Real Estates to be scraped"""

from abc import ABC, abstractmethod
from typing import List

from web_poet import ItemWebPage, WebPage  # type: ignore

from real_estate_scrapers.models import ListingType, Location, Price, RealEstate


class RealEstateListPage(WebPage, ABC):  # type: ignore
    """Page Object Model for Real Estate List Pages"""

    @staticmethod
    @abstractmethod
    def domain() -> str:
        """
        Returns: The domain of the website from which the urls are scraped
        """
        ...

    @staticmethod
    @abstractmethod
    def start_urls() -> List[str]:
        """
        Returns: A list of urls to be scraped
        """
        ...

    @property
    @abstractmethod
    def real_estate_urls(self) -> List[str]:
        """
        Returns: A list of urls of the real estate detail items to be scraped
        """
        ...


class RealEstatePage(ItemWebPage, ABC):  # type: ignore
    """Defines the Page Object Model for Real Estates to be scraped"""

    @property
    @abstractmethod
    def url(self) -> str:
        """
        Returns: The url of the real estate item
        """
        ...

    @property
    @abstractmethod
    def country(self) -> str:
        """
        Returns: The country where the real estate item is located
        """
        ...

    @property
    @abstractmethod
    def city(self) -> str:
        """
        Returns: The city where the real estate item is located
        """
        ...

    @property
    @abstractmethod
    def zip_code(self) -> str:
        """
        Returns: The ZIP code of the real estate item's location
        """
        ...

    @property
    @abstractmethod
    def listing_type(self) -> ListingType:
        """
        Returns: The ZIP code of the real estate item's location
        """
        ...

    @property
    @abstractmethod
    def area(self) -> float:
        """
        Returns: The area of the real estate item in square meters
        """
        ...

    @property
    @abstractmethod
    def price_amount(self) -> float:
        """
        Returns: The price of the real estate item
        """
        ...

    @property
    @abstractmethod
    def price_currency(self) -> str:
        """
        Returns: The currency in which the real estate item is priced
        """
        ...

    @property
    @abstractmethod
    def epc_label(self) -> str:
        """
        Returns: The EPC Label (Energy class) of the real estate item
        """
        ...

    @property
    @abstractmethod
    def heating_demand(self) -> float:
        """
        Returns: The heating demand of the real estate item
        """
        ...

    def to_item(self) -> RealEstate:
        return RealEstate(
            url=self.url,
            location=Location(
                country=self.country, city=self.city, zip_code=self.zip_code
            ),
            listing_type=self.listing_type,
            area=self.area,
            price=Price(amount=self.price_amount, currency=self.price_currency),
            epc_label=self.epc_label,
            heating_demand=self.heating_demand,
        )
