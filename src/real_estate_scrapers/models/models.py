"""Model classes to represent Real Estate data."""
from datetime import datetime
from typing import Literal, Optional, TypedDict, Union


class Location(TypedDict):
    """Location information for a listing."""

    country: str
    city: str
    zip_code: str


ListingType = Union[Literal["sale"], Literal["rent"]]


class Price(TypedDict):
    """Price information for a listing."""

    amount: float
    unit: str


class EnergyData(TypedDict):
    """Energy data for a listing."""

    energy_class: Optional[str]
    value: Optional[float]


class EPCData(TypedDict):
    """EPC data for a listing."""

    heating_demand: Optional[EnergyData]
    energy_efficiency: Optional[EnergyData]
    epc_pdf_url: Optional[str]
    epc_issued_date: Optional[datetime]


class RealEstateMetadata(TypedDict):
    """Metadata about a Real Estate object."""

    date_built: Optional[datetime]
    type: str


class ScrapeMetadata(TypedDict):
    """Metadata for a scrape."""

    url: str
    timestamp: float


class RealEstate(TypedDict):
    """Real Estate listing information."""

    location: Location
    listing_type: ListingType
    area: Optional[float]
    price: Optional[Price]
    epc_data: EPCData
    item_metadata: RealEstateMetadata
    scrape_metadata: ScrapeMetadata
