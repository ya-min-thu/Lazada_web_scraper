"""
Configuration module for Lazada scraper
Contains all constants and settings for general product scraping
"""

import random
from typing import List


class Config:
    """Configuration class for scraper settings."""
    
    # Lazada URLs
    BASE_URL = "https://www.lazada.sg"
    SEARCH_URL = "https://www.lazada.sg/catalog/"  # Base search endpoint
    
    # Popular category URLs (can be extended)
    CATEGORY_URLS = {
    'electronics': 'https://www.lazada.sg/shop-electronics/',
    'mobiles-tablets': 'https://www.lazada.sg/shop-mobiles-tablets/',
    'computers-laptops': 'https://www.lazada.sg/catalog/?spm=a2o42.page-not-found.cate_2.3.6e9814f8F7MgWF&q=Laptops&from=hp_categories&src=all_channel',
    'home-living': 'https://www.lazada.sg/shop-home-living/',
    'health-beauty': 'https://www.lazada.sg/shop-health-beauty/',
    'babies-toys': 'https://www.lazada.sg/catalog/?spm=a2o42.searchlist.cate_5.9.4f122f72BhoLMP&q=Toys%20%26%20Games&from=hp_categories&src=all_channel',
    'groceries': 'https://www.lazada.sg/tag/groceries/?q=groceries&catalog_redirect_tag=true',
    'fashion-women': 'https://www.lazada.sg/tag/women-fashion/?q=women%20fashion&catalog_redirect_tag=true',
    'fashion-men': 'https://www.lazada.sg/tag/men-fashion/?q=men%20fashion&catalog_redirect_tag=true',
    'watches-accessories': 'https://www.lazada.sg/tag/watch-accessories/?q=watch%20accessories&catalog_redirect_tag=true',
    'home-fitness-equipment': 'https://www.lazada.sg/shop-home-fitness-equipment/',
    'automotive': 'https://www.lazada.sg/shop-automotive/'
}
    
    # API endpoints (if available)
    API_BASE = "https://www.lazada.sg/api/pdp/v2/"
    SEARCH_API = "https://www.lazada.sg/api/search"
    
    # Scraping settings
    MAX_PAGES = 3
    MIN_PRICE = 0
    MAX_PRICE = float('inf')
    MIN_RATING = 0.0
    ITEMS_PER_PAGE = 40  # Lazada typically shows 40 items per page
    MIN_PRODUCTS_TARGET = 100
    
    # Browser settings
    HEADLESS = False  # Set to False for debugging Lazada's anti-bot
    BROWSER_TIMEOUT = 45000  # 45 seconds (Lazada can be slower)
    PAGE_LOAD_TIMEOUT = 60000  # 60 seconds
    
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 3
    BACKOFF_FACTOR = 2
    
    # Request settings
    REQUEST_DELAY = (2, 5)  # Longer delays for Lazada
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
    ]
    
    # Output settings
    OUTPUT_DIR = "output"
    CSV_FILENAME = "lazada_products.csv"
    
    # Data fields to extract
    DATA_FIELDS = [
        'product_name',
        'price',
        'discount_percentage',
        'review_count',
        'discount_tag_line',
        'product_url',
        'brand',
        'location',
        'quantity_sold',
        'category',
        'scraped_at'
    ]
    
    # CSS Selectors for Lazada (generic for all products)
    SELECTORS = {
        # Product grid and cards
        'product_grid': '[data-qa-locator="product-grid"], .gridItem--Yd0sa',
        'product_card': '[data-qa-locator="product-item"], .gridItem--Yd0sa',
        
        # Product details
        'product_name': '[data-qa-locator="product-name"], .title--wFj93, .titleText--f74c8',
        'product_title': '.RfADt, .title--wFj93',
        
        # Price selectors
        'price': '[data-qa-locator="product-price"], .price--NVB62, .currency--GVKjl',
        'current_price': '.ooOxS, .price--NVB62, .currency--GVKjl',
        'original_price': 'span.pdp-v2-product-price-content-originalPrice-amount, .originPrice--AJxRs',
        'discount': '.IcOsH, .discount--WehBj, .discount-percent',
        
        # Rating and reviews
        'star_rating': '[data-qa-locator="product-rating"], .rating--D3lOX .average--iqiEa, .qzqFw .number, .stars-rating .rating-value',
        'star_rating_value': '.average--iqiEa, .rating-value, .star-rating-value, .rating-number',
        'star_rating_alt': '.qzqFw span:first-child, .rating--D3lOX span:first-child, .rating-container .rating-score',
        'rating_stars': '.qzqFw, .rating--D3lOX, .stars-container, .rating-stars',
        'rating_stars_filled': '.rating--D3lOX .filled, .stars-filled, .star-filled',
        'review_count': '.qzqFw + span, .count--iq2as, .ratingCount--KfjIx, .rating-count, .review-count',
        'review_count_alt': '.qzqFw span:last-child, .rating--D3lOX span:last-child, .rating-reviews',
        
        # Legacy rating (for backward compatibility)
        'rating': '[data-qa-locator="product-rating"], .rating--D3lOX, .average--iqiEa',
        
        # Shop information
        'discount_tag_line': 'a.seller-name-v2__detail-name, [data-qa-locator="seller-name"], .shopName--wEhCK, .seller-name',
        'shop_name_alt': '.WNoq3, .seller-name-v2__wrapper a, .shop-card__name',
        'mall_indicator': '.official-store, .mall--yQygL, .official-icon',
        
        # Additional info
        'free_shipping': '[data-qa-locator="shipping-info"], .freeShipping--wjIw7, .shipping-info',
        'product_image': '[data-qa-locator="product-image"] img, .image--WOxYy img, .mainImage--wJKIb img',
        'location': 'div.buTCk div._6uN7R > span.oa6ri, [data-qa-locator="location"], .location--LAzqk, .seller-location',
        
        # Navigation
        'next_button': '[data-qa-locator="pagination-next"], .ant-pagination-next, .pagination-next',
        'pagination': '.ant-pagination, .pagination--f7Tw7',
        'page_numbers': '.ant-pagination-item, .pagination-item',
        
        # Loading indicators
        'loading': '.ant-spin-spinning, .loading--hd8h1',
        'product_loading': '[data-qa-locator="product-loading"], .skeleton--loading'
    }
    
    # Enhanced backup selectors with more alternatives
    BACKUP_SELECTORS = {
        'product_card': '.Bm3ON, .gridItem--Yd0sa, .product-item',
        'product_name': '.RfADt a, .title--wFj93, .product-title',
        'price': '.ooOxS, .price--NVB62, .current-price',
        'original_price': '.originPrice--AJxRs, .was-price, .old-price, .original-price',
        'rating': '.qzqFw, .rating--D3lOX, .star-rating',
        'discount_tag_line': '.WNoq3, .shopName--wEhCK, .seller-name, .shop-name',
        'next_button': '.ant-pagination-next, .pagination-next-btn'
    }
    
    # Product filtering (initialized empty, can be set dynamically)
    INCLUDE_KEYWORDS = []  # Keywords that products must contain
    EXCLUDE_KEYWORDS = []  # Keywords to exclude from products
    BRAND_FILTER = None    # Specific brand to filter by
    
    # Predefined brand lists for common categories (can be extended)
    BRAND_LISTS = {
        'electronics': [
            'sony', 'samsung', 'lg', 'panasonic', 'philips', 'sharp', 'toshiba',
            'pioneer', 'jbl', 'bose', 'beats', 'audio-technica', 'sennheiser'
        ],
        'mobiles-tablets': [
            'apple', 'iphone', 'samsung', 'galaxy', 'huawei', 'xiaomi', 'redmi',
            'oppo', 'vivo', 'oneplus', 'google', 'pixel', 'sony', 'lg', 'motorola',
            'nokia', 'realme', 'honor', 'asus', 'poco', 'blackberry', 'tcl',
            'infinix', 'tecno', 'nothing', 'fairphone'
        ],
        'computers-laptops': [
            'dell', 'hp', 'lenovo', 'asus', 'acer', 'apple', 'macbook', 'msi',
            'alienware', 'razer', 'surface', 'microsoft', 'gigabyte', 'intel', 'amd'
        ],
        'fashion-women': [
            'nike', 'adidas', 'zara', 'h&m', 'uniqlo', 'forever21', 'mango',
            'charles & keith', 'coach', 'michael kors', 'kate spade', 'tory burch'
        ],
        'fashion-men': [
            'nike', 'adidas', 'polo ralph lauren', 'tommy hilfiger', 'calvin klein',
            'levi\'s', 'uniqlo', 'h&m', 'zara', 'boss', 'armani', 'lacoste'
        ],
        'health-beauty': [
            'olay', 'neutrogena', 'l\'oreal', 'maybelline', 'revlon', 'clinique',
            'estee lauder', 'lancome', 'shiseido', 'sk-ii', 'the ordinary', 'cerave', 'innisfree'
        ],
        'watches-accessories': [
            'rolex', 'omega', 'tag heuer', 'tissot', 'seiko', 'citizen', 'casio',
            'apple watch', 'samsung gear', 'fitbit', 'garmin', 'fossil', 'daniel wellington'
        ],
        'sports-outdoor': [
            'nike', 'adidas', 'under armour', 'puma', 'reebok', 'new balance',
            'asics', 'mizuno', 'yonex', 'wilson', 'spalding', 'coleman', 'the north face'
        ]
    }
    
    # Category-specific keywords for better filtering
    CATEGORY_KEYWORDS = {
        'electronics': ['tv', 'television', 'speaker', 'headphone', 'camera', 'audio', 'video'],
        'mobiles-tablets': ['smartphone', 'phone', 'mobile', 'tablet', 'ipad', 'android', 'ios'],
        'computers-laptops': ['laptop', 'computer', 'desktop', 'notebook', 'pc', 'workstation'],
        'fashion-women': ['dress', 'top', 'blouse', 'skirt', 'pants', 'jeans', 'shoes', 'bag'],
        'fashion-men': ['shirt', 'polo', 't-shirt', 'pants', 'jeans', 'shoes', 'watch', 'wallet'],
        'health-beauty': ['skincare', 'makeup', 'cosmetic', 'cream', 'serum', 'cleanser', 'moisturizer'],
        'watches-accessories': ['watch', 'bracelet', 'necklace', 'ring', 'earring', 'sunglasses'],
        'sports-outdoor': ['running', 'fitness', 'gym', 'outdoor', 'sports', 'exercise', 'training']
    }
    
    @classmethod
    def get_random_user_agent(cls) -> str:
        """Get a random user agent string."""
        return random.choice(cls.USER_AGENTS)
    
    @classmethod
    def get_request_delay(cls) -> float:
        """Get a random delay between requests."""
        return random.uniform(*cls.REQUEST_DELAY)
    
    @classmethod
    def get_search_url(cls, query: str, page: int = 1) -> str:
        """Build search URL for Lazada."""
        return f"{cls.SEARCH_URL}?q={query}&page={page}"
    
    @classmethod
    def get_category_url(cls, category: str) -> str:
        """Get URL for a specific category."""
        return cls.CATEGORY_URLS.get(category.lower(), cls.get_search_url(category))
    
    def is_valid_product(self, product_name: str, price: float = None, rating: float = None) -> bool:
        """Check if product meets filtering criteria."""
        name_lower = product_name.lower()
        
        # Check exclude keywords first
        if self.EXCLUDE_KEYWORDS:
            if any(exclude in name_lower for exclude in self.EXCLUDE_KEYWORDS):
                return False
        
        # Check include keywords
        if self.INCLUDE_KEYWORDS:
            if not any(include in name_lower for include in self.INCLUDE_KEYWORDS):
                return False
        
        # Check brand filter
        if self.BRAND_FILTER:
            if self.BRAND_FILTER not in name_lower:
                return False
        
        # Check price range
        if price is not None:
            if not (self.MIN_PRICE <= price <= self.MAX_PRICE):
                return False
        
        return True
    
    @classmethod
    def extract_brand_from_name(cls, product_name: str, category: str = None) -> str:
        """Extract brand from product name using category-specific brand lists."""
        name_lower = product_name.lower()
        
        # Try category-specific brands first
        if category and category in cls.BRAND_LISTS:
            for brand in cls.BRAND_LISTS[category]:
                if brand.lower() in name_lower:
                    return brand.title()
        
        # Try all brands from all categories
        for brand_list in cls.BRAND_LISTS.values():
            for brand in brand_list:
                if brand.lower() in name_lower:
                    return brand.title()
        
        # Try to extract first word as potential brand
        first_word = product_name.split()[0] if product_name.split() else "Unknown"
        return first_word.title()
    
    @classmethod
    def get_category_brands(cls, category: str) -> List[str]:
        """Get list of brands for a specific category."""
        return cls.BRAND_LISTS.get(category.lower(), [])
    
    @classmethod
    def get_category_keywords(cls, category: str) -> List[str]:
        """Get list of keywords for a specific category."""
        return cls.CATEGORY_KEYWORDS.get(category.lower(), [])
    
    def set_category_filters(self, category: str):
        """Set filters based on category."""
        category_lower = category.lower()
        
        # Set include keywords based on category
        if category_lower in self.CATEGORY_KEYWORDS:
            self.INCLUDE_KEYWORDS = self.CATEGORY_KEYWORDS[category_lower]
        
        # You can extend this to set other category-specific filters
        # For example, price ranges, rating minimums, etc.
    
    def update_from_args(self, **kwargs):
        """Update configuration from command line arguments or other sources."""
        for key, value in kwargs.items():
            if hasattr(self, key.upper()) and value is not None:
                setattr(self, key.upper(), value)