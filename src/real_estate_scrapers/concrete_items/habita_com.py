"""
Scraper specification for https://www.habita.com/ (API-based)
"""
import json
import re
from collections import defaultdict
from datetime import datetime
from functools import cached_property
from typing import List, Literal, Optional, Type, TypedDict

from real_estate_scrapers.items import RealEstateHomePage, RealEstateListPage, RealEstatePage
from real_estate_scrapers.models import EnergyData, ListingType


class HabitaItemData(TypedDict):
    """Typing for the item returned by the Habita API call."""

    id: int
    area: str
    area3: str
    district: str
    country: str
    latitude: float
    longitude: float
    price: float
    # pylint: disable=invalid-name
    convertedPrice: Optional[float]
    currency: str
    type: str
    title: Optional[str]
    upcoming: bool
    image: str
    showing: Optional[bool]
    reserved: Optional[bool]


class HabitaApiResponse(TypedDict):
    """
    Full API response typing
    """

    results: List[HabitaItemData]
    # pylint: disable=invalid-name
    numResults: int
    # pylint: disable=invalid-name
    totalPages: int


_country_iso_dict = {
    "Finland": "FIN",
    "Spain": "ESP",
    "Greece": "GRC",
    "Germany": "DEU",
}

# Codes for API access
_country_name_site_code_dct = {
    "Finland": 1,
    "Spain": 3,
    "Greece": 15,
    "Germany": 9,
}
codes = list(_country_name_site_code_dct.values())

# Key: item id, value: dict returned by the API call
item_map = {}

ListingQueryType = Literal["ResidenceSale", "ResidenceRent"]


def _create_api_url(
    country_codes: List[int], page: int, items_per_page: int, listing_query_type: ListingQueryType
) -> str:
    countries = ",".join(str(country_code) for country_code in country_codes)
    return (
        f"https://www.habita.com/propertysearch/results/en/{page}/{items_per_page}/full?"
        f"countries={countries}&"
        f"sort=newest&"
        f"type={listing_query_type}"
    )


class HabitaComRealEstateHomePage(RealEstateHomePage):
    """
    Entry point for scraping items from https://www.habita.com/.
    Defines how to extract urls pointing to ``HabitaComRealEstateListPage``s.
    """

    @staticmethod
    def domain() -> str:
        return "habita.com"

    @staticmethod
    def start_urls() -> List[str]:
        return ["https://www.habita.com/"]

    @property
    def real_estate_list_urls(self) -> List[str]:
        return [
            _create_api_url(codes, 1, 1, "ResidenceSale"),
            _create_api_url(codes, 1, 1, "ResidenceRent"),
        ]


class HabitaComRealEstateListPage(RealEstateListPage):
    """
    Defines how to extract urls pointing to ``HabitaComRealEstatePage``s.
    """

    @staticmethod
    def parent_page_type() -> Type[RealEstateHomePage]:
        return HabitaComRealEstateHomePage

    @cached_property
    def data(self) -> HabitaApiResponse:
        result: HabitaApiResponse = json.loads(self.response.html)
        return result

    @property
    def real_estate_list_urls_paginated(self) -> List[str]:
        listing_query_type: ListingQueryType = self.url.split("=")[-1]
        num_results = self.data["numResults"]
        num_pages = num_results // 100 + 1
        return [_create_api_url(codes, page, 100, listing_query_type) for page in range(1, num_pages + 1)]

    @property
    def real_estate_urls(self) -> List[str]:
        results: List[HabitaItemData] = self.data["results"]
        item_ids = [result["id"] for result in results]
        # "Passing down" country details to ``HabitaComRealEstatePage`` using a global dict
        for result in results:
            item_id = result["id"]
            item_map[item_id] = result
        return [f"https://www.habita.com/property/en/{item_id}" for item_id in item_ids]


class HabitaComRealEstatePage(RealEstatePage):
    """
    Defines how to extract single real estate objects from https://www.habita.com/.
    """

    @staticmethod
    def parent_page_type() -> Type[RealEstateListPage]:
        return HabitaComRealEstateListPage

    @cached_property
    def data(self) -> HabitaItemData:
        # Extracting id from URL: https://www.habita.com/property/rent/642964/en
        result = re.findall(r"\d{6}", self.url)
        item_id: int = int(result[0])
        item_data = item_map[item_id]
        return defaultdict(lambda: None, item_data)  # type: ignore

    def general_entry(self, name: str) -> Optional[str]:
        selector = f"//table[@id='general-information']//th[text()='{name}']/following-sibling::td/text()"
        result: Optional[str] = self.xpath(selector).get()
        return result

    def detail_entry(self, name: str) -> Optional[str]:
        selector = f"//table[@class='details']//th[text()='{name}']/following-sibling::td/text()"
        result: Optional[str] = self.xpath(selector).get()
        return result

    @property
    def country(self) -> str:
        return _country_iso_dict[self.data["country"]]

    @property
    def city(self) -> str:
        return self.data["area3"]

    @property
    def zip_code(self) -> str:
        # 45700 Kuusankoski
        location_str = self.general_entry("Location")
        if location_str is None:
            raise AttributeError("Location not found")
        result = re.findall(r"\d+", location_str)
        zip_str: str = result[0]
        return zip_str

    @property
    def listing_type(self) -> ListingType:
        if "rent" in self.url:
            return "rent"
        return "sale"

    @property
    def area(self) -> Optional[float]:
        # 125 m²
        area_str = self.data["area"]
        if area_str is None:
            return None
        num_str = area_str.split(" ")[0]
        return float(num_str)

    @property
    def price_amount(self) -> Optional[float]:
        return self.data["price"]

    @property
    def price_unit(self) -> str:
        if self.listing_type == "rent":
            return "EUR/MONTH"
        return "EUR"

    @property
    def heating_demand(self) -> Optional[EnergyData]:
        return None

    @property
    def energy_efficiency(self) -> Optional[EnergyData]:
        # D, 2013
        energy_info_str: Optional[str] = self.detail_entry("Energy certificate class")
        if energy_info_str is None:
            return None
        result = re.findall(r"([A-G]), (\d{4})", energy_info_str)
        if len(result) == 0:
            return None
        class_str, _ = result[0]
        return EnergyData(energy_class=class_str, value=None)

    @property
    def epc_pdf_url(self) -> Optional[str]:
        return None

    @property
    def epc_issued_date(self) -> Optional[datetime]:
        # D, 2013
        energy_info_str: Optional[str] = self.detail_entry("Energy certificate class")
        if energy_info_str is None:
            return None
        result = re.findall(r"([A-G]), (\d{4})", energy_info_str)
        if len(result) == 0:
            return None
        _, year_str = result[0]
        return datetime.strptime(year_str, "%Y")

    @property
    def date_of_building(self) -> Optional[datetime]:
        year_str = self.detail_entry("Construction year")
        if year_str is None:
            return None
        return datetime.strptime(year_str, "%Y")

    @property
    def object_type(self) -> str:
        return self.data["type"]
