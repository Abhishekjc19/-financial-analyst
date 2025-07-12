"""
Utility Helper Functions
Common utilities for the financial analysis system
"""

import os
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np

def setup_logging(log_level: str = 'INFO', log_file: str = 'logs/financial_analyst.log'):
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level
        log_file: Log file path
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def validate_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Remove common prefixes/suffixes
    symbol = symbol.upper().strip()
    
    # Basic validation - alphanumeric and common symbols
    if not re.match(r'^[A-Z0-9\.\-]+$', symbol):
        return False
    
    # Check length
    if len(symbol) < 1 or len(symbol) > 10:
        return False
    
    return True

def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    Format currency amount
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if currency == 'USD':
        return f"${amount:,.2f}"
    elif currency == 'EUR':
        return f"€{amount:,.2f}"
    elif currency == 'GBP':
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format percentage value
    
    Args:
        value: Value to format (as decimal)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimal_places}f}%"

def calculate_returns(prices: pd.Series, periods: List[int] = [1, 5, 20, 252]) -> Dict[str, float]:
    """
    Calculate returns for different periods
    
    Args:
        prices: Price series
        periods: List of periods to calculate
        
    Returns:
        Dictionary with returns for each period
    """
    returns = {}
    
    for period in periods:
        if len(prices) > period:
            returns[f'{period}d_return'] = (prices.iloc[-1] / prices.iloc[-period] - 1) * 100
    
    return returns

def calculate_volatility(prices: pd.Series, window: int = 20) -> float:
    """
    Calculate volatility
    
    Args:
        prices: Price series
        window: Rolling window size
        
    Returns:
        Annualized volatility
    """
    returns = prices.pct_change().dropna()
    if len(returns) < window:
        return 0.0
    
    return returns.rolling(window=window).std().iloc[-1] * np.sqrt(252) * 100

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio
    
    Args:
        returns: Return series
        risk_free_rate: Risk-free rate (annual)
        
    Returns:
        Sharpe ratio
    """
    if len(returns) == 0 or returns.std() == 0:
        return 0.0
    
    excess_returns = returns - risk_free_rate / 252
    return (excess_returns.mean() * 252) / (returns.std() * np.sqrt(252))

def calculate_max_drawdown(prices: pd.Series) -> float:
    """
    Calculate maximum drawdown
    
    Args:
        prices: Price series
        
    Returns:
        Maximum drawdown as percentage
    """
    cumulative = (1 + prices.pct_change()).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min() * 100

def is_market_open() -> bool:
    """
    Check if market is currently open (US market hours)
    
    Returns:
        True if market is open, False otherwise
    """
    now = datetime.now()
    
    # Check if it's a weekday
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Check market hours (9:30 AM - 4:00 PM EST)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return market_open <= now <= market_close

def get_next_market_open() -> datetime:
    """
    Get next market open time
    
    Returns:
        Next market open datetime
    """
    now = datetime.now()
    
    # If it's weekend, next open is Monday
    if now.weekday() >= 5:
        days_ahead = 7 - now.weekday()
        next_open = now + timedelta(days=days_ahead)
    else:
        # If it's after market close, next open is tomorrow
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        if now > market_close:
            next_open = now + timedelta(days=1)
        else:
            next_open = now
    
    return next_open.replace(hour=9, minute=30, second=0, microsecond=0)

def parse_timeframe(timeframe: str) -> int:
    """
    Parse timeframe string to number of days
    
    Args:
        timeframe: Timeframe string (e.g., '1d', '1w', '1m', '1y')
        
    Returns:
        Number of days
    """
    timeframe = timeframe.lower()
    
    if timeframe.endswith('d'):
        return int(timeframe[:-1])
    elif timeframe.endswith('w'):
        return int(timeframe[:-1]) * 7
    elif timeframe.endswith('m'):
        return int(timeframe[:-1]) * 30
    elif timeframe.endswith('y'):
        return int(timeframe[:-1]) * 365
    else:
        return 30  # Default to 30 days

def get_risk_level(volatility: float) -> str:
    """
    Get risk level based on volatility
    
    Args:
        volatility: Annualized volatility percentage
        
    Returns:
        Risk level string
    """
    if volatility < 10:
        return 'low'
    elif volatility < 20:
        return 'medium'
    elif volatility < 30:
        return 'high'
    else:
        return 'very_high'

def get_trend_strength(prices: pd.Series, window: int = 20) -> float:
    """
    Calculate trend strength
    
    Args:
        prices: Price series
        window: Rolling window size
        
    Returns:
        Trend strength (0-100)
    """
    if len(prices) < window:
        return 50.0
    
    # Calculate linear regression slope
    x = np.arange(window)
    y = prices.tail(window).values
    
    slope = np.polyfit(x, y, 1)[0]
    
    # Normalize slope to 0-100 scale
    price_range = prices.max() - prices.min()
    if price_range == 0:
        return 50.0
    
    normalized_slope = (slope / price_range) * 100
    return max(0, min(100, 50 + normalized_slope))

def calculate_correlation_matrix(returns_dict: Dict[str, pd.Series]) -> pd.DataFrame:
    """
    Calculate correlation matrix for multiple assets
    
    Args:
        returns_dict: Dictionary with symbol as key and returns series as value
        
    Returns:
        Correlation matrix DataFrame
    """
    # Combine all returns into a single DataFrame
    returns_df = pd.DataFrame(returns_dict)
    
    # Calculate correlation matrix
    correlation_matrix = returns_df.corr()
    
    return correlation_matrix

def detect_outliers(data: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
    """
    Detect outliers in data
    
    Args:
        data: Data series
        method: Method to use ('iqr', 'zscore')
        threshold: Threshold for outlier detection
        
    Returns:
        Boolean series indicating outliers
    """
    if method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return (data < lower_bound) | (data > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((data - data.mean()) / data.std())
        return z_scores > threshold
    
    else:
        raise ValueError(f"Unknown method: {method}")

def clean_market_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean market data by removing outliers and handling missing values
    
    Args:
        data: Raw market data
        
    Returns:
        Cleaned market data
    """
    cleaned_data = data.copy()
    
    # Handle missing values
    cleaned_data = cleaned_data.fillna(method='ffill')
    cleaned_data = cleaned_data.fillna(method='bfill')
    
    # Remove extreme outliers from price data
    for col in ['Open', 'High', 'Low', 'Close']:
        if col in cleaned_data.columns:
            outliers = detect_outliers(cleaned_data[col], method='iqr', threshold=3)
            cleaned_data.loc[outliers, col] = np.nan
    
    # Forward fill any remaining NaN values
    cleaned_data = cleaned_data.fillna(method='ffill')
    
    return cleaned_data

