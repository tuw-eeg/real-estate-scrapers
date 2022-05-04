"""
Scraper specification for https://www.green-acres.es/.

Re-uses the concrete item scraper logic defined in ``green_acres_gr``, as the site structure is identical.
"""
from typing import List, Type

import real_estate_scrapers.concrete_items.green_acres_gr as green_acres_base
from real_estate_scrapers.items import RealEstateHomePage, RealEstateListPage


class GreenAcresEsRealEstateHomePage(green_acres_base.GreenAcresGrRealEstateHomePage):
    """
    Entry point for scraping items from https://www.green-acres.es/.
    Defines how to extract urls pointing to ``GreenAcresGrRealEstateListPage``s.

    Re-uses the logic used for https://www.green-acres.gr/.
    """

    @staticmethod
    def domain() -> str:
        return "green-acres.es"

    @staticmethod
    def start_urls() -> List[str]:
        return ["https://www.green-acres.es/en/properties"]


class GreenAcresEsRealEstateListPage(green_acres_base.GreenAcresGrRealEstateListPage):
    """
    Defines how to extract urls pointing to ``GreenAcresEsRealEstatePage``s.

    Re-uses the logic used for https://www.green-acres.gr/.
    """

    @staticmethod
    def parent_page_type() -> Type[RealEstateHomePage]:
        return GreenAcresEsRealEstateHomePage


class GreenAcresEsRealEstatePage(green_acres_base.GreenAcresGrRealEstatePage):
    """
    Defines how to extract single real estate objects from https://www.green-acres.es/.

    Re-uses the logic used for https://www.green-acres.gr/.
    """

    @staticmethod
    def parent_page_type() -> Type[RealEstateListPage]:
        return GreenAcresEsRealEstateListPage

    @property
    def country(self) -> str:
        return "ESP"
