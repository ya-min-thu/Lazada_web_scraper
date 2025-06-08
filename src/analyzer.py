"""
Data analysis module for scraped product data
"""

import logging
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any
from statistics import mean, median, mode, StatisticsError

from .utils import format_currency, safe_divide


class DataAnalyzer:
    """Analyzer for scraped smartphone data."""
    
    def __init__(self, products: List[Dict[str, Any]]):
        self.products = products
        self.logger = logging.getLogger(__name__)
    
    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive analysis of the scraped data."""
        self.logger.info(f"Analyzing {len(self.products)} products...")
        
        analysis = {
            'summary': self.get_summary_stats(),
            'price_analysis': self.analyze_prices(),
            # 'brand_analysis': self.analyze_brands(), # brands could be populated accurately for improvement
            'rating_analysis': self.analyze_ratings(),
            'shop_analysis': self.analyze_shops(),
            'top_products': self.get_top_products()
        }
        
        return analysis
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get basic summary statistics."""
        total_products = len(self.products)
        products_with_price = [p for p in self.products if p.get('price', 0) > 0]
        products_with_rating = [p for p in self.products if p.get('rating', 0) > 0]
        
        return {
            'total_products': total_products,
            'products_with_price': len(products_with_price),
            'products_with_rating': len(products_with_rating),
            # 'unique_brands': len(set(p.get('brand', 'Unknown') for p in self.products)),
            # 'unique_shops': len(set(p.get('shop_name', '') for p in self.products if p.get('shop_name')))
        }
    
    def analyze_prices(self) -> Dict[str, Any]:
        """Analyze price distribution and statistics."""
        prices = [p.get('price', 0) for p in self.products if p.get('price', 0) > 0]
        
        if not prices:
            return {'error': 'No valid prices found'}
        
        try:
            price_stats = {
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': mean(prices),
                'median_price': median(prices),
                'total_value': sum(prices)
            }
            
            # Add mode if possible
            try:
                price_stats['mode_price'] = mode(prices)
            except StatisticsError:
                price_stats['mode_price'] = None
            
            # Price ranges
            price_ranges = self.get_price_ranges(prices)
            
            return {
                'statistics': price_stats,
                'ranges': price_ranges,
                'formatted_stats': {
                    'min': format_currency(price_stats['min_price']),
                    'max': format_currency(price_stats['max_price']),
                    'avg': format_currency(price_stats['avg_price']),
                    'median': format_currency(price_stats['median_price']),
                    'total': format_currency(price_stats['total_value'])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing prices: {str(e)}")
            return {'error': str(e)}
    
    def get_price_ranges(self, prices: List[float]) -> Dict[str, int]:
        """Categorize prices into ranges."""
        ranges = {
            'Under $200': 0,
            '$200-$500': 0,
            '$500-$1000': 0,
            '$1000-$1500': 0,
            'Over $1500': 0
        }
        
        for price in prices:
            if price < 200:
                ranges['Under $200'] += 1
            elif price < 500:
                ranges['$200-$500'] += 1
            elif price < 1000:
                ranges['$500-$1000'] += 1
            elif price < 1500:
                ranges['$1000-$1500'] += 1
            else:
                ranges['Over $1500'] += 1
        
        return ranges
    
    def analyze_brands(self) -> Dict[str, Any]:
        """Analyze brand distribution and statistics."""
        brands = [p.get('brand', 'Unknown') for p in self.products]
        brand_counter = Counter(brands)
        
        # Get brand statistics
        brand_stats = {}
        for brand in brand_counter.keys():
            brand_products = [p for p in self.products if p.get('brand') == brand]
            prices = [p.get('price', 0) for p in brand_products if p.get('price', 0) > 0]
            ratings = [p.get('rating', 0) for p in brand_products if p.get('rating', 0) > 0]
            
            stats = {
                'count': len(brand_products),
                'avg_price': mean(prices) if prices else 0,
                'avg_rating': mean(ratings) if ratings else 0,
                'price_range': (min(prices), max(prices)) if prices else (0, 0)
            }
            
            brand_stats[brand] = stats
        
        return {
            'distribution': dict(brand_counter.most_common()),
            'top_brands': brand_counter.most_common(10),
            'statistics': brand_stats
        }
    
    def analyze_ratings(self) -> Dict[str, Any]:
        """Analyze rating distribution and statistics."""
        ratings = [p.get('rating', 0) for p in self.products if p.get('rating', 0) > 0]
        review_counts = [p.get('review_count', 0) for p in self.products if p.get('review_count', 0) > 0]
        
        if not ratings:
            return {'error': 'No valid ratings found'}
        
        try:
            rating_stats = {
                'avg_rating': mean(ratings),
                'median_rating': median(ratings),
                'min_rating': min(ratings),
                'max_rating': max(ratings),
                'total_ratings': len(ratings)
            }
            
            review_stats = {}
            if review_counts:
                review_stats = {
                    'avg_reviews': mean(review_counts),
                    'median_reviews': median(review_counts),
                    'total_reviews': sum(review_counts),
                    'max_reviews': max(review_counts)
                }
            
            # Rating distribution
            rating_distribution = Counter([round(r, 1) for r in ratings])
            
            return {
                'rating_statistics': rating_stats,
                'review_statistics': review_stats,
                'distribution': dict(rating_distribution)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing ratings: {str(e)}")
            return {'error': str(e)}
    
    def analyze_shops(self) -> Dict[str, Any]:
        """Analyze shop distribution and performance."""
        shops = [p.get('shop_name', '') for p in self.products if p.get('shop_name')]
        shop_counter = Counter(shops)
        
        # Get shop statistics
        shop_stats = {}
        for shop in shop_counter.keys():
            shop_products = [p for p in self.products if p.get('shop_name') == shop]
            prices = [p.get('price', 0) for p in shop_products if p.get('price', 0) > 0]
            ratings = [p.get('rating', 0) for p in shop_products if p.get('rating', 0) > 0]
            
            stats = {
                'product_count': len(shop_products),
                'avg_price': mean(prices) if prices else 0,
                'avg_rating': mean(ratings) if ratings else 0,
                'total_value': sum(prices) if prices else 0
            }
            
            shop_stats[shop] = stats
        
        # Top shops by different criteria
        top_by_count = shop_counter.most_common(10)
        top_by_value = sorted(
            [(shop, stats['total_value']) for shop, stats in shop_stats.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        return {
            'total_shops': len(shop_counter),
            'distribution': dict(shop_counter),
            'top_by_count': top_by_count,
            'top_by_value': top_by_value,
            'statistics': shop_stats
        }
    
    def get_top_products(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get top products by various criteria."""
        # Filter products with valid data
        valid_products = [p for p in self.products if p.get('price', 0) > 0]
        rated_products = [p for p in self.products if p.get('rating', 0) > 0]
        reviewed_products = [p for p in self.products if p.get('review_count', 0) > 0]
        
        return {
            'most_expensive': sorted(
                valid_products, 
                key=lambda x: x.get('price', 0), 
                reverse=True
            )[:10],
            'cheapest': sorted(
                valid_products, 
                key=lambda x: x.get('price', 0)
            )[:10],
            'highest_rated': sorted(
                rated_products, 
                key=lambda x: x.get('rating', 0), 
                reverse=True
            )[:10],
            'most_reviewed': sorted(
                reviewed_products, 
                key=lambda x: x.get('review_count', 0), 
                reverse=True
            )[:10],
            'best_value': self.get_best_value_products(rated_products)[:10]
        }
    
    def get_best_value_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate best value products (high rating, reasonable price)."""
        scored_products = []
        
        for product in products:
            rating = product.get('rating', 0)
            price = product.get('price', 0)
            review_count = product.get('review_count', 0)
            
            if rating > 0 and price > 0:
                # Simple value score: rating / log(price) * log(reviews + 1)
                import math
                review_factor = math.log(review_count + 1)
                price_factor = math.log(price) if price > 1 else 1
                value_score = (rating * review_factor) / price_factor
                
                scored_products.append((product, value_score))
        
        # Sort by value score
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return [product for product, score in scored_products]
    
    def save_analysis(self, analysis: Dict[str, Any], filepath: Path):
        """Save analysis results to a text file."""
        self.logger.info(f"Saving analysis to {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("LAZADA SCRAPING ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Summary
            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 20 + "\n")
            summary = analysis.get('summary', {})
            for key, value in summary.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            f.write("\n")
            
            # Price Analysis
            f.write("PRICE ANALYSIS\n")
            f.write("-" * 15 + "\n")
            price_analysis = analysis.get('price_analysis', {})
            if 'formatted_stats' in price_analysis:
                stats = price_analysis['formatted_stats']
                f.write(f"Minimum Price: {stats.get('min', 'N/A')}\n")
                f.write(f"Maximum Price: {stats.get('max', 'N/A')}\n")
                f.write(f"Average Price: {stats.get('avg', 'N/A')}\n")
                f.write(f"Median Price: {stats.get('median', 'N/A')}\n")
                f.write(f"Total Value: {stats.get('total', 'N/A')}\n")
            
            if 'ranges' in price_analysis:
                f.write("\nPrice Range Distribution:\n")
                for range_name, count in price_analysis['ranges'].items():
                    f.write(f"  {range_name}: {count} products\n")
            f.write("\n")
            
            # Brand Analysis
            # f.write("BRAND ANALYSIS\n")
            # f.write("-" * 15 + "\n")
            brand_analysis = analysis.get('brand_analysis', {})
            if 'top_brands' in brand_analysis:
                f.write("Top 10 Brands:\n")
                for i, (brand, count) in enumerate(brand_analysis['top_brands'], 1):
                    f.write(f"  {i}. {brand}: {count} products\n")
            f.write("\n")
            
            # Rating Analysis
            # f.write("RATING ANALYSIS\n")
            # f.write("-" * 16 + "\n")
            rating_analysis = analysis.get('rating_analysis', {})
            if 'rating_statistics' in rating_analysis:
                stats = rating_analysis['rating_statistics']
                f.write(f"Average Rating: {stats.get('avg_rating', 0):.2f}\n")
                f.write(f"Median Rating: {stats.get('median_rating', 0):.2f}\n")
                f.write(f"Total Rated Products: {stats.get('total_ratings', 0)}\n")
            
            if 'review_statistics' in rating_analysis:
                stats = rating_analysis['review_statistics']
                f.write(f"Average Reviews per Product: {stats.get('avg_reviews', 0):.0f}\n")
                f.write(f"Total Reviews: {stats.get('total_reviews', 0)}\n")
            f.write("\n")
            
            # Top Products
            f.write("TOP PRODUCTS\n")
            f.write("-" * 12 + "\n")
            top_products = analysis.get('top_products', {})
            
            if 'most_expensive' in top_products:
                f.write("Most Expensive:\n")
                for i, product in enumerate(top_products['most_expensive'][:5], 1):
                    name = product.get('product_name', 'Unknown')[:50]
                    price = format_currency(product.get('price', 0))
                    f.write(f"  {i}. {name}... - {price}\n")
            
            # f.write("\n")
            # if 'highest_rated' in top_products:
            #     f.write("Highest Rated:\n")
            #     for i, product in enumerate(top_products['highest_rated'][:5], 1):
            #         name = product.get('product_name', 'Unknown')[:50]
            #         rating = product.get('rating', 0)
            #         f.write(f"  {i}. {name}... - {rating:.1f} Reviews\n")
            
        self.logger.info(f"Analysis saved to {filepath}")
    
    def get_insights(self) -> List[str]:
        """Generate key insights from the analysis."""
        analysis = self.analyze()
        insights = []
        
        # Price insights
        price_analysis = analysis.get('price_analysis', {})
        if 'statistics' in price_analysis:
            stats = price_analysis['statistics']
            avg_price = stats.get('avg_price', 0)
            if avg_price > 0:
                insights.append(f"Average smartphone price is {format_currency(avg_price)}")
        
        # Brand insights
        brand_analysis = analysis.get('brand_analysis', {})
        if 'top_brands' in brand_analysis:
            top_brand = brand_analysis['top_brands'][0] if brand_analysis['top_brands'] else None
            if top_brand:
                insights.append(f"Most popular brand is {top_brand[0]} with {top_brand[1]} products")
        
        # Rating insights
        rating_analysis = analysis.get('rating_analysis', {})
        if 'rating_statistics' in rating_analysis:
            avg_rating = rating_analysis['rating_statistics'].get('avg_rating', 0)
            if avg_rating > 0:
                insights.append(f"Average customer rating is {avg_rating:.1f} stars")
        
        return insights