def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate common technical indicators
    
    Args:
        data: OHLCV data
        
    Returns:
        DataFrame with technical indicators
    """
    indicators = data.copy()
    
    # Moving averages
    indicators['SMA_20'] = indicators['Close'].rolling(window=20).mean()
    indicators['SMA_50'] = indicators['Close'].rolling(window=50).mean()
    indicators['EMA_12'] = indicators['Close'].ewm(span=12).mean()
    indicators['EMA_26'] = indicators['Close'].ewm(span=26).mean()
    
    # RSI
    delta = indicators['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    indicators['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    indicators['MACD'] = indicators['EMA_12'] - indicators['EMA_26']
    indicators['MACD_Signal'] = indicators['MACD'].ewm(span=9).mean()
    indicators['MACD_Histogram'] = indicators['MACD'] - indicators['MACD_Signal']
    
    # Bollinger Bands
    indicators['BB_Middle'] = indicators['Close'].rolling(window=20).mean()
    bb_std = indicators['Close'].rolling(window=20).std()
    indicators['BB_Upper'] = indicators['BB_Middle'] + (bb_std * 2)
    indicators['BB_Lower'] = indicators['BB_Middle'] - (bb_std * 2)
    
    return indicators

def generate_summary_statistics(data: pd.DataFrame) -> Dict:
    """
    Generate summary statistics for market data
    
    Args:
        data: Market data
        
    Returns:
        Dictionary with summary statistics
    """
    if data.empty:
        return {}
    
    returns = data['Close'].pct_change().dropna()
    
    stats = {
        'total_days': len(data),
        'current_price': data['Close'].iloc[-1],
        'price_change': data['Close'].iloc[-1] - data['Close'].iloc[0],
        'price_change_percent': ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100,
        'high_52w': data['High'].max(),
        'low_52w': data['Low'].min(),
        'avg_volume': data['Volume'].mean(),
        'volatility': calculate_volatility(data['Close']),
        'sharpe_ratio': calculate_sharpe_ratio(returns),
        'max_drawdown': calculate_max_drawdown(data['Close']),
        'trend_strength': get_trend_strength(data['Close'])
    }
    
    return stats

def validate_api_response(response: Dict) -> bool:
    """
    Validate API response
    
    Args:
        response: API response dictionary
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(response, dict):
        return False
    
    # Check for common error indicators
    error_keys = ['error', 'Error', 'ERROR', 'message', 'Message']
    for key in error_keys:
        if key in response:
            return False
    
    return True

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default 