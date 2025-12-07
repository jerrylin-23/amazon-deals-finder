"""
CamelCamelCamel Price History Scraper
Fetches historical price data from CamelCamelCamel.com
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
import json


class CamelScraper:
    """Scrape price history from CamelCamelCamel"""
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.base_url = "https://ca.camelcamelcamel.com"
    
    def get_price_history(self, asin: str) -> Optional[Dict]:
        """
        Get price history for an Amazon product by ASIN
        
        Args:
            asin: Amazon ASIN (product ID)
            
        Returns:
            Dictionary with price history data or None if not found
        """
        url = f"{self.base_url}/product/{asin}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract product info
            title = self._extract_title(soup)
            current_prices = self._extract_current_prices(soup)
            price_stats = self._extract_price_stats(soup)
            
            # Try to extract chart data (CamelCamelCamel embeds chart data in JavaScript)
            chart_data = self._extract_chart_data(response.text)
            
            return {
                'asin': asin,
                'title': title,
                'current_prices': current_prices,
                'price_stats': price_stats,
                'chart_data': chart_data,
                'camel_url': url
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching CamelCamelCamel data for {asin}: {e}")
            return None
        except Exception as e:
            print(f"Error parsing CamelCamelCamel data for {asin}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title"""
        title_elem = soup.find('h1', {'class': 'product_title'})
        if title_elem:
            return title_elem.get_text(strip=True)
        return ""
    
    def _extract_current_prices(self, soup: BeautifulSoup) -> Dict:
        """Extract current Amazon, New, and Used prices"""
        prices = {
            'amazon': None,
            'new_third_party': None,
            'used': None
        }
        
        # Find price elements
        price_divs = soup.find_all('div', {'class': 'price'})
        
        for div in price_divs:
            price_text = div.get_text(strip=True)
            price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
            
            if price_match:
                price = float(price_match.group(1).replace(',', ''))
                
                # Identify which price type (Amazon, New, or Used)
                label = div.find_previous('span', {'class': 'label'})
                if label:
                    label_text = label.get_text(strip=True).lower()
                    if 'amazon' in label_text:
                        prices['amazon'] = price
                    elif 'new' in label_text:
                        prices['new_third_party'] = price
                    elif 'used' in label_text:
                        prices['used'] = price
        
        return prices
    
    def _extract_price_stats(self, soup: BeautifulSoup) -> Dict:
        """Extract price statistics (lowest, highest, average)"""
        stats = {
            'lowest_amazon': None,
            'highest_amazon': None,
            'average_amazon': None,
            'lowest_new': None,
            'highest_new': None,
            'current_amazon': None
        }
        
        # CamelCamelCamel shows these in a summary table
        summary_table = soup.find('table', {'class': 'product_summary'})
        
        if summary_table:
            rows = summary_table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    label = cells[0].get_text(strip=True).lower()
                    
                    # Extract prices from cells
                    for idx, cell in enumerate(cells[1:], 1):
                        price_text = cell.get_text(strip=True)
                        price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                        if price_match:
                            price = float(price_match.group(1).replace(',', ''))
                            
                            if 'amazon' in label:
                                if 'current' in cells[0].get_text(strip=True).lower():
                                    stats['current_amazon'] = price
                                elif 'lowest' in cells[0].get_text(strip=True).lower():
                                    stats['lowest_amazon'] = price
                                elif 'highest' in cells[0].get_text(strip=True).lower():
                                    stats['highest_amazon'] = price
        
        return stats
    
    def _extract_chart_data(self, html: str) -> Optional[List[Dict]]:
        """
        Extract chart data from embedded JavaScript
        CamelCamelCamel includes price history data in JS variables
        """
        # Look for chart data in JavaScript
        # Pattern: var chartData = [...]; or similar
        pattern = r'var\s+\w*[Cc]hart[Dd]ata\w*\s*=\s*(\[.*?\]);'
        match = re.search(pattern, html, re.DOTALL)
        
        if match:
            try:
                # Parse the JavaScript array as JSON
                data_str = match.group(1)
                # Clean up JavaScript to make it valid JSON
                data_str = re.sub(r'new Date\((\d+)\)', r'\1', data_str)
                chart_data = json.loads(data_str)
                return chart_data
            except:
                pass
        
        return None
    
    def get_lowest_price_ever(self, asin: str) -> Optional[float]:
        """Quick method to just get the lowest price ever for a product"""
        data = self.get_price_history(asin)
        if data and data.get('price_stats'):
            return data['price_stats'].get('lowest_amazon')
        return None
    
    def is_at_lowest_price(self, asin: str, current_price: float, threshold: float = 1.0) -> bool:
        """
        Check if current price is at or near historical low
        
        Args:
            asin: Amazon ASIN
            current_price: Current price to check
            threshold: Price difference threshold (dollars)
            
        Returns:
            True if at historical low (within threshold)
        """
        lowest = self.get_lowest_price_ever(asin)
        if lowest is None:
            return False
        
        return current_price <= (lowest + threshold)
