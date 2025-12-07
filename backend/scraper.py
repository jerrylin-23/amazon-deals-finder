"""
Amazon Product Scraper - Optimized Version
Fetches product data with parallel scraping and caching
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import time
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import hashlib


class AmazonScraper:
    """Scrape Amazon product data (optimized with caching)"""
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    TECH_CATEGORIES = {
        'laptops': 'laptop',
        'monitors': 'monitor',
        'keyboards': 'mechanical keyboard',
        'mice': 'gaming mouse',
        'headphones': 'headphones',
        'phones': 'smartphone',
        'tablets': 'tablet',
        'smartwatches': 'smartwatch',
        'webcams': 'webcam',
        'microphones': 'microphone'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def _get_cache_key(self, query: str, max_results: int, min_discount: int, max_pages: int = 2) -> str:
        """Generate cache key for a search"""
        return hashlib.md5(f"{query}_{max_results}_{min_discount}_{max_pages}".encode()).hexdigest()
    
    def search_products(self, query: str, max_results: int = 30, min_discount: int = 0, max_pages: int = 2) -> List[Dict]:
        """
        Search Amazon for products (balanced for Render free tier)
        
        Args:
            query: Search term (e.g., 'laptop', 'mechanical keyboard')
            max_results: Maximum number of results to return (default: 30)
            min_discount: Minimum discount percentage to filter by (default: 0)
            max_pages: Maximum number of pages to scrape (default: 2 for balance)
            
        Returns:
            List of product dictionaries
        """
        # Check cache first
        cache_key = self._get_cache_key(query, max_results, min_discount, max_pages)
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return cached_data
        
        all_products = []
        
        def scrape_page(page_num):
            """Scrape a single page"""
            encoded_query = quote_plus(query)
            url = f'https://www.amazon.ca/s?k={encoded_query}&page={page_num}'
            
            try:
                response = self.session.get(url, timeout=8)  # Balanced timeout
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'lxml')
                items = soup.find_all('div', {'data-component-type': 's-search-result'})
                
                page_products = []
                for item in items:
                    try:
                        product = self._extract_product_data(item)
                        if product and product.get('discount_percent', 0) >= min_discount:
                            page_products.append(product)
                    except Exception:
                        continue
                
                return page_products
                
            except Exception as e:
                print(f"Error on page {page_num}: {str(e)}")
                return []
        
        # Scrape pages with moderate parallelism (balanced for both local and Render)
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(scrape_page, page): page for page in range(1, max_pages + 1)}
            
            for future in as_completed(futures):
                products = future.result()
                all_products.extend(products)
                
                # Stop if we have enough products
                if len(all_products) >= max_results:
                    break
        
        result = all_products[:max_results]
        
        # Cache the results
        self._cache[cache_key] = (result, time.time())
        
        return result
    
    def _extract_product_data(self, item) -> Optional[Dict]:
        """Extract product data from a search result item (optimized)"""
        
        # ASIN (Amazon product ID) - fastest check first
        asin = item.get('data-asin', '')
        if not asin:
            return None
        
        # Title
        title_elem = item.h2
        if not title_elem:
            return None
        title = title_elem.get_text(strip=True)
        
        # URL
        link_elem = item.find('a', {'class': 'a-link-normal s-no-outline'})
        url = "https://www.amazon.ca" + link_elem['href'] if link_elem and 'href' in link_elem.attrs else ''
        
        # Price - optimized extraction
        price_whole = item.find('span', {'class': 'a-price-whole'})
        price_fraction = item.find('span', {'class': 'a-price-fraction'})
        
        current_price = None
        if price_whole:
            price_str = price_whole.get_text(strip=True).replace(',', '').replace('.', '')
            if price_fraction:
                price_str += price_fraction.get_text(strip=True)
            try:
                current_price = float(price_str) / 100 if price_fraction else float(price_str)
            except:
                pass
        
        # Original price (for discounts)
        original_price_elem = item.find('span', {'class': 'a-price a-text-price'})
        original_price = None
        if original_price_elem:
            price_text = original_price_elem.get_text(strip=True)
            match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
            if match:
                try:
                    original_price = float(match.group(1).replace(',', ''))
                except:
                    pass
        
        # Calculate discount
        discount_percent = 0
        if current_price and original_price and original_price > current_price:
            discount_percent = int(((original_price - current_price) / original_price) * 100)
        
        # Rating - optimized
        rating = None
        rating_elem = item.find('span', {'class': 'a-icon-alt'})
        if rating_elem:
            match = re.search(r'([\d.]+)', rating_elem.get_text(strip=True))
            if match:
                try:
                    rating = float(match.group(1))
                except:
                    pass
        
        # Number of reviews - optimized
        num_reviews = 0
        reviews_elem = item.find('span', {'class': 'a-size-base s-underline-text'})
        if reviews_elem:
            match = re.search(r'(\d+)', reviews_elem.get_text(strip=True).replace(',', ''))
            if match:
                try:
                    num_reviews = int(match.group(1))
                except:
                    pass
        
        # Image
        img_elem = item.find('img', {'class': 's-image'})
        image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else ''
        
        # Prime eligibility
        is_prime = item.find('i', {'class': 'a-icon-prime'}) is not None
        
        return {
            'asin': asin,
            'title': title,
            'url': url,
            'current_price': current_price,
            'original_price': original_price,
            'discount_percent': discount_percent,
            'rating': rating,
            'num_reviews': num_reviews,
            'image_url': image_url,
            'is_prime': is_prime,
            'is_deal': discount_percent >= 15  # 15%+ is considered a deal
        }
    
    def get_category_deals(self, category: str, min_discount: int = 10) -> List[Dict]:
        """Get deals for a specific tech category (balanced for Render)"""
        if category not in self.TECH_CATEGORIES:
            raise ValueError(f"Unknown category: {category}. Available: {list(self.TECH_CATEGORIES.keys())}")
        
        query = self.TECH_CATEGORIES[category]
        return self.search_products(query, max_results=30, min_discount=min_discount, max_pages=2)
    
    def get_all_categories(self) -> List[str]:
        """Get list of available categories"""
        return list(self.TECH_CATEGORIES.keys())
