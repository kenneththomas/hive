"""
Market data retrieval module using Alpha Vantage API.
Requires requests package: pip install requests
"""

import requests
from typing import Dict, Optional, Union
from datetime import datetime
import maricon

class AlphaVantageClient:
    """Client for interacting with Alpha Vantage API."""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str):
        """
        Initialize the Alpha Vantage client.
        
        Args:
            api_key (str): Your Alpha Vantage API key
        """
        self.api_key = api_key
        
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
    
    def get_global_quote(self, symbol: str) -> Dict:
        """
        Get real-time and daily historical data.
        
        Args:
            symbol (str): The stock symbol (e.g., "AAPL")
            
        Returns:
            Dict: The global quote data
        """
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    
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