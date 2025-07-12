"""
Configuration settings for Financial Analyst System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # API Keys
    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
    FRED_API_KEY = os.environ.get('FRED_API_KEY')
    
    # Data settings
    DATA_CACHE_DURATION = 300  # 5 minutes
    MAX_DATA_POINTS = 10000
    DEFAULT_PERIOD = '1y'
    
    # Technical Analysis settings
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BOLLINGER_PERIOD = 20
    BOLLINGER_STD = 2
    
    # Prediction settings
    PREDICTION_HORIZON = 30  # days
    CONFIDENCE_THRESHOLD = 0.7
    MIN_DATA_POINTS = 252  # 1 year of trading days
    
    # Risk settings
    MAX_PORTFOLIO_RISK = 0.15  # 15% maximum portfolio risk
    DIVERSIFICATION_MIN = 0.1  # Minimum 10% allocation per asset
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/financial_analyst.log'
    
    # Database (if needed)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # External APIs
    YAHOO_FINANCE_BASE_URL = 'https://query1.finance.yahoo.com'
    ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
    FRED_BASE_URL = 'https://api.stlouisfed.org/fred'
    
    # Chart settings
    CHART_WIDTH = 1200
    CHART_HEIGHT = 600
    CHART_THEME = 'plotly_white'
    
    # Market hours (EST)
    MARKET_OPEN_HOUR = 9
    MARKET_OPEN_MINUTE = 30
    MARKET_CLOSE_HOUR = 16
    MARKET_CLOSE_MINUTE = 0
    
    # Timezone
    TIMEZONE = 'America/New_York'
    
    # Cache settings
    REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_TYPE = 'simple'  # or 'redis'
    
    # Security
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Performance
    MAX_CONCURRENT_REQUESTS = 10
    REQUEST_TIMEOUT = 30
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 