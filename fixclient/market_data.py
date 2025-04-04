"""
Market data retrieval module using Finnhub API.
Requires requests package: pip install requests
"""

import requests
from typing import Dict, Optional, Union
from datetime import datetime
import maricon
import time

class FinnhubClient:
    """Client for interacting with Finnhub API."""
    
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self, api_key: str, max_orders_before_refresh: int = 20):
        """
        Initialize the Finnhub client.
        
        Args:
            api_key (str): Your Finnhub API key
            max_orders_before_refresh (int): Maximum number of orders before refreshing price
        """
        self.api_key = api_key
        self.max_orders_before_refresh = max_orders_before_refresh
        self.price_cache = {}  # {symbol: {'price': price, 'last_updated': timestamp, 'order_count': count}}
        
    def get_candles(self, 
                    symbol: str, 
                    resolution: str = "D",
                    from_time: Optional[int] = None,
                    to_time: Optional[int] = None) -> Dict:
        """
        Get candlestick data.
        
        Args:
            symbol (str): The stock symbol (e.g., "AAPL")
            resolution (str): Time resolution ("1", "5", "15", "30", "60", "D", "W", "M")
            from_time (int, optional): Start time in Unix timestamp
            to_time (int, optional): End time in Unix timestamp
            
        Returns:
            Dict: The candlestick data
        """
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "token": self.api_key
        }
        
        if from_time:
            params["from"] = from_time
        if to_time:
            params["to"] = to_time
            
        response = requests.get(f"{self.BASE_URL}/stock/candle", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_quote(self, symbol: str, force_refresh: bool = False) -> Dict:
        """
        Get real-time quote data.
        
        Args:
            symbol (str): The stock symbol (e.g., "AAPL")
            force_refresh (bool): Force a refresh of the cached price
            
        Returns:
            Dict: The quote data
        """
        # Check if we have a cached price and if it's still valid
        if not force_refresh and symbol in self.price_cache:
            cache_entry = self.price_cache[symbol]
            # If we haven't exceeded the order count limit, return cached price
            if cache_entry['order_count'] < self.max_orders_before_refresh:
                return {'c': cache_entry['price']}  # 'c' is current price in Finnhub API
        
        # If we need to refresh, make the API call
        params = {
            "symbol": symbol,
            "token": self.api_key
        }
        
        response = requests.get(f"{self.BASE_URL}/quote", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Update the cache
        if 'c' in data and data['c']:
            self.price_cache[symbol] = {
                'price': float(data['c']),
                'last_updated': time.time(),
                'order_count': 0  # Reset order count
            }
        
        return data
    
    def increment_order_count(self, symbol: str) -> None:
        """
        Increment the order count for a symbol.
        This should be called after each order is placed.
        
        Args:
            symbol (str): The stock symbol
        """
        if symbol in self.price_cache:
            self.price_cache[symbol]['order_count'] += 1
    
    def get_cached_price(self, symbol: str) -> Optional[float]:
        """
        Get the cached price for a symbol without making an API call.
        
        Args:
            symbol (str): The stock symbol
            
        Returns:
            Optional[float]: The cached price, or None if not available
        """
        if symbol in self.price_cache:
            return self.price_cache[symbol]['price']
        return None
    
    def search_symbol(self, keywords: str) -> Dict:
        """
        Search for symbols and company names.
        
        Args:
            keywords (str): Keywords to search for
            
        Returns:
            Dict: Search results
        """
        params = {
            "q": keywords,
            "token": self.api_key
        }
        
        response = requests.get(f"{self.BASE_URL}/search", params=params)
        response.raise_for_status()
        return response.json()

# Example usage:
if __name__ == "__main__":
    # Replace with your actual API key
    API_KEY = maricon.finnhub_key
    client = FinnhubClient(API_KEY)
    
    # Example: Get quote data for Apple
    try:
        quote_data = client.get_quote("AAPL")
        print("Quote data for AAPL:", quote_data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}") 