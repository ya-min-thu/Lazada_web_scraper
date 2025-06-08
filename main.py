#!/usr/bin/env python3
"""
Lazada Singapore Product Scraper
Main script for extracting product data from Lazada.sg

Author: Ya Min Thu
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from src.scraper import LazadaScraper
from src.analyzer import DataAnalyzer
from src.config import Config
from src.utils import setup_logging, ensure_output_directory


async def main():
    """Main entry point for the scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape product data from Lazada Singapore"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Maximum number of pages to scrape (default: 10)"
    )
    parser.add_argument(
        "--min-price",
        type=float,
        default=0,
        help="Minimum price filter in SGD (default: 0)"
    )
    parser.add_argument(
        "--max-price",
        type=float,
        default=float('inf'),
        help="Maximum price filter in SGD (default: no limit)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Output directory for CSV file (default: output)"
    )
    parser.add_argument(
        "--log-level",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--headless",
        action='store_true',
        help="Run browser in headless mode (default: True)"
    )
    parser.add_argument(
        "--analyze",
        action='store_true',
        help="Perform data analysis after scraping"
    )
    parser.add_argument(
        "--category",
        type=str,
        default="electronics",
        help="Product category to scrape (default: electronics)"
    )
    parser.add_argument(
        "--search-query",
        type=str,
        help="Custom search query (overrides category if provided)"
    )

    parser.add_argument(
        "--include-keywords",
        "--include-words",  # Added alias
        type=str,
        help="Keywords that products must contain (comma-separated or space-separated)"
    )
    parser.add_argument(
        "--exclude-keywords",
        "--exclude-words",  # Added alias for consistency
        type=str,
        help="Keywords to exclude from products (comma-separated or space-separated)"
    )
    parser.add_argument(
        "--min-rating",
        type=float,
        default=0.0,
        help="Minimum product rating filter (default: 0.0)"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Direct URL to scrape (overrides category and search-query)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Ensure output directory exists
    output_path = Path(args.output_dir)
    ensure_output_directory(output_path)
    
    # Determine search parameters
    search_query = args.search_query or args.category
    if args.url:
        logger.info(f"Using direct URL: {args.url}")
    elif args.search_query:
        logger.info(f"Using custom search query: {args.search_query}")
    else:
        logger.info(f"Using category: {args.category}")
    
    # Update config with command line arguments
    config = Config()
    config.MAX_PAGES = args.max_pages
    config.MIN_PRICE = args.min_price
    config.MAX_PRICE = args.max_price
    config.OUTPUT_DIR = str(output_path)
    config.HEADLESS = args.headless
    
    # Fixed: Proper handling of include/exclude keywords
    if args.include_keywords:
        # Handle both comma-separated and space-separated keywords
        if ',' in args.include_keywords:
            keywords = [kw.strip().lower() for kw in args.include_keywords.split(',')]
        else:
            keywords = [kw.strip().lower() for kw in args.include_keywords.split()]
        config.INCLUDE_KEYWORDS = keywords
        logger.info(f"Include keywords: {keywords}")
    
    if args.exclude_keywords:
        # Handle both comma-separated and space-separated keywords
        if ',' in args.exclude_keywords:
            keywords = [kw.strip().lower() for kw in args.exclude_keywords.split(',')]
        else:
            keywords = [kw.strip().lower() for kw in args.exclude_keywords.split()]
        config.EXCLUDE_KEYWORDS = keywords
        logger.info(f"Exclude keywords: {keywords}")
    
    logger.info("Starting Lazada product scraper...")
    logger.info(f"Configuration: max_pages={args.max_pages}, "
                f"search_query='{search_query}', "
                f"price_range=[{args.min_price}, {args.max_price}], "
                f"sort=popularity") # can scale up to other sorting options in future
    
    try:
        # Initialize and run scraper using async context manager
        async with LazadaScraper(config) as scraper:
            # Check what methods the scraper supports
            if hasattr(scraper, 'scrape_products_with_query'):
                # If scraper has been updated to support search queries
                products = await scraper.scrape_products_with_query(search_query)
            elif args.url and hasattr(scraper, 'scrape_from_url'):
                # If scraper has scrape_from_url method, use it
                products = await scraper.scrape_from_url(args.url)
            else:
                # Fallback: set search query in config and use existing method
                config.SEARCH_QUERY = search_query
                if args.url:
                    config.CUSTOM_URL = args.url
                
                # Use existing scrape_products method (should work with updated config)
                products = await scraper.scrape_products()
            
            if not products:
                logger.error("No products were scraped. Exiting.")
                sys.exit(1)
            
            # Generate filename based on search parameters
            filename_parts = []
            if args.search_query:
                filename_parts.append(args.search_query.replace(' ', '_').lower())
            else:
                filename_parts.append(args.category.replace(' ', '_').lower())
            
            csv_filename = f"{'_'.join(filename_parts)}_products.csv"
            csv_path = output_path / csv_filename
            await scraper.save_to_csv(products, csv_path)
        
        logger.info(f"Successfully scraped {len(products)} products")
        logger.info(f"Data saved to: {csv_path}")
        
        # Perform analysis if requested
        if args.analyze:
            logger.info("Performing data analysis...")
            analyzer = DataAnalyzer(products)
            analysis_results = analyzer.analyze()
            
            # Save analysis results
            analysis_filename = csv_filename.replace('.csv', '_analysis_summary.txt')
            analysis_path = output_path / analysis_filename
            analyzer.save_analysis(analysis_results, analysis_path)
            logger.info(f"Analysis saved to: {analysis_path}")
        
        logger.info("Scraping completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())