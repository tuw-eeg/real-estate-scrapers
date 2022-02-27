"""Model class to represent a ``RealEstate`` ``dict`` in the database."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore

from real_estate_scrapers.models.models import RealEstate

SQLBaseModel = declarative_base()


class RealEstateDBItem(SQLBaseModel):  # type: ignore
    """SQLAlchemy model class to represent a ``RealEstate``"""

    __tablename__ = "real_estate_items"

    id = Column(Integer, primary_key=True)
    location_country = Column(String)
    location_city = Column(String)
    location_zip_code = Column(String)
    listing_type = Column(String)
    area = Column(Float, nullable=True)
    price_amount = Column(Float, nullable=True)
    price_unit = Column(String, nullable=True)
    epc_data_heating_demand_energy_class = Column(String, nullable=True)
    epc_data_heating_demand_value = Column(Float, nullable=True)
    epc_data_energy_efficiency_energy_class = Column(String, nullable=True)
    epc_data_energy_efficiency_value = Column(Float, nullable=True)
    epc_data_epc_pdf_url = Column(String, nullable=True)
    epc_data_epc_issued_date = Column(DateTime, nullable=True)
    item_metadata_date_built = Column(DateTime, nullable=True)
    item_metadata_type = Column(String)
    scrape_metadata_url = Column(String)
    scrape_metadata_timestamp = Column(DateTime)

    @staticmethod
    def from_dict(dct: RealEstate) -> "RealEstateDBItem":
        """
        Convert a ``RealEstate`` ``dict`` to a ``RealEstateDBItem``.

        Args:
            dct: The ``RealEstate`` ``dict`` to convert.

        Returns: The converted ``RealEstateDBItem``.
        """
        return RealEstateDBItem(
            location_country=dct["location"]["country"],
            location_city=dct["location"]["city"],
            location_zip_code=dct["location"]["zip_code"],
            listing_type=dct["listing_type"],
            area=dct["area"],
            price_amount=dct["price"] and dct["price"]["amount"] or None,
            price_unit=dct["price"] and dct["price"]["unit"] or None,
            epc_data_heating_demand_energy_class=dct["epc_data"]["heating_demand"]
            and dct["epc_data"]["heating_demand"]["energy_class"]
            or None,
            epc_data_heating_demand_value=dct["epc_data"]["heating_demand"]
            and dct["epc_data"]["heating_demand"]["value"]
            or None,
            epc_data_energy_efficiency_energy_class=dct["epc_data"]["energy_efficiency"]
            and dct["epc_data"]["energy_efficiency"]["energy_class"]
            or None,
            epc_data_energy_efficiency_value=dct["epc_data"]["energy_efficiency"]
            and dct["epc_data"]["energy_efficiency"]["value"]
            or None,
            epc_data_epc_pdf_url=dct["epc_data"]["epc_pdf_url"],
            epc_data_epc_issued_date=dct["epc_data"]["epc_issued_date"],
            item_metadata_date_built=dct["item_metadata"]["date_built"],
            item_metadata_type=dct["item_metadata"]["type"],
            scrape_metadata_url=dct["scrape_metadata"]["url"],
            scrape_metadata_timestamp=datetime.fromtimestamp(dct["scrape_metadata"]["timestamp"]),
        )
