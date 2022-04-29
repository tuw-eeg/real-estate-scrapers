"""Defines the Page Object Model for Real Estates to be scraped"""
from datetime import datetime
from typing import List, Optional, Type

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


class RealEstateHomePage(WebPage):  # type: ignore
    """Page Object Model for Real Estate Home Pages from which urls to ``RealEstateListPage``s are scraped."""

    @staticmethod
    def should_use_selenium() -> bool:
        """
        Returns: ``True`` if the page should be scraped using Selenium.
                  Will affect the scraping method of ``RealEstateListPage`` and ``RealEstatePage`` too.
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
        Method to specify the initial urls to be processed by ``real_estate_list_urls``.

        Returns: The urls of the website from which urls to ``RealEstateListPage``s are scraped. Must be absolute urls.
        """
        raise NotImplementedError

    @property
    def real_estate_list_urls(self) -> List[str]:
        """
        Method to actually parse the home page for the urls of the real estate list pages.

        Returns: A list of urls to be used to scrape ``RealEstateListPage`` objects.
                 Must be absolute urls if ``should_use_selenium`` is true.
        """
        raise NotImplementedError


class RealEstateListPage(WebPage):  # type: ignore
    """Page Object Model for Real Estate List Pages, from which urls pointing to ``RealEstatePage``s are scraped."""

    @staticmethod
    def parent_page_type() -> Type[RealEstateHomePage]:
        """
        Returns: The parent page type (class) of this page object model.
        """
        raise NotImplementedError

    @property
    def real_estate_urls(self) -> List[str]:
        """
        Returns: A list of urls to be used to scrape ``RealEstatePage`` objects.
                 Must be absolute urls if ``should_use_selenium`` is true.
        """
        raise NotImplementedError


class RealEstatePage(ItemWebPage):  # type: ignore
    """
    Defines the Page Object Model for Real Estates to be scraped.
    Items get extracted based on the logic defined in this class.
    """

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
        Possible values: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3

        Returns: The ISO 3166-1 alpha-3 country code of the real estate item's location.
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
