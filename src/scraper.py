"""
Core scraper module for Lazada Singapore
Handles the main scraping logic using Playwright for any product category
"""

import asyncio
import csv
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import aiohttp
from playwright.async_api import async_playwright, TimeoutError

from .config import Config
from .utils import retry_async, clean_text, extract_number, parse_price


class LazadaScraper:
    """Main scraper class for Lazada products."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = None
        self.browser = None
        self.page = None
        self.current_search_query = None
        self.current_category = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.setup()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        
    async def setup(self):
        """Initialize browser and session."""
        self.logger.info("Setting up Lazada scraper...")
        
        # Initialize aiohttp session
        self.session = aiohttp.ClientSession()
        
        # Initialize Playwright with additional args for Lazada
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.config.HEADLESS,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create new page with realistic settings
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self.config.get_random_user_agent()
        )
        
        self.page = await context.new_page()
        
        # Additional stealth measures for Lazada
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        # Set timeouts
        self.page.set_default_timeout(self.config.BROWSER_TIMEOUT)
        
    async def cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up resources...")
        
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        if self.session:
            await self.session.close()
    
    @retry_async(max_retries=3, delay=3)
    async def scrape_products(self, search_query: str = None) -> List[Dict[str, Any]]:
        """Main method to scrape product data based on search query or category."""
        if not self.browser:
            await self.setup()
        
        # Use provided search query or fall back to config
        if search_query:
            self.current_search_query = search_query
        else:
            self.current_search_query = getattr(self.config, 'SEARCH_QUERY', 'electronics')
        
        self.current_category = self.current_search_query
        all_products = []
        
        try:
            # Determine the URL to navigate to
            if hasattr(self.config, 'CUSTOM_URL') and self.config.CUSTOM_URL:
                url = self.config.CUSTOM_URL
                self.logger.info(f"Using custom URL: {url}")
            elif self.current_search_query in self.config.CATEGORY_URLS:
                url = self.config.CATEGORY_URLS[self.current_search_query]
                self.logger.info(f"Using category URL for '{self.current_search_query}': {url}")
            else:
                url = self.config.get_search_url(self.current_search_query)
                self.logger.info(f"Using search URL for query '{self.current_search_query}': {url}")
            
            # Navigate to the URL
            self.logger.info(f"Navigating to: {url}")
            await self.page.goto(url, 
                               wait_until='domcontentloaded',
                               timeout=self.config.PAGE_LOAD_TIMEOUT)
            
            # Wait for initial content and handle potential popups
            await self.handle_popups()
            await asyncio.sleep(5)  # Longer wait for Lazada
            
            page_num = 1
            products_scraped = 0
            
            while (page_num <= self.config.MAX_PAGES and 
                   products_scraped < self.config.MIN_PRODUCTS_TARGET):
                
                self.logger.info(f"Scraping page {page_num}...")
                
                # Wait for products to load
                await self.wait_for_products_to_load()
                
                # Scrape current page using DOM parsing
                page_products = await self.scrape_via_dom()
                
                if not page_products:
                    self.logger.warning(f"No products found on page {page_num}")
                    # Try scrolling to load more products
                    if not await self.scroll_and_load_more():
                        break
                    page_products = await self.scrape_via_dom()
                
                if not page_products:
                    self.logger.warning("Still no products after scroll, ending scrape")
                    break
                
                # Filter products by price and other criteria
                filtered_products = self.filter_products(page_products)
                all_products.extend(filtered_products)
                products_scraped += len(filtered_products)
                
                self.logger.info(f"Found {len(filtered_products)} products on page {page_num}")
                self.logger.info(f"Total products scraped: {products_scraped}")
                
                # Navigate to next page
                if page_num < self.config.MAX_PAGES:
                    success = await self.navigate_to_next_page()
                    if not success:
                        self.logger.info("No more pages available")
                        break
                
                page_num += 1
                
                # Random delay between pages
                delay = self.config.get_request_delay()
                await asyncio.sleep(delay)
            
            self.logger.info(f"Scraping completed. Total products: {len(all_products)}")
            return all_products
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            raise
    
    async def scrape_products_with_query(self, search_query: str) -> List[Dict[str, Any]]:
        """Scrape products with a specific search query."""
        return await self.scrape_products(search_query)
    
    async def scrape_from_url(self, url: str) -> List[Dict[str, Any]]:
        """Scrape products from a specific URL."""
        if not self.browser:
            await self.setup()
        
        all_products = []
        
        try:
            self.logger.info(f"Navigating to URL: {url}")
            await self.page.goto(url, 
                               wait_until='domcontentloaded',
                               timeout=self.config.PAGE_LOAD_TIMEOUT)
            
            # Wait for initial content and handle potential popups
            await self.handle_popups()
            await asyncio.sleep(5)
            
            page_num = 1
            products_scraped = 0
            
            while (page_num <= self.config.MAX_PAGES and 
                   products_scraped < self.config.MIN_PRODUCTS_TARGET):
                
                self.logger.info(f"Scraping page {page_num}...")
                
                # Wait for products to load
                await self.wait_for_products_to_load()
                
                # Scrape current page using DOM parsing
                page_products = await self.scrape_via_dom()
                
                if not page_products:
                    self.logger.warning(f"No products found on page {page_num}")
                    if not await self.scroll_and_load_more():
                        break
                    page_products = await self.scrape_via_dom()
                
                if not page_products:
                    self.logger.warning("Still no products after scroll, ending scrape")
                    break
                
                # Filter products
                filtered_products = self.filter_products(page_products)
                all_products.extend(filtered_products)
                products_scraped += len(filtered_products)
                
                self.logger.info(f"Found {len(filtered_products)} products on page {page_num}")
                self.logger.info(f"Total products scraped: {products_scraped}")
                
                # Navigate to next page
                if page_num < self.config.MAX_PAGES:
                    success = await self.navigate_to_next_page()
                    if not success:
                        self.logger.info("No more pages available")
                        break
                
                page_num += 1
                
                # Random delay between pages
                delay = self.config.get_request_delay()
                await asyncio.sleep(delay)
            
            self.logger.info(f"Scraping completed. Total products: {len(all_products)}")
            return all_products
            
        except Exception as e:
            self.logger.error(f"Error during URL scraping: {str(e)}")
            raise

    async def handle_popups(self):
        """Handle Lazada popups and overlays."""
        try:
            # Close cookie banner
            cookie_accept = await self.page.query_selector('[data-qa-locator="cookie-accept"]')
            if cookie_accept:
                await cookie_accept.click()
                await asyncio.sleep(1)
            
            # Close promotional popups
            popup_close = await self.page.query_selector('.mui-dialog-close, .close-btn, [data-qa-locator="popup-close"]')
            if popup_close:
                await popup_close.click()
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.debug(f"Error handling popups: {str(e)}")
    
    async def wait_for_products_to_load(self):
        """Wait for product cards to load on the page."""
        try:
            # Try primary selector first
            await self.page.wait_for_selector(
                self.config.SELECTORS['product_card'], 
                timeout=15000
            )
        except TimeoutError:
            # Try backup selector
            try:
                await self.page.wait_for_selector(
                    self.config.BACKUP_SELECTORS['product_card'], 
                    timeout=10000
                )
            except TimeoutError:
                self.logger.warning("Products failed to load with both selectors")
    
    async def scroll_and_load_more(self) -> bool:
        """Scroll page to load more products (for infinite scroll)."""
        try:
            # Get initial product count
            initial_count = len(await self.page.query_selector_all(
                f"{self.config.SELECTORS['product_card']}, {self.config.BACKUP_SELECTORS['product_card']}"
            ))
            
            # Scroll to bottom
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)
            
            # Check if more products loaded
            new_count = len(await self.page.query_selector_all(
                f"{self.config.SELECTORS['product_card']}, {self.config.BACKUP_SELECTORS['product_card']}"
            ))
            
            return new_count > initial_count
            
        except Exception as e:
            self.logger.error(f"Error during scroll and load: {str(e)}")
            return False
    
    async def scrape_via_dom(self) -> List[Dict[str, Any]]:
        """Scraping method using DOM parsing for Lazada."""
        products = []
        
        try:
            # Try primary selectors first
            product_cards = await self.page.query_selector_all(self.config.SELECTORS['product_card'])
            
            # Fallback to backup selectors if needed
            if not product_cards:
                product_cards = await self.page.query_selector_all(self.config.BACKUP_SELECTORS['product_card'])
            
            self.logger.info(f"Found {len(product_cards)} product cards")
            
            for i, card in enumerate(product_cards):
                try:
                    product = await self.extract_product_from_card(card)
                    if product:
                        products.append(product)
                        self.logger.debug(f"Extracted product {i+1}: {product.get('product_name', '')[:50]}...")
                except Exception as e:
                    self.logger.warning(f"Error extracting product from card {i+1}: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"DOM scraping error: {str(e)}")
        
        return products
    
    async def extract_product_from_card(self, card) -> Optional[Dict[str, Any]]:
        """Extract product data from a Lazada product card element."""
        try:
            # Extract product name (try multiple selectors)
            name = await self.extract_text_with_fallback(card, [
                self.config.SELECTORS['product_name'],
                self.config.SELECTORS['product_title'],
                self.config.BACKUP_SELECTORS['product_name'],
                'a[title]'
            ])
            
            if not name:
                return None
            
            # Extract current price
            current_price_text = await self.extract_text_with_fallback(card, [
                self.config.SELECTORS['current_price'],
                self.config.SELECTORS['price'],
                self.config.BACKUP_SELECTORS['price']
            ])
            current_price = parse_price(current_price_text) if current_price_text else 0.0
            
            # Extract shop name / discount tag line
            discount_tag_line = await self.extract_text_with_fallback(card, [
                self.config.SELECTORS['discount_tag_line'],
                self.config.BACKUP_SELECTORS['discount_tag_line']
            ])
            
            # Extract discount information
            discount_amount = 'unknown'
            if discount_tag_line and '$' in discount_tag_line:
                try:
                    discount_amount = discount_tag_line.split('$')[1].strip()
                    discount_amount = float(discount_amount)
                except (IndexError, ValueError):
                    discount_amount = 'unknown'
            
            if discount_tag_line and 'save' in discount_tag_line:
                try:
                    discount_amount = discount_tag_line.split('save')[1].strip()
                    discount_amount = float(discount_amount)
                except (IndexError, ValueError):
                    discount_amount = 'unknown'
            
            # Extract original price (for discount calculation)
            original_price_text = await self.extract_text_with_fallback(card, [
                self.config.SELECTORS['original_price'],
                self.config.BACKUP_SELECTORS['original_price']
            ])
            
            if original_price_text:
                original_price = parse_price(original_price_text)
            elif discount_amount != 'unknown':
                original_price = current_price + discount_amount
            else:
                original_price = current_price
            
            # Extract rating
            rating_text = await self.extract_text_with_fallback(card, [
                self.config.SELECTORS['star_rating'],
                self.config.BACKUP_SELECTORS['rating']
            ])
            star_rating = extract_number(rating_text) if rating_text else 0.0
            
            # Extract product URL
            link_elem = await card.query_selector('a')
            href = await link_elem.get_attribute('href') if link_elem else ''
            product_url = urljoin(self.config.BASE_URL, href) if href else ''
            
            # Extract image URL
            # img_elem = await card.query_selector(self.config.SELECTORS['product_image'])
            # image_url = await img_elem.get_attribute('src') if img_elem else ''
            
            # Check for mall product
            mall_indicator = await card.query_selector(self.config.SELECTORS['mall_indicator'])
            is_mall_product = mall_indicator is not None
            
            # Check for free shipping
            shipping_elem = await card.query_selector(self.config.SELECTORS['free_shipping'])
            free_shipping = shipping_elem is not None
            
            # Calculate discount percentage
            discount_percentage = 0.0
            if original_price and original_price > current_price:
                discount_percentage = round(((original_price - current_price) / original_price) * 100, 2)
            
            # Extract location/shipping info
            location = await self.extract_text_with_fallback(card, [
                'span.oa6ri',
                'div._6uN7R span',
                'div.buTCk span',
                '[class*="location"]',
                '[class*="shipping"]',
                '[class*="region"]',
                'span[class*="ship"]',
                'div[class*="location"] span',
                self.config.SELECTORS['location']
            ])
            
            # If no location found with selectors, try broader search
            if not location:
                location = await self.extract_location_with_text_search(card)
            
            # Extract brand using config method
            brand = self.config.extract_brand_from_name(name, self.current_category)
            
            # Separate quantity sold from location
            quantity_sold = None
            if location and 'sold' in location.lower():
                quantity_sold = location
                location = None
            
            return {
                'product_name': clean_text(name),
                'price': current_price,
                # 'original_price': original_price if original_price != current_price else None,
                'discount_percentage': discount_percentage,
                'review_count': star_rating,
                'discount_tag_line': clean_text(discount_tag_line) if discount_tag_line else '',
                'product_url': product_url,
                # 'image_url': image_url,
                'brand': brand,
                'location': location,
                'quantity_sold': quantity_sold,
                'category': self.current_category,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting product data: {str(e)}")
            return None
    
    async def extract_text_with_fallback(self, card, selectors: List[str]) -> Optional[str]:
        """Try multiple selectors to extract text, return first successful result."""
        for selector in selectors:
            try:
                elem = await card.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    if text and text.strip():
                        return text.strip()
            except Exception:
                continue
        return None
    
    async def extract_location_with_text_search(self, card) -> Optional[str]:
        """Extract location information using text-based search."""
        try:
            # Get all text content from the card
            card_text = await card.inner_text()
            
            # Look for common location indicators
            location_indicators = ['Singapore', 'Overseas', 'Local', 'sold']
            for indicator in location_indicators:
                if indicator.lower() in card_text.lower():
                    # Try to extract the line containing the location
                    lines = card_text.split('\n')
                    for line in lines:
                        if indicator.lower() in line.lower():
                            return line.strip()
            
            return None
        except Exception:
            return None
    
    async def navigate_to_next_page(self) -> bool:
        """Navigate to the next page of results."""
        try:
            # Look for next button using multiple selectors
            next_button = await self.page.query_selector(self.config.SELECTORS['next_button'])
            if not next_button:
                next_button = await self.page.query_selector(self.config.BACKUP_SELECTORS['next_button'])
            if not next_button:
                # Try generic next button selectors
                next_button = await self.page.query_selector('.ant-pagination-next:not(.ant-pagination-disabled)')
            
            if next_button:
                # Check if button is disabled
                is_disabled = await next_button.is_disabled()
                classes = await next_button.get_attribute('class') or ''
                if is_disabled or 'disabled' in classes:
                    return False
                
                # Scroll button into view and click
                await next_button.scroll_into_view_if_needed()
                await next_button.click()
                
                # Wait for page to load
                await self.page.wait_for_load_state('domcontentloaded')
                await asyncio.sleep(3)
                
                # Wait for new products to load
                await self.wait_for_products_to_load()
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error navigating to next page: {str(e)}")
            return False
    
    def filter_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter products based on config criteria."""
        filtered = []
        
        for product in products:
            price = product.get('price', 0)
            product_name = product.get('product_name', '')
            rating = product.get('rating', 0)
            
            # Use config's validation method
            if self.config.is_valid_product(product_name, price, rating):
                filtered.append(product)
        
        return filtered
    
    async def save_to_csv(self, products: List[Dict[str, Any]], filepath: Path):
        """Save products to CSV file."""
        self.logger.info(f"Saving {len(products)} products to {filepath}")
        
        if not products:
            self.logger.warning("No products to save")
            return
        
        # Ensure output directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = self.config.DATA_FIELDS
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for product in products:
                # Ensure all fields are present
                row = {field: product.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        self.logger.info(f"Successfully saved data to {filepath}")
    
    async def save_to_json(self, products: List[Dict[str, Any]], filepath: Path):
        """Save products to JSON file."""
        self.logger.info(f"Saving {len(products)} products to {filepath}")
        
        if not products:
            self.logger.warning("No products to save")
            return
        
        # Ensure output directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(products, jsonfile, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Successfully saved data to {filepath}")