"""Model classes to represent Real Estate data."""
from typing import Literal, TypedDict, Union

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


class RealEstate(TypedDict):
    """Real Estate listing information."""

    url: str
    location: Location
    listing_type: ListingType
    area: float
    price: Price
    epc_label: str
    heating_demand: float
