# Lazada Product Scraper

A production-ready web scraper for extracting product data from Lazada Singapore. This project is designed for use in data-intensive environments such as e-commerce intelligence and market research teams.

---

## Features

* **Multi-Category Support**: Customised products scraping from all major Lazada categories (electronics, fashion, health & beauty, etc.)
* **Robust Data Extraction**: Extracts comprehensive product data including pricing, review counts
* **Smart Pagination**: Handles both pagination and infinite scroll patterns
* **JavaScript Rendering**: Uses Playwright for JavaScript-heavy content
* **Error Handling**: Comprehensive retry logic and error recovery
* **User-Agent Rotation**: Prevents blocking with rotating headers
* **Data Analysis**: Built-in analysis tools for pricing and brand insights
* **Flexible Filtering**: Filter by price range, and keywords
* **Production Ready**: Modular architecture with proper logging and monitoring

---

## Quick Start

### Prerequisites

* Python 3.11+
* `pip` for dependency management

### Installation

Clone the repository:

```bash
git clone <repository-url>
cd lazada-scraper
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright browsers:

```bash
playwright install chromium
```

### Basic Usage Examples

```bash
# Basic scraping - search for smartphones
python main.py --search-query "smartphone"

# Scrape a specific category
python main.py --category electronics

# Search with price filters
python main.py --search-query "nike shoes" --min-price 50 --max-price 300

# Scrape with brand filtering
python main.py --search-query "laptop"

# Advanced usage with analysis
python main.py --category mobiles-tablets --max-pages 15 --analyze --headless
```

---

## Command Line Arguments

### Basic Arguments
| Argument     | Type   | Default    | Description                                |
| ------------ | ------ | ---------- | ------------------------------------------ |
| --search-query      | str    | None       | Search query (e.g., "smartphone", "nike") |
| --category   | str    | None       | Category to scrape (see categories below) |
| --max-pages  | int    | 3          | Maximum pages to scrape                    |
| --min-price  | float  | 0          | Minimum price filter (SGD)                 |
| --max-price  | float  | ∞          | Maximum price filter (SGD)                 |

### Output & Behavior
| Argument     | Type   | Default    | Description                                |
| ------------ | ------ | ---------- | ------------------------------------------ |
| --output-dir | str    | "output"   | Output directory for files                 |
| --headless   | flag   | False      | Run browser in headless mode               |
| --analyze    | flag   | False      | Perform data analysis after scraping       |
| --log-level  | str    | "INFO"     | Logging level (DEBUG/INFO/WARNING/ERROR)   |

### Advanced Filtering
| Argument         | Type   | Default | Description                           |
| ---------------- | ------ | ------- | ------------------------------------- |
| --include-words  | str    | None    | Comma-separated words to include      |
| --exclude-words  | str    | None    | Comma-separated words to exclude      |

---

## Available Categories

Use these category names with the `--category` argument:

| Category             | Command                          | Description                    |
| -------------------- | -------------------------------- | ------------------------------ |
| electronics          | `--category electronics`         | TVs, audio, cameras            |
| mobiles-tablets      | `--category mobiles-tablets`     | Smartphones, tablets           |
| computers-laptops    | `--category computers-laptops`   | Laptops, desktops, accessories |
| home-living          | `--category home-living`         | Furniture, home decor          |
| health-beauty        | `--category health-beauty`       | Skincare, makeup, wellness     |
| fashion-women        | `--category fashion-women`       | Women's clothing, accessories  |
| fashion-men          | `--category fashion-men`         | Men's clothing, accessories    |
| watches-accessories  | `--category watches-accessories` | Watches, jewelry               |
| babies-toys          | `--category babies-toys`         | Baby products, toys            |
| groceries            | `--category groceries`           | Food, beverages                |
| automotive           | `--category automotive`          | Car accessories, parts         |

---

## Usage Examples by Category

### Electronics & Tech
```bash
# Scrape smartphones
python main.py --category mobiles-tablets --min-price 200 --max-price 1500

# Search for specific laptop brands
python main.py --search-query "dell laptop"

# Find gaming accessories
python main.py --search-query "gaming mouse"
```

### Fashion & Lifestyle
```bash
# Women's fashion with price range
python main.py --category fashion-women --min-price 20 --max-price 200

# Search for Nike shoes
python main.py --search-query "nike" --include-words "shoes,sneakers"

# Luxury watches
python main.py --category watches-accessories --min-price 500
```

### Health & Beauty
```bash
# Skincare products
python main.py --category health-beauty --search-query "skincare" # Custom search query (overrides category if provided)

# Specific brands
python main.py --search-query "olay" --exclude-words "sample,travel"
```

### Home & Living
```bash
# Furniture
python main.py --category home-living --max-pages 10

# Kitchen appliances
python main.py --search-query "kitchen" --category home-living --min-price 50
```

---

## Advanced Usage Patterns

### Brand-Focused Scraping
```bash
# All Apple products
python main.py --brand "apple"

