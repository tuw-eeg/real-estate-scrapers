"""Scraper specification for https://www.immowelt.at/"""
from datetime import datetime
from typing import List, Optional

from real_estate_scrapers.items import RealEstateListPage, RealEstatePage
from real_estate_scrapers.models import EnergyData, ListingType

real_estate_type_map = {
    "haeuser": "Haus",
    "wohnungen": "Wohnung",
    "wohnen-auf-zeit": "Wohnung",
}


class ImmoweltAtRealEstateListPage(RealEstateListPage):
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
            "amstetten",
            "ansfelden",
            "bad-ischl",
            "bad-voeslau",
            "baden",
            "bischofshofen",
            "braunau-am-inn",
            "bregenz",
            "bruck-an-der-mur",
            "brunn-am-gebirge",
            "bludenz",
            "dornbirn",
            "eisenstadt",
            "enns",
            "feldkirch",
            "feldkirchen-in-kaernten",
            "gmunden",
            "goetzis",
            "graz",
            "hall-in-tirol",
            "hallein",
            "hard",
            "hohenems",
            "hollabrunn",
            "innsbruck",
            "immobilien?geoid=10306009007",
            "klagenfurt",
            "klosterneuburg",
            "krems-an-der-donau",
            "kapfenberg",
            "kufstein",
            "korneuburg",
            "leoben",
            "leonding",
            "linz",
            "lienz",
            "lustenau",
            "moedling",
            "marchtrenk",
            "mistelbach",
            "neunkirchen",
            "perchtoldsdorf",
            "rankweil",
            "ried-im-innkreis",
            "salzburg",
            "saalfelden-am-steinernen-meer",
            "schwaz",
            "schwechat",
            "spittal-an-der-drau",
            "st-poelten",
            "st-veit-an-der-glan",
            "sankt-johann-im-pongau",
            "steyr",
            "stockerau",
            "telfs",
            "ternitz",
            "tulln-an-der-donau",
            "traun-oberoesterreich",
            "traiskirchen",
            "villach",
            "voecklabruck",
            "voelkermarkt",
            "waidhofen-an-der-ybbs",
            "wals-siezenheim",
            "wels",
            "wien",
            "wiener-neustadt",
            "wolfsberg",
            "woergl",
            "zwettl-niederoesterreich",
        ]

        objects = real_estate_type_map.keys()
        listing_links = [f"https://www.immowelt.at/liste/{place}/{obj}" for place in places for obj in objects]
        paginated_links = [f"{link}?cp={page}" for link in listing_links for page in range(2, 201)]
        return [*listing_links, *paginated_links]

    @property
    def real_estate_urls(self) -> List[str]:
        listing_ids = [
            tag.attrib["href"].split("/")[-1] for tag in self.css("#listItemWrapperFixed div a[href^='/expose']")
        ]
        return [f"https://www.immowelt.at/expose/{listing_id}" for listing_id in listing_ids]


class ImmoweltAtRealEstatePage(RealEstatePage):
    """
    Handles scraping the of real estate objects
    from https://www.immowelt.at/
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
        # No EPC data available on Immowelt
        return None

    @property
    def epc_issued_date(self) -> Optional[datetime]:
        # No EPC data available on Immowelt
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
