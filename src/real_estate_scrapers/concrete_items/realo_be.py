"""Scraper specification for https://realo.be/"""
import re
from datetime import datetime
from re import Match
from typing import AnyStr, List, Optional, Type

from scrapy.exceptions import DropItem  # type: ignore

from real_estate_scrapers.items import RealEstateHomePage, RealEstateListPage, RealEstatePage
from real_estate_scrapers.models import EnergyData, ListingType


class RealoBeRealEstateHomePage(RealEstateHomePage):
    """
    Entry point for scraping items from https://realo.be/.
    Defines how to extract urls pointing to ``RealoBeRealEstateListPage``s.
    """

    @staticmethod
    def domain() -> str:
        return "realo.be"

    @staticmethod
    def start_urls() -> List[str]:
        return ["https://www.realo.be/en/cities?search=1"]

    @property
    def real_estate_list_urls(self) -> List[str]:
        # '/en/search/'s-gravenwezel-2970'
        hrefs: List[str] = self.xpath("//li[@class='cities-list--item']/a/@href").getall()
        return [f"https://www.{self.domain()}{href}" for href in hrefs]


class RealoBeRealEstateListPage(RealEstateListPage):
    """
    Defines how to extract urls pointing to ``RealoBeRealEstatePage``s.
    """

    @staticmethod
    def parent_page_type() -> Type[RealEstateHomePage]:
        return RealoBeRealEstateHomePage

    @property
    def real_estate_list_urls_paginated(self) -> List[str]:
        # avoid infinite recursion, do not paginate already paginated pages
        if "?page=" in self.url:
            return []
        # "2.039 results"
        match_number_text = self.xpath("//div[@data-id='totalResultsContainer']/text()").get()
        if not match_number_text:
            return []
        num_string: str = match_number_text.split()[0]
        match_number = int(num_string.replace(".", ""))
        items_per_page = 48
        pages = (match_number // items_per_page) + 1
        return [f"{self.url}?page={page}" for page in range(1, pages + 1)]

    @property
    def real_estate_urls(self) -> List[str]:
        hrefs: List[str] = self.xpath("//li[@data-id='componentEstateListGridItem']/div/@data-href").getall()
        return [f"https://www.{self.parent_page_type().domain()}{href}" for href in hrefs]


class RealoBeRealEstatePage(RealEstatePage):
    """
    Defines how to extract single real estate objects from https://realo.be/.
    """

    @property
    def country(self) -> str:
        return "BEL"

    @property
    def city(self) -> str:
        city_referrer: Optional[str] = self.xpath("//a[text()='Back to results for ']/em/text()").get()
        if not city_referrer:
            raise DropItem("Could not find city in page")
        return city_referrer.strip()

    @staticmethod
    def zip_re_search(text: AnyStr) -> Optional[Match[AnyStr]]:
        return re.search(r"\d{4}", text)  # type: ignore

    @property
    def zip_code(self) -> str:
        # try and get the ZIP from the url: 'https://www.realo.be/en/7090-braine-le-comte/5207953?l=1626355765'
        # 7090-braine-le-comte
        segment = self.url.replace("https://www.realo.be/en/", "").split("/")[0]
        re_search = self.zip_re_search(segment)
        if re_search:
            zip_string: str = re_search.group(1)
            return zip_string
        # Fallback to the address line
        # "Stationsstraat 16, 9420 Burst, Erpe-Mere burst"
        address_text: str = (
            self.xpath("//h1[@class='address']/text()").get().replace("\n", "").replace("\t", "").strip()
        )
        re_search = self.zip_re_search(address_text)
        if not re_search:
            raise DropItem(f"Could not extract ZIP from {address_text}")
        zip_string = re_search.group(1)
        return zip_string.strip()

    @property
    def listing_type(self) -> ListingType:
        type_string = self.xpath("//div[@class='type']/strong/text()").get()
        if not type_string:
            raise DropItem("Could not find listing type in page")
        if "sale" in type_string.lower():
            return "sale"
        return "rent"

    @property
    def area(self) -> Optional[float]:
        # "246m"
        area_string = self.__get_feature_value("Habitable area")
        if not area_string:
            return None
        return float(area_string.replace("m", ""))

    @property
    def price_amount(self) -> Optional[float]:
        price_string = self.xpath('//span[@itemprop="price"]/text()').get()
        if not price_string:
            return None
        return float(price_string)

    @property
    def price_unit(self) -> str:
        if self.listing_type == "sale":
            return "EUR"
        return "EUR/MONTH"

    @property
    def heating_demand(self) -> Optional[EnergyData]:
        return None

    @property
    def energy_efficiency(self) -> Optional[EnergyData]:
        energy_class_string = self.__get_feature_value("Energy classification")
        if energy_class_string:
            energy_class = energy_class_string[0]
            return EnergyData(energy_class=energy_class, value=None)
        peb_image_query = "//div[@class='component-property-features']//img[@class='peb-image']"
        # 'realocdn.com/assets/4cfb5bbcf3bffbe293ed8f284f9eb1fb7/img/peb/g.png'
        image_src: Optional[str] = self.xpath(peb_image_query + "/@src").get()
        if image_src:
            # '.../g.png' -> 'G'
            peb_class = image_src[-5].upper()
            peb_value: Optional[float] = None
            # '999kwh/m'
            peb_value_string = self.__get_feature_value("CPEB")
            if peb_value_string:
                peb_value = float(peb_value_string.replace("kwh/m", ""))
            return EnergyData(energy_class=peb_class, value=peb_value)
        return None

    @property
    def epc_pdf_url(self) -> Optional[str]:
        return self.__get_feature_value("EPC certificate number")

    @property
    def epc_issued_date(self) -> Optional[datetime]:
        return None

    @property
    def date_of_building(self) -> Optional[datetime]:
        year_string = self.__get_feature_value("Year built")
        if not year_string:
            return None
        year = int(year_string.strip())
        return datetime(year, 1, 1)

    @property
    def object_type(self) -> str:
        type_string = self.__get_feature_value("Property type")
        if not type_string:
            return "Unknown"
        return type_string.strip()

    def __get_feature_value(self, feature_name: str) -> Optional[str]:
        value_string: Optional[str] = self.xpath(
            f"//td[@class='name'][text()='{feature_name}']/following-sibling::td/text()"
        ).get()
        return value_string.strip().replace("\n", "").replace("\t", "") if value_string else None
