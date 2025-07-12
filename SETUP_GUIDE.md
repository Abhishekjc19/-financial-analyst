# Financial Analyst - Setup Guide

## 🚀 Quick Start

This guide will help you set up and run the Financial Analyst system, which provides advanced stock market predictions based on technical analysis and macroeconomic indicators.

## 📋 Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Git** (for cloning the repository)
- **Internet connection** (for fetching market data)

## 🛠️ Installation Steps

### 1. Clone or Download the Project

If you have Git:
```bash
git clone <repository-url>
cd Financial-Analyst
```

Or download and extract the ZIP file to your desired location.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** Some packages might take a few minutes to install, especially TensorFlow and other ML libraries.

### 3. Set Up Environment Variables

Copy the example environment file:
```bash
cp env_example.txt .env
```

Edit the `.env` file with your API keys:

```bash
# Required API Keys (Get these from respective services)
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key-here
FRED_API_KEY=your-fred-api-key-here

# Optional: Change these if needed
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_DEBUG=True
LOG_LEVEL=INFO
```

### 4. Get API Keys

#### Alpha Vantage API Key (Free)
1. Go to [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Sign up for a free account
3. Get your API key
4. Add it to your `.env` file

#### FRED API Key (Free)
1. Go to [FRED API](https://fred.stlouisfed.org/docs/api/api_key.html)
2. Sign up for a free account
3. Get your API key
4. Add it to your `.env` file

## 🧪 Testing the Installation

Run the system test to verify everything is working:

```bash
python test_system.py
```

You should see output like:
```
==================================================
Financial Analyst System Test
==================================================

Running test: Module Imports
✓ MarketDataCollector imported successfully
✓ TechnicalAnalyzer imported successfully
✓ MacroeconomicAnalyzer imported successfully
✓ MarketPredictor imported successfully
✓ ChartGenerator imported successfully
✓ Helper functions imported successfully
✓ Module Imports PASSED

Running test: Market Data Collection
✓ Successfully collected data for AAPL: 5 data points
  Latest price: $150.25
✓ Market Data Collection PASSED

...

🎉 All tests passed! The system is ready to use.
```

## 🚀 Running the Application

### Option 1: Using the Startup Script (Recommended)

```bash
python run.py
```

### Option 2: Direct Flask Run

```bash
python app.py
```

### Option 3: Using Flask CLI

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

## 🌐 Accessing the Dashboard

Once the application is running, open your web browser and go to:

```
http://localhost:5000
```

You should see the Financial Analyst dashboard with:
- Market overview
- Stock analysis tools
- Interactive charts
- Prediction capabilities

## 📊 Using the System

### 1. Market Overview
The dashboard shows real-time market data for major indices:
- S&P 500
- Dow Jones Industrial Average
- NASDAQ Composite
- VIX (Volatility Index)

### 2. Stock Analysis
1. Enter a stock symbol (e.g., AAPL, MSFT, GOOGL)
2. Select a timeframe (1 day to 2 years)
3. Click "Analyze" to get technical analysis
4. Click "Get Predictions" for market forecasts

### 3. Technical Analysis Features
- **Price Charts**: Candlestick charts with moving averages
- **Technical Indicators**: RSI, MACD, Bollinger Bands
- **Support/Resistance**: Key price levels
- **Volume Analysis**: Trading volume patterns
- **Trend Analysis**: Short, medium, and long-term trends

### 4. Predictions
- **Price Predictions**: 30-day price forecasts
- **Trend Predictions**: Market direction analysis
- **Risk Assessment**: Investment risk evaluation
- **Scenario Analysis**: Bull, bear, and base cases

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | Required |
| `FRED_API_KEY` | FRED API key | Required |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `FLASK_DEBUG` | Debug mode | True |
| `LOG_LEVEL` | Logging level | INFO |
| `CHART_WIDTH` | Chart width | 1200 |
| `CHART_HEIGHT` | Chart height | 600 |

### Customizing Analysis Parameters

Edit `config/settings.py` to modify:
- Technical indicator parameters
- Prediction horizons
- Risk thresholds
- Chart themes

## 📁 Project Structure

```
Financial-Analyst/
├── app.py                 # Main Flask application
├── run.py                 # Startup script
├── test_system.py         # System test script
├── requirements.txt       # Python dependencies
├── env_example.txt        # Environment variables example
├── README.md             # Project documentation
├── SETUP_GUIDE.md        # This file
├── config/               # Configuration files
│   ├── settings.py       # Main settings
│   └── __init__.py
├── data/                 # Data collection
│   ├── collectors/       # Market data collectors
│   └── __init__.py
├── analysis/             # Analysis modules
│   ├── technical/        # Technical analysis
│   ├── macroeconomic/    # Macroeconomic analysis
│   └── __init__.py
├── models/               # Machine learning models
│   ├── prediction/       # Prediction algorithms
│   └── __init__.py
├── visualization/        # Chart generation
│   ├── charts/          # Chart components
│   └── __init__.py
├── utils/               # Utility functions
│   ├── helpers.py       # Helper functions
│   └── __init__.py
└── templates/           # Web templates
    └── dashboard.html   # Main dashboard
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: `ModuleNotFoundError` when running the application
**Solution**: 
```bash
pip install -r requirements.txt
```

#### 2. API Key Errors
**Problem**: "Invalid API key" errors
**Solution**: 
- Verify your API keys in the `.env` file
- Check if you've exceeded API rate limits
- Ensure the keys are correct and active

#### 3. Data Fetching Issues
**Problem**: No data returned for stocks
**Solution**:
- Check your internet connection
- Verify the stock symbol is valid
- Try a different stock symbol

#### 4. Chart Display Issues
**Problem**: Charts not displaying properly
**Solution**:
- Clear browser cache
- Check browser console for JavaScript errors
- Ensure Plotly.js is loading correctly

#### 5. Port Already in Use
**Problem**: "Address already in use" error
**Solution**:
```bash
# Find and kill the process using port 5000
lsof -ti:5000 | xargs kill -9
```

### Getting Help

1. **Check the logs**: Look at the console output for error messages
2. **Run the test script**: `python test_system.py` to identify issues
3. **Verify dependencies**: Ensure all packages are installed correctly
4. **Check API keys**: Verify your API keys are valid and active

## 🔒 Security Considerations

1. **Never commit API keys**: Keep your `.env` file out of version control
2. **Use HTTPS in production**: Always use HTTPS when deploying
3. **Regular updates**: Keep dependencies updated for security patches
4. **Rate limiting**: Be aware of API rate limits

## 📈 Performance Optimization

### For Better Performance:

1. **Enable caching**: Set up Redis for data caching
2. **Optimize data fetching**: Use appropriate timeframes
3. **Reduce chart complexity**: Limit the number of indicators
4. **Use production settings**: Set `FLASK_DEBUG=False`

### Memory Usage:

- The system uses approximately 200-500MB of RAM
- Large datasets may require more memory
- Consider using data sampling for very large datasets

## 🚀 Deployment

### Local Development
```bash
python run.py
```

### Production Deployment
1. Set `FLASK_DEBUG=False`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Set up proper logging
4. Configure environment variables
5. Use HTTPS

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📞 Support

If you encounter issues:

1. Check this setup guide
2. Run the test script: `python test_system.py`
3. Review the console logs for error messages
4. Verify your API keys and internet connection

## 🎯 Next Steps

After successful setup:

1. **Explore the dashboard**: Try analyzing different stocks
2. **Customize settings**: Modify analysis parameters
3. **Add more data sources**: Integrate additional APIs
4. **Extend functionality**: Add new technical indicators
5. **Deploy to production**: Set up for production use

## 📝 License

This project is for educational and research purposes. Please ensure compliance with API terms of service and local regulations.

---

**Happy Trading! 📈**

The Financial Analyst system is now ready to provide you with advanced market insights and predictions. 