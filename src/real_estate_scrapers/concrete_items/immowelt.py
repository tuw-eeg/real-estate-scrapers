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
        places = [
            "dornbirn",
            "graz",
            "innsbruck",
            "klagenfurt",
            "linz",
            "salzburg",
            "st-poelten",
            "steyr",
            "villach",
            "wels",
            "wien",
            "wiener-neustadt",
        ]
        objects = ["wohnungen", "haeuser", "wohnen-auf-zeit"]
        listing_links = [f"https://www.immowelt.at/liste/{place}/{obj}" for place in places for obj in objects]
        paginated_links = [f"{link}?cp={page}" for link in listing_links for page in range(2, 10)]
        return [*listing_links, *paginated_links]

    @property
    def real_estate_urls(self) -> List[str]:
        listing_ids = [
            tag.attrib["href"].split("/")[-1] for tag in self.css("#listItemWrapperFixed div a[href^='/expose']")
        ]
        return [f"https://www.immowelt.at/expose/{listing_id}" for listing_id in listing_ids]


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
        # '4400 St. Pölten\xa0'
        address_text = (
            self.xpath(
                '//*[@id="aUebersicht"]/app-estate-address/div/sd-cell/sd-cell-row/sd-cell-col[2]/span[2]/div[1]/text()'
            )
            .get()
            .strip()
        )
        # '4400 St. Pölten'
        trimmed_address_text = address_text[:-1]
        # 'St. Pölten'
        city: str = " ".join(trimmed_address_text.split()[1:])
        return city

    @property
    def zip_code(self) -> str:
        # '4400 Steyr\xa0'
        address_text = (
            self.xpath(
                '//*[@id="aUebersicht"]/app-estate-address/div/sd-cell/sd-cell-row/sd-cell-col[2]/span[2]/div[1]/text()'
            )
            .get()
            .strip()
        )
        # '4400 Steyr'
        trimmed_address_text = address_text[:-1]
        # '4400'
        zip_code: str = trimmed_address_text.split()[0]
        return zip_code

    @property
    def listing_type(self) -> ListingType:
        price_caption = self.xpath('//*[@id="aUebersicht"]/app-hardfacts' "/div/div/div[1]/div[2]/text()").get().strip()
        if price_caption == "Gesamtmiete":
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
    def price_currency(self) -> str:
        return "EUR"

    @property
    def epc_label(self) -> Optional[str]:
        return None

    @property
    def heating_demand(self) -> Optional[EnergyData]:
        return None

    @property
    def energy_efficiency(self) -> Optional[EnergyData]:
        return None
