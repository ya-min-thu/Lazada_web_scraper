"""
Utility functions for the Lazada scraper
"""

import asyncio
import logging
import re
from functools import wraps
from pathlib import Path
from typing import Callable, Union


def setup_logging(level: str = 'INFO'):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('scraper.log')
        ]
    )


def ensure_output_directory(path: Path):
    """Ensure output directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def retry_async(max_retries: int = 3, delay: float = 1, backoff: float = 2):
    """Async retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    logger = logging.getLogger(func.__module__)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {current_delay}s..."
                    )
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
        
        return wrapper
    return decorator


def retry_sync(max_retries: int = 3, delay: float = 1, backoff: float = 2):
    """Sync retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    logger = logging.getLogger(func.__module__)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {current_delay}s..."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
        
        return wrapper
    return decorator


def clean_text(text: str) -> str:
    """Clean and normalize text data."""
    if not text:
        return ''
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause CSV issues
    text = re.sub(r'[^\w\s\-.,()&+/]', '', text)
    
    return text


def extract_number(text: str) -> Union[int, float]:
    """Extract number from text string."""
    if not text:
        return 0
    
    # Remove common number separators and extract digits
    cleaned = re.sub(r'[^\d.,]', '', text)
    
    if not cleaned:
        return 0
    
    try:
        # Handle different decimal separators
        if ',' in cleaned and '.' in cleaned:
            # Assume comma is thousands separator
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Could be decimal separator in some locales
            if cleaned.count(',') == 1 and len(cleaned.split(',')[1]) <= 2:
                cleaned = cleaned.replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        
        # Try to convert to appropriate number type
        if '.' in cleaned:
            return float(cleaned)
        else:
            return int(cleaned)
            
    except ValueError:
        return 0


def parse_price(price_text: str) -> float:
    """Parse price from text string."""
    if not price_text:
        return 0.0
    
    # Remove various currency symbols: S$, ₱, ₹, ฿, RM, etc.
    cleaned = re.sub(r'[S$₱₹฿RM\s,]', '', price_text)
    
    # Extract number
    number = extract_number(cleaned)
    return float(number) if number else 0.0


def format_currency(amount: float, currency: str = 'SGD') -> str:
    """Format amount as currency string."""
    return f"{currency} {amount:,.2f}"


def safe_divide(numerator: float, denominator: float) -> float:
    """Safely divide two numbers, returning 0 if denominator is 0."""
    try:
        return numerator / denominator if denominator != 0 else 0.0
    except (TypeError, ZeroDivisionError):
        return 0.0


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis."""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + '...'


def validate_url(url: str) -> bool:
    """Validate if string is a proper URL."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)',  # path
        re.IGNORECASE  # <-- THIS should be passed to re.compile, not in the string
    )
    return url_pattern.match(url) is not None


def get_file_size_mb(filepath: Path) -> float:
    """Get file size in megabytes."""
    try:
        size_bytes = filepath.stat().st_size
        return size_bytes / (1024 * 1024)
    except (OSError, FileNotFoundError):
        return 0.0


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename
    