# Samsung electronics only
python main.py --search-query "samsung" --category electronics --max-pages 20
```

### Price Research
```bash
# Budget smartphones
python main.py --category mobiles-tablets --max-price 500 --analyze

# Premium products analysis
python main.py --search-query "premium" --min-price 1000 --analyze --headless
```

### Market Research
```bash
# Comprehensive category analysis
python main.py --category health-beauty --max-pages 25 --analyze

# Competitor analysis
python main.py --include-words "nike,adidas,puma" --category fashion-men --analyze
```

---

## Project Structure

```
lazada-scraper/
├── main.py                 # Entry point script
├── src/
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration settings & categories
│   ├── scraper.py          # Core scraping logic
│   ├── analyzer.py         # Data analysis module
│   └── utils.py            # Utility functions
├── output/                 # Output directory (created automatically)
├── requirements.txt        # Python dependencies
├── LazadaDashboard.py      # Streamlit dashboard
└── README.md               # This file
```

---

## Data Output

### CSV Fields Extracted

| Field                | Description                        | Example                    |
| -------------------- | ---------------------------------- | -------------------------- |
| product_name         | Full product name                  | "iPhone 15 Pro Max 256GB" |
| price                | Current price in SGD               | 1699.00                    |
| original_price       | Original price (if discounted), derived    | 1899.00                    |
| discount_percentage  | Discount percentage                | 10.5                       |
| review_count         | Number of customer reviews         | 1,234                      |
| discount_tag_line    | Discount info text                 | Subsidized $x, Voucher save x|"Apple"                    |
| location             | Shop location                      | "Singapore"                |
| quantity_sold        | Number of items sold               | "500+ sold"                |
| category             | Product category                   | "mobiles-tablets"          |
| product_url          | Direct link to product page        | https://lazada.sg/...      |
| scraped_at           | Timestamp of data extraction       | 2025-06-07 10:30:00        |

---

## Data Analysis Dashboard

Run the interactive dashboard for visual analysis:

```bash
streamlit run LazadaDashboard.py -- --file_name "mobiles-tablets_products.csv"
```

### Dashboard Features:
* **Price Distribution Analysis**: Visualize price ranges
* **Distribution by Location**: location analysis
* **Top 5 Expensive Products**: To see upper end prices
* **Price Statistics** To see the mean, median, min, max prices

---

## Troubleshooting Common Issues

### Category Not Found
If you get "no results" for a category:
```bash
# Use search query instead
python main.py --search-query "sports equipment" --max-pages 5

# Or try related categories
python main.py --category home-living --search-query "fitness"
```

### Rate Limiting
If you encounter rate limiting:
```bash
# Increase delays and reduce pages
python main.py --search-query "laptop" --max-pages 3 --headless

# Use longer delays (modify config.py REQUEST_DELAY)
```

### Low Product Count
If not enough products are found:
```bash
# Increase page limit
python main.py --category electronics --max-pages 15

# Broaden search terms
python main.py --search-query "phone" --include-words "smartphone,mobile"
```

---

## Configuration Customization

### Modifying Scraping Behavior

Edit `src/config.py` to customize:

```python
# Increase request delays to avoid blocking
REQUEST_DELAY = (3, 7)  # 3-7 second delays

# Adjust browser timeout
BROWSER_TIMEOUT = 60000  # 60 seconds

# Modify retry settings
MAX_RETRIES = 5
RETRY_DELAY = 5
```

### Adding New Categories

```python
# Add to CATEGORY_URLS in config.py
CATEGORY_URLS = {
    'your-category': 'https://www.lazada.sg/your-category-url/',
    # ... existing categories
}
```

---

## Performance Tips

### For Large-Scale Scraping
```bash
# Use headless mode for better performance
python main.py --category electronics --headless --max-pages 20

# Combine with analysis for insights
python main.py --search-query "smartphone" --analyze
```

### For Development/Testing
```bash
# Use non-headless mode to see what's happening
python main.py --search-query "test" --max-pages 1 --log-level DEBUG

# Quick category test
python main.py --category mobiles-tablets --max-pages 2
```

---

## Error Handling

The scraper handles common issues automatically:

* **Network Timeouts**: Automatic retry with exponential backoff
* **Page Load Failures**: Skips failed pages and continues
* **Anti-Bot Measures**: User-agent rotation and random delays
* **Data Parsing Errors**: Graceful handling of missing fields
* **Resource Cleanup**: Proper browser cleanup on interruption

---

## Support

For issues related to:
* **Specific categories not working**: Try using search queries instead
* **No products found**: Check if the category URL is still valid
* **Rate limiting**: Increase delays in config.py
* **Browser issues**: Reinstall Playwright browsers

```bash
# Reinstall browsers if needed
playwright install --force chromium
```