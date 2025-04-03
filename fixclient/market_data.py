"""
Market data retrieval module using Alpha Vantage API.
Requires requests package: pip install requests
"""

import requests
from typing import Dict, Optional, Union
from datetime import datetime
import maricon
import time

class AlphaVantageClient:
    """Client for interacting with Alpha Vantage API."""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str, max_orders_before_refresh: int = 20):
        """
        Initialize the Alpha Vantage client.
        
        Args:
            api_key (str): Your Alpha Vantage API key
            max_orders_before_refresh (int): Maximum number of orders before refreshing price
        """
        self.api_key = api_key
        self.max_orders_before_refresh = max_orders_before_refresh
        self.price_cache = {}  # {symbol: {'price': price, 'last_updated': timestamp, 'order_count': count}}
        
    def get_intraday(self, 
                     symbol: str, 
                     interval: str = "5min",
                     outputsize: str = "compact") -> Dict:
        """
        Get intraday time series data.
        
        Args:
            symbol (str): The stock symbol (e.g., "AAPL")
            interval (str): Time interval between data points ("1min", "5min", "15min", "30min", "60min")
            outputsize (str): "compact" (latest 100 points) or "full" (up to 20 years of data)
            
        Returns:
            Dict: The intraday time series data
        """
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": self.api_key
        }
        
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_daily(self, 
                  symbol: str, 
                  outputsize: str = "compact") -> Dict:
        """
        Get daily time series data.
        
        Args:
            symbol (str): The stock symbol (e.g., "AAPL")
            outputsize (str): "compact" (latest 100 points) or "full" (up to 20 years of data)
            
        Returns:
            Dict: The daily time series data
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,
            "apikey": self.api_key
        }
        
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_global_quote(self, symbol: str, force_refresh: bool = False) -> Dict:
        """
        Get real-time and daily historical data.
        
        Args:
            symbol (str): The stock symbol (e.g., "AAPL")
            force_refresh (bool): Force a refresh of the cached price
            
        Returns:
            Dict: The global quote data
        """
        # Check if we have a cached price and if it's still valid
        if not force_refresh and symbol in self.price_cache:
            cache_entry = self.price_cache[symbol]
            # If we haven't exceeded the order count limit, return cached price
            if cache_entry['order_count'] < self.max_orders_before_refresh:
                return {'Global Quote': {'05. price': str(cache_entry['price'])}}
        
        # If we need to refresh, make the API call
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Update the cache
        if 'Global Quote' in data and data['Global Quote'].get('05. price'):
            self.price_cache[symbol] = {
                'price': float(data['Global Quote']['05. price']),
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
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": self.api_key
        }
        
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()

# Example usage:
if __name__ == "__main__":
    # Replace with your actual API key
    API_KEY = maricon.alphavantage_key
    client = AlphaVantageClient(API_KEY)
    
    # Example: Get daily data for Apple
    try:
        daily_data = client.get_daily("AAPL")
        print("Daily data for AAPL:", daily_data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}") 