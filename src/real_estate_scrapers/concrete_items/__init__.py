"""
Exposing concrete items dynamically.
Makes it possible to add support for a new website just by
creating a new Python module under this package, and declaring
a concrete implementation for ``RealEstateHomePage``, ``RealEstateListPage`` and ``RealEstatePage``.
"""
import importlib.util
import inspect
import pkgutil
from pathlib import Path
from typing import Dict, List, Tuple, Type, TypeVar

from loguru import logger
from web_poet import WebPage  # type: ignore

from real_estate_scrapers.items import RealEstateHomePage, RealEstateListPage, RealEstatePage

T = TypeVar("T", bound=WebPage)


def _get_concrete_class(class_tuples: List[Tuple[str, Type[T]]], abstract_class: Type[T]) -> Type[T]:
    """
    Returns the concrete implementation of the specified ``abstract_class``, choosing from ``class_tuples``.

    ``class_tuples`` can be easily obtained by invoking:

    >>> inspect.getmembers(module, inspect.isclass)

    Args:
        class_tuples: List of tuples of the form (module_name, class_name)
        abstract_class: The abstract class whose concrete implementation is to be found.

    Returns: The concrete implementation of the specified ``abstract_class``. Always the first match gets returned.

    Raises: ``ValueError`` if no concrete implementation is found.
    """
    for _, cls in class_tuples:
        if issubclass(cls, abstract_class) and cls is not abstract_class:
            return cls
    raise ValueError(f"No concrete implementation found for {abstract_class.__name__}")


# Used to have a grouping of URLs per page, so that request types can be specified dynamically (e.g. Selenium or plain)
_start_url_dict: Dict[Type[RealEstateHomePage], List[str]] = {}

# Will be assigned to the ``SCRAPY_POET_OVERRIDES`` class variable in the ``RealEstateSpider``
_scrapy_poet_overrides: Dict[str, Dict[Type[WebPage], Type[WebPage]]] = {}

# Loading concrete implementations from the file system automagically
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

    home_page_class: Type[RealEstateHomePage] = _get_concrete_class(classes, RealEstateHomePage)
    list_page_class: Type[RealEstateListPage] = _get_concrete_class(classes, RealEstateListPage)
    page_class: Type[RealEstatePage] = _get_concrete_class(classes, RealEstatePage)
    domain_specific_overrides = {
        RealEstateHomePage: home_page_class,
        RealEstateListPage: list_page_class,
        RealEstatePage: page_class,
    }
    # Sets the override dict in ``SCRAPY_OVERRIDES`` so that ``scrapy_poet.InjectionMiddleware`` can inject the proper
    # concrete implementation for each page type on a per-domain basis
    domain = home_page_class.domain()
    _scrapy_poet_overrides[domain] = domain_specific_overrides
    logger.debug(f"Registered overrides for {domain}: {domain_specific_overrides}")

    # Register the static (hard-coded) start urls for this domain,
    # to be used as entrypoint(s) to scrape urls to ``RealEstateListPage``s
    _start_url_dict[home_page_class] = home_page_class.start_urls()
    logger.info(f"Loaded {full_module_name} for {domain}")


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


def get_start_url_dict() -> Dict[Type[RealEstateHomePage], List[str]]:
    """
    Returns: The start urls for the scrapy crawler, grouped by subclasses of ``RealEstateListPage``.
    """
    return _start_url_dict
