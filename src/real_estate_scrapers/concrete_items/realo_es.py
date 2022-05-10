"""
Scraper specification for https://realo.es/

Re-uses the concrete item scraper logic defined in ``realo_be``, as the site structure is identical.
"""
import re
from re import Match
from typing import AnyStr, List, Optional, Type

import real_estate_scrapers.concrete_items.realo_be as realo_base
from real_estate_scrapers.items import RealEstateHomePage, RealEstateListPage


class RealoEsRealEstateHomePage(realo_base.RealoBeRealEstateHomePage):
    """
    Entry point for scraping items from https://realo.es/.
    Defines how to extract urls pointing to ``RealoEsRealEstateListPage``s.

    Re-uses the logic used for https://realo.be/.
    """

    @staticmethod
    def domain() -> str:
        return "realo.es"

    @staticmethod
    def start_urls() -> List[str]:
        num_city_pages = 41
        return [f"https://www.realo.es/en/cities?page={i}" for i in range(1, num_city_pages + 1)]


class RealoEsRealEstateListPage(realo_base.RealoBeRealEstateListPage):
    """
    Defines how to extract urls pointing to ``RealoEsRealEstatePage``s.

    Re-uses the logic used for https://realo.be/.
    """

    @staticmethod
    def parent_page_type() -> Type[RealEstateHomePage]:
        return RealoEsRealEstateHomePage


class RealoEsRealEstatePage(realo_base.RealoBeRealEstatePage):
    """
    Defines how to extract single real estate objects from https://realo.es/.

    Re-uses the logic used for https://realo.be/.
    """

    @staticmethod
    def parent_page_type() -> Type[RealEstateListPage]:
        return RealoEsRealEstateListPage

    @property
    def country(self) -> str:
        return "ESP"

    @staticmethod
    def zip_re_search(text: AnyStr) -> Optional[Match[AnyStr]]:
        return re.search(r"\d{5}", text)  # type: ignore
