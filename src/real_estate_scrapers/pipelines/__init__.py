"""Scrapy Pipelines"""
from real_estate_scrapers.pipelines.duplicates_pipeline import DuplicatesPipeline
from real_estate_scrapers.pipelines.postgres_pipeline import PostgresPipeline

__all__ = ["PostgresPipeline", "DuplicatesPipeline"]
