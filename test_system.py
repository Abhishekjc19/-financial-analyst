#!/usr/bin/env python3
"""
Financial Analyst - System Test Script
Test the core components of the financial analysis system
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all modules can be imported"""
    logger.info("Testing module imports...")
    
    try:
        from data.collectors.market_data import MarketDataCollector
        logger.info("✓ MarketDataCollector imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import MarketDataCollector: {e}")
        return False
    
    try:
        from analysis.technical.analyzer import TechnicalAnalyzer
        logger.info("✓ TechnicalAnalyzer imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import TechnicalAnalyzer: {e}")
        return False
    
    try:
        from analysis.macroeconomic.analyzer import MacroeconomicAnalyzer
        logger.info("✓ MacroeconomicAnalyzer imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import MacroeconomicAnalyzer: {e}")
        return False
    
    try:
        from models.prediction.predictor import MarketPredictor
        logger.info("✓ MarketPredictor imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import MarketPredictor: {e}")
        return False
    
    try:
        from visualization.charts.chart_generator import ChartGenerator
        logger.info("✓ ChartGenerator imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import ChartGenerator: {e}")
        return False
    
    try:
        from utils.helpers import validate_symbol, format_currency
        logger.info("✓ Helper functions imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import helper functions: {e}")
        return False
    
    return True

def test_market_data_collector():
    """Test market data collection"""
    logger.info("Testing market data collection...")
    
    try:
        from data.collectors.market_data import MarketDataCollector
        
        collector = MarketDataCollector()
        
        # Test getting data for a well-known stock
        data = collector.get_stock_data('AAPL', period='5d')
        
        if data is not None and not data.empty:
            logger.info(f"✓ Successfully collected data for AAPL: {len(data)} data points")
            logger.info(f"  Latest price: ${data['Close'].iloc[-1]:.2f}")
            return True
        else:
            logger.error("✗ No data returned for AAPL")
            return False
            
    except Exception as e:
        logger.error(f"✗ Failed to test market data collection: {e}")
        return False

def test_technical_analysis():
    """Test technical analysis"""
    logger.info("Testing technical analysis...")
    
    try:
        from data.collectors.market_data import MarketDataCollector
        from analysis.technical.analyzer import TechnicalAnalyzer
        
        # Get some data first
        collector = MarketDataCollector()
        data = collector.get_stock_data('AAPL', period='1mo')
        
        if data is None or data.empty:
            logger.error("✗ No data available for technical analysis")
            return False
        
        # Perform technical analysis
        analyzer = TechnicalAnalyzer()
        analysis = analyzer.analyze(data)
        
        if analysis and 'summary' in analysis:
            logger.info("✓ Technical analysis completed successfully")
            logger.info(f"  Current price: ${analysis['summary']['current_price']:.2f}")
            logger.info(f"  RSI: {analysis['momentum']['rsi']:.2f}")
            logger.info(f"  Trend: {analysis['trend']['short_term']}")
            return True
        else:
            logger.error("✗ Technical analysis failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Failed to test technical analysis: {e}")
        return False

def test_macroeconomic_analysis():
    """Test macroeconomic analysis"""
    logger.info("Testing macroeconomic analysis...")
    
    try:
        from analysis.macroeconomic.analyzer import MacroeconomicAnalyzer
        
        analyzer = MacroeconomicAnalyzer()
        
        # Test getting global indicators
        indicators = analyzer.get_global_indicators()
        
        if indicators:
            logger.info("✓ Macroeconomic analysis completed successfully")
            logger.info(f"  US GDP Growth: {indicators.get('us_economy', {}).get('gdp_growth', 'N/A')}%")
            logger.info(f"  Unemployment Rate: {indicators.get('us_economy', {}).get('unemployment_rate', 'N/A')}%")
            return True
        else:
            logger.error("✗ No macroeconomic indicators returned")
            return False
            
    except Exception as e:
        logger.error(f"✗ Failed to test macroeconomic analysis: {e}")
        return False

def test_prediction_model():
    """Test prediction model"""
    logger.info("Testing prediction model...")
    
    try:
        from data.collectors.market_data import MarketDataCollector
        from analysis.macroeconomic.analyzer import MacroeconomicAnalyzer
        from models.prediction.predictor import MarketPredictor
        
        # Get data and macro context
        collector = MarketDataCollector()
        data = collector.get_stock_data('AAPL', period='6mo')
        
        macro_analyzer = MacroeconomicAnalyzer()
        macro_context = macro_analyzer.get_current_context()
        
        if data is None or data.empty:
            logger.error("✗ No data available for prediction")
            return False
        
        # Test prediction
        predictor = MarketPredictor()
        predictions = predictor.predict(data, macro_context, '30d')
        
        if predictions:
            logger.info("✓ Prediction model completed successfully")
            logger.info(f"  Confidence: {predictions.get('confidence_metrics', {}).get('overall_confidence', 0):.2f}")
            return True
        else:
            logger.error("✗ No predictions returned")
            return False
            
    except Exception as e:
        logger.error(f"✗ Failed to test prediction model: {e}")
        return False

def test_chart_generation():
    """Test chart generation"""
    logger.info("Testing chart generation...")
    
    try:
        from data.collectors.market_data import MarketDataCollector
        from analysis.technical.analyzer import TechnicalAnalyzer
        from visualization.charts.chart_generator import ChartGenerator
        
        # Get data and analysis
        collector = MarketDataCollector()
        data = collector.get_stock_data('AAPL', period='1mo')
        
        analyzer = TechnicalAnalyzer()
        analysis = analyzer.analyze(data)
        
        if data is None or data.empty:
            logger.error("✗ No data available for chart generation")
            return False
        
        # Test chart generation
        chart_generator = ChartGenerator()
        charts = chart_generator.create_technical_charts(data, analysis)
        
        if charts:
            logger.info("✓ Chart generation completed successfully")
            logger.info(f"  Generated {len(charts)} charts")
            return True
        else:
            logger.error("✗ No charts generated")
            return False
            
    except Exception as e:
        logger.error(f"✗ Failed to test chart generation: {e}")
        return False

def test_utility_functions():
    """Test utility functions"""
    logger.info("Testing utility functions...")
    
    try:
        from utils.helpers import validate_symbol, format_currency, format_percentage
        
        # Test symbol validation
        assert validate_symbol('AAPL') == True
        assert validate_symbol('INVALID!') == False
        logger.info("✓ Symbol validation works correctly")
        
        # Test currency formatting
        formatted = format_currency(1234.56)
        assert '$1,234.56' in formatted
        logger.info("✓ Currency formatting works correctly")
        
        # Test percentage formatting
        formatted = format_percentage(0.1234)
        assert '12.34%' in formatted
        logger.info("✓ Percentage formatting works correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to test utility functions: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("=" * 50)
    logger.info("Financial Analyst System Test")
    logger.info("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Market Data Collection", test_market_data_collector),
        ("Technical Analysis", test_technical_analysis),
        ("Macroeconomic Analysis", test_macroeconomic_analysis),
        ("Prediction Model", test_prediction_model),
        ("Chart Generation", test_chart_generation),
        ("Utility Functions", test_utility_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning test: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The system is ready to use.")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 