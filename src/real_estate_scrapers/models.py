"""Model classes to represent Real Estate data."""
from typing import Literal, Optional, TypedDict, Union

ListingType = Union[Literal["sale"], Literal["rent"]]


class Price(TypedDict):
    """Price information for a listing."""

    amount: float
    currency: str


class Location(TypedDict):
    """Location information for a listing."""

    country: str
    city: str
    zip_code: str


class EnergyData(TypedDict):
    """Energy data for a listing."""

    energy_class: Optional[str]
    value: Optional[float]


class ScrapeMetadata(TypedDict):
    """Metadata for a scrape."""

    url: str
    timestamp: str


class RealEstate(TypedDict):
    """Real Estate listing information."""

    location: Location
    listing_type: ListingType
    area: Optional[float]
    price: Optional[Price]
    heating_demand: Optional[EnergyData]
    energy_efficiency: Optional[EnergyData]
    scrape_metadata: ScrapeMetadata
