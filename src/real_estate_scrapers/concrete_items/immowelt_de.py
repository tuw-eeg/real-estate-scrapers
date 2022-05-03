"""Scraper specification for https://www.immowelt.de/"""
import itertools
import re
from datetime import datetime
from typing import List, Optional, Type

from real_estate_scrapers.items import RealEstateHomePage, RealEstateListPage, RealEstatePage
from real_estate_scrapers.models import EnergyData, ListingType

real_estate_type_map = {
    "haeuser": "Haus",
    "wohnungen": "Wohnung",
    "wohnen-auf-zeit": "Wohnung",
}


class ImmoweltDeRealEstateHomePage(RealEstateHomePage):
    """
    Entry point for scraping items from https://www.immowelt.de/.
    Defines how to extract urls pointing to ``ImmoweltDeRealEstateListPage``s.
    """

    @staticmethod
    def domain() -> str:
        return "immowelt.de"

    @staticmethod
    def start_urls() -> List[str]:
        return ["https://www.immowelt.de/sitemap"]

    @property
    def real_estate_list_urls(self) -> List[str]:
        def search_hrefs_for_heading(heading: str) -> List[str]:
            hrefs: List[str] = self.xpath(
                f'//h2[contains(text(), "{heading}")]'
                "/following-sibling::*[position()=1]"
                '//li/a[contains(@href, "/suche/")]/@href'
            ).getall()
            return hrefs

        headings = ["Immobilien nach Bundesland", "Immobilien in Städten", "Wohnungen in Großstädten"]
        search_hrefs = list(itertools.chain.from_iterable(search_hrefs_for_heading(heading) for heading in headings))
        pattern = r"(https:\/\/www.immowelt.de)?\/suche\/([\w-]+)\/"
        places = set(re.findall(pattern, href)[0][1] for href in search_hrefs)
        objects = real_estate_type_map.keys()
        return [f"https://www.immowelt.de/liste/{place}/{obj}" for place in places for obj in objects]


class ImmoweltDeRealEstateListPage(RealEstateListPage):
    """
    Defines how to extract urls pointing to ``ImmoweltDeRealEstatePage``s.
    """

    @staticmethod
    def parent_page_type() -> Type[RealEstateHomePage]:
        return ImmoweltDeRealEstateHomePage

    @property
    def real_estate_list_urls_paginated(self) -> List[str]:
        # avoid infinite recursion, do not paginate already paginated pages
        if "?sp=" in self.url:
            return []
        # "6.123 Wohnungen in Hamburg"
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
        return list(self.xpath('//a[starts-with(@href, "https://www.immowelt.de/expose")]/@href').getall())


class ImmoweltDeRealEstatePage(RealEstatePage):
    """
    Defines how to extract single real estate objects from https://www.immowelt.de/.
    """

    @property
    def country(self) -> str:
        return "DEU"

    @property
    def city(self) -> str:
        # '33617 Bielefeld-Gadderbaum'
        address_text = self.xpath('//span[@data-cy="address-city"]/div[1]/text()').get()
        # 'Bielefeld-Gadderbaum'
        city: str = " ".join(address_text.split()[1:])
        return city

    @property
    def zip_code(self) -> str:
        # '33617 Bielefeld-Gadderbaum'
        address_text = self.xpath('//span[@data-cy="address-city"]/div[1]/text()').get()
        # '33617'
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
        # '548.000\xa0€'
        price_label = (
            self.xpath('//*[@id="aUebersicht"]/app-hardfacts/div/div/div[1]/div[1]/strong/text()').get().strip()
        )
        # 548000
        num_str = price_label[:-2].replace(".", "").replace(",", ".")
        return float(num_str) if self.fmtckr.is_numeric(num_str) else None

    @property
    def price_unit(self) -> str:
        price_caption = self.xpath('//*[@id="aUebersicht"]/app-hardfacts/div/div/div[1]/div[2]/text()').get().strip()
        if any(kw in price_caption.lower() for kw in ["kauf", "mindest"]):
            return "EUR"
        elif any(kw in price_caption.lower() for kw in ["miet"]):
            return "EUR/MONTH"
        else:
            raise NotImplementedError(f"No price unit mapping for: '{price_caption}'")

    @property
    def heating_demand(self) -> Optional[EnergyData]:
        energy_info_selection = self.xpath("//app-energy-certificate/div[contains(@class, 'energy_information')]")
        if len(energy_info_selection) == 0:
            return None
        energy_info_tag = energy_info_selection[0]
        # '71,30 kWh/(m²·a)  - Warmwasser enthalten'
        heating_demand_text = energy_info_tag.xpath('//sd-cell-col[@data-cy="energy-consumption"]/p[2]/text()').get()
        if heating_demand_text is not None:
            # '71,30'
            heating_demand_value_text = heating_demand_text.strip().split()[0]
            num_str = heating_demand_value_text.replace(".", "").replace(",", ".")
            energy_class = energy_info_tag.xpath('//sd-cell-col[@data-cy="energy-class"]/p[2]/text()').get()
            return EnergyData(energy_class=energy_class, value=float(num_str))
        return None

    @property
    def energy_efficiency(self) -> Optional[EnergyData]:
        # fGEE available only for Austrian real estates
        return None

    @property
    def epc_pdf_url(self) -> Optional[str]:
        # Not available
        return None

    @property
    def epc_issued_date(self) -> Optional[datetime]:
        energy_info_selection = self.xpath("//app-energy-certificate/div[contains(@class, 'energy_information')]")
        if len(energy_info_selection) == 0:
            return None
        energy_info_tag = energy_info_selection[0]
        validity_date_text: Optional[str] = energy_info_tag.xpath(
            '//sd-cell-col[@data-cy="energy-validity"]/p[2]/text()'
        ).get()
        if validity_date_text is not None:
            validity_date_text = validity_date_text.strip()
            if validity_date_text.startswith("bis"):
                # case: 'bis 28.10.2021'
                return None
            if validity_date_text.startswith("seit"):
                # case: 'seit 28.10.2021'
                start_year = validity_date_text.split()[1]
            else:
                # case: '01.08.2018 bis 31.07.2028'
                start_year = validity_date_text.split()[0]
            return datetime.strptime(start_year, "%d.%m.%Y")
        return None

    @property
    def date_of_building(self) -> Optional[datetime]:
        energy_info_selection = self.xpath("//app-energy-certificate/div[contains(@class, 'energy_information')]")
        if len(energy_info_selection) == 0:
            return None
        energy_info_tag = energy_info_selection[0]
        # '2000'
        date_text = energy_info_tag.xpath('//sd-cell-col[@data-cy="energy-yearofmodernization"]/p[2]/text()').get()
        if date_text is not None and self.fmtckr.contains_number(date_text):
            year_str = self.fmtckr.extract_year(date_text)
            return datetime(int(year_str), 1, 1)
        return None

    @property
    def object_type(self) -> str:
        # 'https://www.immowelt.de/suche/haeuser'
        back_href = self.xpath("//app-breadcrumb/descendant-or-self::nav/ol/li[2]/a/@href").get()
        if back_href is None:
            raise ValueError("No back href found for object type")
        # 'haeuser'
        object_type_slug = back_href.split("/")[-1]
        return real_estate_type_map.get(object_type_slug, "unknown")
