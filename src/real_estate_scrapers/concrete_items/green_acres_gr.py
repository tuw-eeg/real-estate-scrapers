"""Scraper specification for https://www.green-acres.gr/"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from real_estate_scrapers.items import RealEstateHomePage, RealEstateListPage, RealEstatePage
from real_estate_scrapers.models import EnergyData, ListingType


class GreenAcresGrRealEstateHomePage(RealEstateHomePage):
    """
    Entry point for scraping items from https://www.green-acres.gr/.
    Defines how to extract urls pointing to ``GreenAcresGrRealEstateListPage``s.
    """

    @staticmethod
    def should_use_selenium() -> bool:
        return True

    @staticmethod
    def domain() -> str:
        return "green-acres.gr"

    @staticmethod
    def start_urls() -> List[str]:
        return ["https://www.green-acres.gr/en/properties"]

    @staticmethod
    def __click_search_button_js() -> str:
        return """
                const searchButton = document.querySelector('button.btn-search');
                if (searchButton) {
                    searchButton.click();
                }
                """

    @staticmethod
    def request_kwargs() -> Dict[str, Any]:
        # pass script to `SeleniumRequest`
        return dict(
            script=GreenAcresGrRealEstateHomePage.__click_search_button_js(),
            wait_time=3,
            wait_until=presence_of_element_located((By.XPATH, "//p[@class='pagination-info']")),  # type: ignore
        )

    @property
    def real_estate_list_urls(self) -> List[str]:
        # '/property-for-sale/attica'
        hrefs = self.xpath("//li[not(@class)]/a[starts-with(@href, '/property')]/@href").getall()
        return [f"https://www.green-acres.gr{href}" for href in hrefs]


class GreenAcresGrRealEstateListPage(RealEstateListPage):
    """
    Defines how to extract urls pointing to ``GreenAcresGrRealEstatePage``s.
    """

    @staticmethod
    def parent_page_type() -> Type[RealEstateHomePage]:
        return GreenAcresGrRealEstateHomePage

    @property
    def real_estate_list_urls_paginated(self) -> List[str]:
        # avoid infinite recursion, do not paginate already paginated pages
        if "?p_n=" in self.url:
            return []
        # "1 - 24 out of 7,754 properties"
        match_number_text = self.xpath("//p[@class='pagination-info']/text()").get()
        re_search = re.search(r".* out of (\d+(?:,\d+)?) properties", match_number_text)
        if not re_search:
            raise ValueError(f"Could not extract number of properties from {match_number_text}")
        num_string: str = re_search.groups()[0]
        match_number = int(num_string.replace(",", ""))
        items_per_page = 24
        pages = (match_number // items_per_page) + 1
        pagination_base_href = self.xpath("//ul[@class='pagination']/li[@class='active']/a/@href").get()
        return [f"https://www.green-acres.gr{pagination_base_href}?p_n={page}" for page in range(1, pages + 1)]

    @property
    def real_estate_urls(self) -> List[str]:
        hrefs = self.xpath("//figure[@class='item-main']/a/@href").getall()
        return [f"https://www.green-acres.gr{href}" for href in hrefs]


class GreenAcresGrRealEstatePage(RealEstatePage):
    """
    Defines how to extract single real estate objects from https://www.green-acres.gr/.
    """

    @property
    def country(self) -> str:
        return "GRC"

    @property
    def city(self) -> str:
        city_text: str = self.xpath("//a[@class='item-location']/p/text()").get()
        return city_text.strip()

    @property
    def zip_code(self) -> str:
        return None  # type: ignore

    @property
    def listing_type(self) -> ListingType:
        return "sale"

    @property
    def area(self) -> Optional[float]:
        xpath = "//p[@class='details-name'][text()='Living area']/parent::li/text()"
        if self.object_type == "land":
            xpath = "//p[@class='details-name'][text()='Land']/parent::li/text()"
        text_nodes: List[str] = self.xpath(xpath).getall()

        stripped_text_nodes = [node.replace("\n", "").strip() for node in text_nodes]
        area_text = [node for node in stripped_text_nodes if node][0].replace(",", "")
        if self.fmtckr.is_numeric(area_text):
            return float(area_text)
        return None

    @property
    def price_amount(self) -> Optional[float]:
        # 45,000 €
        price_text: str = self.xpath("//h2[@class='title-standard']/span[@class='price']/text()").get()
        number_text: str = price_text.replace("€", "").replace(",", "").strip()
        if self.fmtckr.is_numeric(number_text):
            return float(number_text)
        return None

    @property
    def price_unit(self) -> str:
        return "EUR"

    @property
    def heating_demand(self) -> Optional[EnergyData]:
        data_text: str = self.xpath("//span[@class='icons-text'][text()='PEA']/parent::span/text()").get().strip()
        if data_text == "N/C":
            return None
        return EnergyData(energy_class=data_text, value=None)

    @property
    def energy_efficiency(self) -> Optional[EnergyData]:
        return None

    @property
    def epc_pdf_url(self) -> Optional[str]:
        return None

    @property
    def epc_issued_date(self) -> Optional[datetime]:
        return None

    @property
    def date_of_building(self) -> Optional[datetime]:
        description_text = self.xpath("//div[@id='descriptionBlockAdvertPage']/div/p[@class='text']").get()
        if description_text is None:
            return None
        # Match 4-digit numbers between 1700 and 2099
        re_search = re.search(r"((:?17|18|19|20)\d{2})", description_text.lower())
        if not re_search:
            return None
        year_str: str = re_search.groups()[0]
        return datetime(int(year_str), 1, 1)

    @property
    def object_type(self) -> str:
        # url: https://www.green-acres.gr/en/properties/apartment/athens/Ad2adhezqe41y31v.htm
        url_segments = self.url.replace("https://www.green-acres.gr/", "").split("/")
        type_segment: str = url_segments[2]
        return type_segment
