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
    heating_demand_energy_class = Column(String, nullable=True)
    heating_demand_value = Column(Float, nullable=True)
    energy_efficiency_energy_class = Column(String, nullable=True)
    energy_efficiency_value = Column(Float, nullable=True)
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
            heating_demand_energy_class=dct["heating_demand"] and dct["heating_demand"]["energy_class"] or None,
            heating_demand_value=dct["heating_demand"] and dct["heating_demand"]["value"] or None,
            energy_efficiency_energy_class=dct["energy_efficiency"]
            and dct["energy_efficiency"]["energy_class"]
            or None,
            energy_efficiency_value=dct["energy_efficiency"] and dct["energy_efficiency"]["value"] or None,
            scrape_metadata_url=dct["scrape_metadata"]["url"],
            scrape_metadata_timestamp=datetime.fromtimestamp(dct["scrape_metadata"]["timestamp"]),
        )

    def __repr__(self) -> str:
        """Object representation."""
        return (
            f"<RealEstateDBItem(id={self.id}, "
            f"location_country={self.location_country}, "
            f"location_city={self.location_city}, "
            f"location_zip_code={self.location_zip_code}, "
            f"listing_type={self.listing_type}, "
            f"area={self.area}, "
            f"price_amount={self.price_amount}, "
            f"price_unit={self.price_unit}, "
            f"heating_demand_energy_class={self.heating_demand_energy_class}, "
            f"heating_demand_value={self.heating_demand_value}, "
            f"energy_efficiency_energy_class={self.energy_efficiency_energy_class}, "
            f"energy_efficiency_value={self.energy_efficiency_value}, "
            f"scrape_metadata_url={self.scrape_metadata_url}, "
            f"scrape_metadata_timestamp={self.scrape_metadata_timestamp})>"
        )
