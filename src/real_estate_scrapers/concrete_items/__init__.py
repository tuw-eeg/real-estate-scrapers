"""
Exposing concrete items dynamically.
Makes it possible to add support for a new website just by
creating a new Python module under this package, and declaring
a concrete implementation for ``RealEstateListPage`` and ``RealEstatePage``.
"""
import importlib.util
import inspect
import pkgutil
from pathlib import Path
from typing import Dict, List, Type

from loguru import logger
from web_poet import WebPage  # type: ignore

from real_estate_scrapers.items import RealEstateListPage, RealEstatePage

_start_url_dict: Dict[Type[RealEstateListPage], List[str]] = {}
_scrapy_poet_overrides: Dict[str, Dict[Type[WebPage], Type[WebPage]]] = {}

_dirpath = Path(__file__).parent
# Iterates over each module in this package
# and registers the concrete crawling logic implementations
for module_info in pkgutil.iter_modules([str(_dirpath)]):
    # Load module which declares concrete implementation
    # for ``RealEstateListPage`` and ``RealEstatePage``
    full_module_name = f"{__package__}.{module_info.name}"
    full_module_path = _dirpath / f"{module_info.name}.py"
    spec = importlib.util.spec_from_file_location(full_module_name, str(full_module_path))
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    # Extract classes
    classes = inspect.getmembers(module, inspect.isclass)
    # Filter for the needed subclasses
    list_page_class = [
        cls for _, cls in classes if issubclass(cls, RealEstateListPage) and cls is not RealEstateListPage
    ][0]
    page_class = [cls for _, cls in classes if issubclass(cls, RealEstatePage) and cls is not RealEstatePage][0]
    logger.debug(
        f"Found concrete implementations in {full_module_name}: " f"{list_page_class.__name__}, {page_class.__name__}"
    )
    _scrapy_poet_overrides[list_page_class.domain()] = {
        RealEstateListPage: list_page_class,
        RealEstatePage: page_class,
    }
    _start_url_dict[list_page_class] = list_page_class.start_urls()
    logger.info(f"Loaded {full_module_name} for {list_page_class.domain()}")


def get_scrapy_poet_overrides() -> Dict[str, Dict[Type[WebPage], Type[WebPage]]]:
    """
    Returns: Configuration to override the exact ``RealEstateListPage``
             and ``RealEstatePage`` implementation dynamically
             based on the scraped domain.
    """
    return _scrapy_poet_overrides


def get_start_urls() -> List[str]:
    """
    Returns: The start urls for the scrapy crawler.
    """
    return [url for url_list in _start_url_dict.values() for url in url_list]


def get_start_url_dict() -> Dict[Type[RealEstateListPage], List[str]]:
    """
    Returns: The start urls for the scrapy crawler, grouped by subclasses of ``RealEstateListPage``.
    """
    return _start_url_dict
