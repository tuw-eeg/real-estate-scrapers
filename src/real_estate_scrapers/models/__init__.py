"""Package containing the in-app models and their respective db models."""
from real_estate_scrapers.models.db_models import RealEstateDBItem, SQLBaseModel
from real_estate_scrapers.models.models import (
    EnergyData,
    EPCData,
    ListingType,
    Location,
    Price,
    RealEstate,
    RealEstateMetadata,
    ScrapeMetadata,
)

__all__ = [
    "EnergyData",
    "ListingType",
    "Location",
    "Price",
    "RealEstate",
    "EPCData",
    "RealEstateMetadata",
    "ScrapeMetadata",
    "RealEstateDBItem",
    "SQLBaseModel",
]
