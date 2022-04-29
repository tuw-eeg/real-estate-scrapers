"""Scraper specification for https://en.tospitimou.gr/"""
import itertools
import re
from datetime import datetime
from typing import List, Optional, Tuple, Type

from real_estate_scrapers.items import RealEstateHomePage, RealEstateListPage, RealEstatePage
from real_estate_scrapers.models import EnergyData, ListingType


class TospitimouGrRealEstateHomePage(RealEstateHomePage):
    """
    Entry point for scraping items from https://en.tospitimou.gr/.
    Defines how to extract urls pointing to ``TospitimouGrRealEstateListPage``s.
    """

    @staticmethod
    def should_use_selenium() -> bool:
        return True

    @staticmethod
    def domain() -> str:
        return "tospitimou.gr"

    @staticmethod
    def start_urls() -> List[str]:
        return ["https://en.tospitimou.gr/"]

    @property
    def real_estate_list_urls(self) -> List[str]:
        hrefs = self.xpath('//ul[@class="listing"]/li/a/@href').getall()
        num_listings = [int(text) for text in self.xpath('//ul[@class="listing"]/li/span/text()').getall()]
        # default of the site
        num_item_per_page = 20

        def get_list_page_urls(base_href: str, num_items: int) -> List[str]:
            num_pages = num_items // num_item_per_page + 1
            return [f"{base_href}?page={page}" for page in range(1, num_pages + 1)]

        return list(
            itertools.chain.from_iterable(get_list_page_urls(href, num) for href, num in zip(hrefs, num_listings))
        )


class TospitimouGrRealEstateListPage(RealEstateListPage):
    """
    Defines how to extract urls pointing to ``TospitimouGrRealEstatePage``s.
    """

    @staticmethod
    def parent_page_type() -> Type[RealEstateHomePage]:
        return TospitimouGrRealEstateHomePage

    @property
    def real_estate_urls(self) -> List[str]:
        raw_urls = self.xpath("//div[@data-targeturl]/@data-targeturl").getall()

        def normalize_url(url: str) -> str:
            return url.replace("\n", "").strip()

        return [normalize_url(url) for url in raw_urls]


class TospitimouGrRealEstatePage(RealEstatePage):
    """
    Defines how to extract single real estate objects from https://en.tospitimou.gr/.
    """

    @property
    def country(self) -> str:
        return "GRC"

    @property
    def city(self) -> str:
        # Derignu 58, Athina 10434
        address_line = self.xpath("//th[text()='Address']/following-sibling::td/text()").get().strip()
        match: List[Tuple[str, str]] = re.findall(r".*, (.*) (\d+)", address_line)
        # pylint: disable=unused-variable
        city, zip_code = match[0]
        return city

    @property
    def zip_code(self) -> str:
        # Derignu 58, Athina 10434
        address_line = self.xpath("//th[text()='Address']/following-sibling::td/text()").get().strip()
        match: List[Tuple[str, str]] = re.findall(r".*, (.*) (\d+)", address_line)
        # pylint: disable=unused-variable
        city, zip_code = match[0]
        return zip_code

    @property
    def listing_type(self) -> ListingType:
        if "sale" in self.url:
            return "sale"
        return "rent"

    @property
    def area(self) -> Optional[float]:
        # 1,420 m
        raw_string = self.xpath("//div[@data-original-title='Living Area in sq.m.']/span/text()").get().strip()
        number_string = raw_string[:-2].replace(",", "")
        return float(number_string)

    @property
    def price_amount(self) -> Optional[float]:
        # 1,200,000
        raw_string = self.xpath("//div[@data-original-title='Price']/span/text()").get().strip()
        number_string = raw_string.replace(",", "")
        return float(number_string)

    @property
    def price_unit(self) -> str:
        if self.listing_type == "sale":
            return "EUR"
        else:
            return "EUR/MONTH"

    @property
    def heating_demand(self) -> Optional[EnergyData]:
        return None

    @property
    def energy_efficiency(self) -> Optional[EnergyData]:
        energy_class = self.xpath("//div[@class='energy-container']/div/text()").get().strip()
        # TODO: energy value is in percentage, discuss how it should be stored
        energy_value = None
        return EnergyData(energy_class=energy_class, value=energy_value)

    @property
    def epc_pdf_url(self) -> Optional[str]:
        return None

    @property
    def epc_issued_date(self) -> Optional[datetime]:
        return None

    @property
    def date_of_building(self) -> Optional[datetime]:
        # 1936
        year_str = self.xpath("//th[text()='Construction year']/following-sibling::td/text()").get().strip()
        return datetime(int(year_str), 1, 1)

    @property
    def object_type(self) -> str:
        object_type_string: Optional[str] = self.xpath("//div[@data-original-title='Residential']/span/text()").get()
        if object_type_string is None:
            return "unknown"
        return object_type_string.strip()
