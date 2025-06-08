"""
A production-ready web scraper for product scraping from Lazada.sg.

Author: Ya Min Thu
"""

__version__ = "1.0.0"
__author__ = "Ya Min Thu"

from .scraper import LazadaScraper
from .analyzer import DataAnalyzer
from .config import Config
from .utils import (
    setup_logging,
    ensure_output_directory,
    clean_text,
    parse_price,
    format_currency,
    retry_async,
    retry_sync
)

__all__ = [
    'LazadaScraper',
    'DataAnalyzer', 
    'Config',
    'setup_logging',
    'ensure_output_directory',
    'clean_text',
    'parse_price',
    'format_currency',
    'retry_async',
    'retry_sync'
]