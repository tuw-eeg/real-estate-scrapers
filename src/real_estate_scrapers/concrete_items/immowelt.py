"""Scraper specification for https://www.immowelt.at/"""
from typing import List, Optional

from real_estate_scrapers.items import RealEstateListPage, RealEstatePage
from real_estate_scrapers.models import EnergyData, ListingType


class ImmoweltRealEstateListPage(RealEstateListPage):
    """
    Handles scraping the urls of ``ImmoweltRealEstatePage`` objects
    from https://www.immowelt.at/.
    """

    @staticmethod
    def domain() -> str:
        return "immowelt.at"

    @staticmethod
    def start_urls() -> List[str]:
        return [
            "https://www.immowelt.at/liste/bezirk-dornbirn"
            "/wohnungen/mieten?lat=47.40493333&"
            "lon=9.69903333&sort=relevanz%20distance"
        ]

    @property
    def real_estate_urls(self) -> List[str]:
        return ["https://www.immowelt.at/expose/24xa35g"]


class ImmoweltRealEstatePage(RealEstatePage):
    """
    Handles scraping the of real estate objects
    from https://www.immowelt.at/
    """

    @property
    def country(self) -> str:
        return "AUT"

    @property
    def city(self) -> str:
        pass

    @property
    def zip_code(self) -> str:
        pass

    @property
    def listing_type(self) -> ListingType:
        pass

    @property
    def area(self) -> float:
        pass

    @property
    def price_amount(self) -> float:
        pass

    @property
    def price_currency(self) -> str:
        return "EUR"

    @property
    def epc_label(self) -> Optional[str]:
        pass

    @property
    def heating_demand(self) -> Optional[EnergyData]:
        pass

    @property
    def energy_efficiency(self) -> Optional[EnergyData]:
        pass
