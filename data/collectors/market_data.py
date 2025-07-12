"""
Market Data Collector
Fetches stock market data from various sources
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import json

logger = logging.getLogger(__name__)

class MarketDataCollector:
    """Collects market data from various sources"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = 300  # 5 minutes
        
    def get_stock_data(self, symbol: str, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
        """
        Get stock data for a given symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Check cache first
            cache_key = f"{symbol}_{period}_{interval}"
            if self._is_cache_valid(cache_key):
                logger.info(f"Returning cached data for {symbol}")
                return self.cache[cache_key]
            
            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Clean and process data
            data = self._clean_data(data)
            
            # Cache the data
            self.cache[cache_key] = data
            self.cache_timestamps[cache_key] = datetime.now()
            
            logger.info(f"Successfully fetched data for {symbol}: {len(data)} data points")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            raise
    
    def get_market_data(self, symbols: List[str], period: str = '1d') -> Dict[str, pd.DataFrame]:
        """
        Get market data for multiple symbols
        
        Args:
            symbols: List of stock symbols
            period: Time period
            
        Returns:
            Dictionary with symbol as key and DataFrame as value
        """
        results = {}
        
        for symbol in symbols:
            try:
                results[symbol] = self.get_stock_data(symbol, period)
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
                continue
        
        return results
    
    def get_real_time_price(self, symbol: str) -> Dict:
        """
        Get real-time price for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with current price information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get latest price
            latest_data = ticker.history(period='1d', interval='1m')
            if not latest_data.empty:
                current_price = latest_data['Close'].iloc[-1]
                previous_close = info.get('previousClose', current_price)
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
            else:
                current_price = info.get('currentPrice', 0)
                previous_close = info.get('previousClose', current_price)
                change = 0
                change_percent = 0
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'previous_close': previous_close,
                'change': change,
                'change_percent': change_percent,
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time price for {symbol}: {str(e)}")
            raise
    
    def search_symbols(self, query: str) -> List[Dict]:
        """
        Search for stock symbols
        
        Args:
            query: Search query
            
        Returns:
            List of matching symbols with company names
        """
        try:
            # Use Yahoo Finance search
            search_results = yf.Tickers(query)
            
            results = []
            for ticker in search_results.tickers:
                try:
                    info = ticker.info
                    results.append({
                        'symbol': info.get('symbol', ''),
                        'name': info.get('longName', info.get('shortName', '')),
                        'exchange': info.get('exchange', ''),
                        'type': info.get('quoteType', '')
                    })
                except:
                    continue
            
            return results[:10]  # Limit to 10 results
            
        except Exception as e:
            logger.error(f"Error searching symbols: {str(e)}")
            return []
    
    def get_earnings_calendar(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get earnings calendar
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with earnings information
        """
        try:
            if not start_date:
                start_date = datetime.now().strftime('%Y-%m-%d')
            if not end_date:
                end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            # This would typically use a paid API like Alpha Vantage
            # For now, return empty DataFrame
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error getting earnings calendar: {str(e)}")
            return pd.DataFrame()
    
    def get_economic_calendar(self) -> pd.DataFrame:
        """
        Get economic calendar with important events
        
        Returns:
            DataFrame with economic events
        """
        try:
            # This would fetch from FRED API or similar
            # For now, return empty DataFrame
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error getting economic calendar: {str(e)}")
            return pd.DataFrame()
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and process raw market data
        
        Args:
            data: Raw DataFrame from API
            
        Returns:
            Cleaned DataFrame
        """
        # Remove any rows with NaN values
        data = data.dropna()
        
        # Ensure we have required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Convert volume to numeric
        data['Volume'] = pd.to_numeric(data['Volume'], errors='coerce')
        
        # Calculate additional technical indicators
        data['Returns'] = data['Close'].pct_change()
        data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))
        
        # Calculate moving averages
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['EMA_12'] = data['Close'].ewm(span=12).mean()
        data['EMA_26'] = data['Close'].ewm(span=26).mean()
        
        # Calculate volatility
        data['Volatility'] = data['Returns'].rolling(window=20).std()
        
        return data
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if cached data is still valid
        
        Args:
            cache_key: Cache key
            
        Returns:
            True if cache is valid, False otherwise
        """
        if cache_key not in self.cache_timestamps:
            return False
        
        cache_time = self.cache_timestamps[cache_key]
        return (datetime.now() - cache_time).seconds < self.cache_duration
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.cache_timestamps.clear()
        logger.info("Cache cleared")
    
    def get_market_status(self) -> Dict:
        """
        Get current market status
        
        Returns:
            Dictionary with market status information
        """
        try:
            now = datetime.now()
            
            # Check if market is open (simplified - assumes US market hours)
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            is_market_open = market_open <= now <= market_close and now.weekday() < 5
            
            return {
                'is_open': is_market_open,
                'current_time': now.isoformat(),
                'market_open': market_open.isoformat(),
                'market_close': market_close.isoformat(),
                'next_open': self._get_next_market_open(now).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market status: {str(e)}")
            return {'is_open': False, 'error': str(e)}
    
    def _get_next_market_open(self, current_time: datetime) -> datetime:
        """
        Get next market open time
        
        Args:
            current_time: Current datetime
            
        Returns:
            Next market open datetime
        """
        # If it's weekend, next open is Monday
        if current_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
            days_ahead = 7 - current_time.weekday()
            next_open = current_time + timedelta(days=days_ahead)
        else:
            # If it's after market close, next open is tomorrow
            market_close = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
            if current_time > market_close:
                next_open = current_time + timedelta(days=1)
            else:
                next_open = current_time
        
        return next_open.replace(hour=9, minute=30, second=0, microsecond=0) 