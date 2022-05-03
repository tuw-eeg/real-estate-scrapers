"""Scraper specification for https://www.immowelt.at/"""
import itertools
import re
from datetime import datetime
from typing import List, Optional, Type

from real_estate_scrapers.items import RealEstateHomePage, RealEstateListPage, RealEstatePage
from real_estate_scrapers.models import EnergyData, ListingType

# real-estate object types to be scraped
real_estate_type_map = {
    "haeuser": "Haus",
    "wohnungen": "Wohnung",
    "wohnen-auf-zeit": "Wohnung",
}


class ImmoweltAtRealEstateHomePage(RealEstateHomePage):
    """
    Entry point for scraping items from https://www.immowelt.at/.
    Defines how to extract urls pointing to ``ImmoweltAtRealEstateListPage``s.
    """

    @staticmethod
    def domain() -> str:
        return "immowelt.at"

    @staticmethod
    def start_urls() -> List[str]:
        return ["https://www.immowelt.at/sitemap"]

    @property
    def real_estate_list_urls(self) -> List[str]:
        search_hrefs = self.xpath(
            '//h2[contains(text(), "Immobilien in Österreich")]'
            "/following-sibling::*[position()=1]"
            '//li/a[contains(@href, "/suche/")]/@href'
        ).getall()
        pattern = r"^\/suche\/(\w+)\/\w+$"
        places = itertools.chain.from_iterable(re.findall(pattern, href) for href in search_hrefs)
        objects = real_estate_type_map.keys()
        listing_links = [f"https://www.immowelt.at/liste/{place}/{obj}" for place in places for obj in objects]
        return listing_links


class ImmoweltAtRealEstateListPage(RealEstateListPage):
    """
    Defines how to extract urls pointing to ``ImmoweltAtRealEstatePage``s.
    """

    @staticmethod
    def parent_page_type() -> Type[RealEstateHomePage]:
        return ImmoweltAtRealEstateHomePage

    @property
    def real_estate_list_urls_paginated(self) -> List[str]:
        # "5.123 Wohnungen in Amstetten"
        match_number_text = self.xpath("//h1[starts-with(@class, 'MatchNumber-')]/text()").get()
        re_search = re.search(r"\d+(\.\d+)?", match_number_text)
        if not re_search:
            raise ValueError(f"Could not extract number of properties from {match_number_text}")
        num_string: str = re_search.group()
        match_number = int(num_string.replace(".", ""))
        items_per_page = 20
        pages = (match_number // items_per_page) + 1
        return [f"{self.url}?sp={page}" for page in range(1, pages + 1)]

    @property
    def real_estate_urls(self) -> List[str]:
        return list(self.xpath('//a[starts-with(@href, "https://www.immowelt.at/expose")]/@href').getall())


class ImmoweltAtRealEstatePage(RealEstatePage):
    """
    Defines how to extract single real estate objects from https://www.immowelt.at/.
    """

    @property
    def country(self) -> str:
        return "AUT"

    @property
    def city(self) -> str:
        # '4400 St. Pölten'
        address_text = (
            self.xpath(
                '//*[@id="aUebersicht"]/app-estate-address/div/sd-cell/sd-cell-row/sd-cell-col[2]/span[2]/div[1]/text()'
            )
            .get()
            .strip()
        )
        # 'St. Pölten'
        city: str = " ".join(address_text.split()[1:])
        return city

    @property
    def zip_code(self) -> str:
        # '4400 Steyr'
        address_text = (
            self.xpath(
                '//*[@id="aUebersicht"]/app-estate-address/div/sd-cell/sd-cell-row/sd-cell-col[2]/span[2]/div[1]/text()'
            )
            .get()
            .strip()
        )
        # '4400'
        zip_code: str = address_text.split()[0]
        return zip_code

    @property
    def listing_type(self) -> ListingType:
        price_caption = self.xpath('//*[@id="aUebersicht"]/app-hardfacts' "/div/div/div[1]/div[2]/text()").get().strip()
        if "miet" in price_caption.lower():
            return "rent"
        else:
            return "sale"

    @property
    def area(self) -> Optional[float]:
        # '1.000,50 m²'
        area_label = (
            self.xpath('//*[@id="aUebersicht"]/app-hardfacts' "/div/div/div[2]/div[1]/span/text()").get().strip()
        )
        # 1000.50
        num_str = area_label.split()[0].replace(".", "").replace(",", ".")
        return float(num_str) if self.fmtckr.is_numeric(num_str) else None

    @property
    def price_amount(self) -> Optional[float]:
        # '€\xa07.117,12'
        price_label = (
            self.xpath('//*[@id="aUebersicht"]/app-hardfacts' "/div/div/div[1]/div[1]/strong/text()").get().strip()
        )
        # 7117.12
        num_str = price_label[2:].replace(".", "").replace(",", ".")
        return float(num_str) if self.fmtckr.is_numeric(num_str) else None

    @property
    def price_unit(self) -> str:
        price_caption = self.xpath('//*[@id="aUebersicht"]/app-hardfacts' "/div/div/div[1]/div[2]/text()").get().strip()
        if price_caption == "Kaufpreis":
            return "EUR"
        elif "miet" in price_caption.lower():
            return "EUR/MONTH"
        else:
            raise NotImplementedError(f"No price unit mapping for: '{price_caption}'")

    def __extract_energy_data(self, base_selector_query: str) -> Optional[EnergyData]:
        base_selector = self.xpath(base_selector_query)
        if len(base_selector) == 0:
            return None
        heating_demand_h4_selector = base_selector[0]
        energy_class = heating_demand_h4_selector.xpath("following-sibling::div[1]/span/text()").get()
        value_str = heating_demand_h4_selector.xpath("following-sibling::p[1]/text()").get()
        num_str = value_str.split()[0].replace(".", "").replace(",", ".")
        return EnergyData(energy_class=energy_class, value=float(num_str) if self.fmtckr.is_numeric(num_str) else None)

    @property
    def heating_demand(self) -> Optional[EnergyData]:
        return self.__extract_energy_data("//app-energy-certificate-at/h4[text()[contains(.,'(HWB)')]]")

    @property
    def energy_efficiency(self) -> Optional[EnergyData]:
        return self.__extract_energy_data("//app-energy-certificate-at/h4[text()[contains(.,'(fGEE)')]]")

    @property
    def epc_pdf_url(self) -> Optional[str]:
        # Not available
        return None

    @property
    def epc_issued_date(self) -> Optional[datetime]:
        # Not available
        return None

    @property
    def date_of_building(self) -> Optional[datetime]:
        # (Ca.)? 1900
        year_str_raw = self.xpath('//sd-cell-col/p[text()="Baujahr"]/following-sibling::p/text()').get()
        if year_str_raw is not None and self.fmtckr.contains_number(year_str_raw):
            year_str = self.fmtckr.extract_year(year_str_raw)
            return datetime(int(year_str), 1, 1)
        return None

    @property
    def object_type(self) -> str:
        # 'https://www.immowelt.at/suche/haeuser'
        back_href = self.xpath("//app-breadcrumb/descendant-or-self::nav/ol/li[2]/a/@href").get()
        if back_href is None:
            raise ValueError("No back href found for object type")
        # 'haeuser'
        object_type_slug = back_href.split("/")[-1]
        return real_estate_type_map.get(object_type_slug, "unknown")
