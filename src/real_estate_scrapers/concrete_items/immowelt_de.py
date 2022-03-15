"""Scraper specification for https://www.immowelt.de/"""
from datetime import datetime
from typing import List, Optional

from real_estate_scrapers.items import RealEstateListPage, RealEstatePage
from real_estate_scrapers.models import EnergyData, ListingType

real_estate_type_map = {
    "haeuser": "Haus",
    "wohnungen": "Wohnung",
    "wohnen-auf-zeit": "Wohnung",
}


class ImmoweltDeRealEstateListPage(RealEstateListPage):
    """
    Handles scraping the urls of ``ImmoweltDeRealEstatePage`` objects
    from https://www.immowelt.de/.
    """

    @staticmethod
    def domain() -> str:
        return "immowelt.de"

    @staticmethod
    def start_urls() -> List[str]:
        places = [
            "berlin",
            "bielefeld",
            "bochum",
            "bonn",
            "bremen",
            "dortmund",
            "dresden",
            "duisburg",
            "duesseldorf",
            "essen",
            "frankfurt-am-main",
            "hamburg",
            "hannover",
            "koeln",
            "leipzig",
            "mannheim",
            "muenchen",
            "nuernberg",
            "stuttgart",
            "wuppertal",
            "aachen",
            "augsburg",
            "bergisch-gladbach",
            "bocholt",
            "bottrop",
            "braunschweig",
            "bremerhaven",
            "chemnitz-sachs",
            "cottbus",
            "darmstadt",
            "dessau",
            "dueren-rheinl",
            "erfurt",
            "erlangen",
            "esslingen",
            "flensburg",
            "freiburg-im-breisgau",
            "fuerth",
            "gelsenkirchen",
            "gera",
            "giessen-lahn",
            "goettingen-niedersachs",
            "guetersloh",
            "hagen",
            "halle-saale",
            "hamm",
            "hanau",
            "heidelberg",
            "heilbronn",
            "herne",
            "hildesheim",
            "ingolstadt",
            "iserlohn",
            "jena",
            "kaiserslautern",
            "karlsruhe",
            "kassel",
            "kiel",
            "krefeld",
            "koblenz",
            "konstanz",
            "landshut",
            "leverkusen",
            "ludwigsburg-wuertt",
            "ludwigshafen-am-rhein",
            "luebeck-hansestadt",
            "luenen",
            "magdeburg",
            "mainz",
            "marburg",
            "marl-westf",
            "minden-westf",
            "moers",
            "muelheim-an-der-ruhr",
            "moenchengladbach",
            "muenster",
            "neuss",
            "oberhausen",
            "offenbach-am-main",
            "oldenburg-oldenburg",
            "osnabrueck",
            "paderborn",
            "pforzheim",
            "potsdam",
            "ratingen",
            "recklinghausen-westf",
            "regensburg",
            "remscheid",
            "reutlingen",
            "rosenheim",
            "rostock",
            "saarbruecken",
            "salzgitter",
            "schwerin",
            "siegen",
            "solingen",
            "straubing",
            "trier",
            "tuebingen",
            "ulm",
            "velbert",
            "villingen-schwenningen",
            "weimar-thuer",
            "wiesbaden",
            "wilhelmshaven",
            "witten",
            "wolfsburg",
            "worms",
            "wuerzburg",
            "zwickau",
        ]
        objects = real_estate_type_map.keys()
        listing_links = [f"https://www.immowelt.de/liste/{place}/{obj}" for place in places for obj in objects]
        paginated_links = [f"{link}?sp={page}" for link in listing_links for page in range(2, 201)]
        return [*listing_links, *paginated_links]

    @property
    def real_estate_urls(self) -> List[str]:
        return list(self.xpath('//a[starts-with(@href, "https://www.immowelt.de/expose")]/@href').getall())


class ImmoweltDeRealEstatePage(RealEstatePage):
    """
    Handles the scraping of single real estate objects
    from https://www.immowelt.de/
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
