#!/usr/bin/env python3
"""
Financial Analyst - Advanced Market Prediction System
Main Flask Application
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import pandas as pd
import numpy as np

# Import our custom modules
from config.settings import Config
from data.collectors.market_data import MarketDataCollector
from analysis.technical.analyzer import TechnicalAnalyzer
from analysis.macroeconomic.analyzer import MacroeconomicAnalyzer
from models.prediction.predictor import MarketPredictor
from visualization.charts.chart_generator import ChartGenerator
from utils.helpers import setup_logging, validate_symbol

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize components
market_collector = MarketDataCollector()
technical_analyzer = TechnicalAnalyzer()
macro_analyzer = MacroeconomicAnalyzer()
predictor = MarketPredictor()
chart_generator = ChartGenerator()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/analysis/<symbol>')
def get_technical_analysis(symbol):
    """Get comprehensive technical analysis for a symbol"""
    try:
        # Validate symbol
        if not validate_symbol(symbol):
            return jsonify({'error': 'Invalid symbol format'}), 400
        
        # Get market data
        data = market_collector.get_stock_data(symbol, period='1y')
        
        # Perform technical analysis
        analysis = technical_analyzer.analyze(data)
        
        # Generate charts
        charts = chart_generator.create_technical_charts(data, analysis)
        
        return jsonify({
            'symbol': symbol,
            'analysis': analysis,
            'charts': charts,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in technical analysis for {symbol}: {str(e)}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/api/prediction/<symbol>')
def get_market_prediction(symbol):
    """Get market predictions for a symbol"""
    try:
        # Validate symbol
        if not validate_symbol(symbol):
            return jsonify({'error': 'Invalid symbol format'}), 400
        
        # Get prediction timeframe from query params
        timeframe = request.args.get('timeframe', '30d')
        
        # Get market data
        data = market_collector.get_stock_data(symbol, period='2y')
        
        # Get macroeconomic context
        macro_context = macro_analyzer.get_current_context()
        
        # Generate predictions
        predictions = predictor.predict(data, macro_context, timeframe)
        
        return jsonify({
            'symbol': symbol,
            'timeframe': timeframe,
            'predictions': predictions,
            'confidence': predictions.get('confidence', 0),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in prediction for {symbol}: {str(e)}")
        return jsonify({'error': 'Prediction failed'}), 500

@app.route('/api/macro/indicators')
def get_macroeconomic_indicators():
    """Get current macroeconomic indicators"""
    try:
        indicators = macro_analyzer.get_global_indicators()
        
        return jsonify({
            'indicators': indicators,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting macroeconomic indicators: {str(e)}")
        return jsonify({'error': 'Failed to fetch indicators'}), 500

@app.route('/api/market/overview')
def get_market_overview():
    """Get overall market overview and sentiment"""
    try:
        # Get major indices
        indices = ['^GSPC', '^DJI', '^IXIC', '^VIX']  # S&P 500, Dow, NASDAQ, VIX
        market_data = {}
        
        for index in indices:
            data = market_collector.get_stock_data(index, period='1m')
            market_data[index] = {
                'current_price': data['Close'].iloc[-1],
                'change': data['Close'].iloc[-1] - data['Close'].iloc[-2],
                'change_percent': ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            }
        
        # Get market sentiment
        sentiment = macro_analyzer.get_market_sentiment()
        
        return jsonify({
            'market_data': market_data,
            'sentiment': sentiment,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting market overview: {str(e)}")
        return jsonify({'error': 'Failed to fetch market overview'}), 500

@app.route('/api/portfolio/optimize', methods=['POST'])
def optimize_portfolio():
    """Optimize portfolio based on risk tolerance and goals"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        risk_tolerance = data.get('risk_tolerance', 'moderate')
        investment_amount = data.get('investment_amount', 100000)
        
        if not symbols:
            return jsonify({'error': 'No symbols provided'}), 400
        
        # Get historical data for all symbols
        portfolio_data = {}
        for symbol in symbols:
            portfolio_data[symbol] = market_collector.get_stock_data(symbol, period='2y')
        
        # Optimize portfolio
        optimization = predictor.optimize_portfolio(portfolio_data, risk_tolerance, investment_amount)
        
        return jsonify({
            'optimization': optimization,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in portfolio optimization: {str(e)}")
        return jsonify({'error': 'Portfolio optimization failed'}), 500

@app.route('/api/search/symbols')
def search_symbols():
    """Search for stock symbols"""
    try:
        query = request.args.get('q', '').upper()
        if len(query) < 2:
            return jsonify({'symbols': []})
        
        # Search for symbols
        symbols = market_collector.search_symbols(query)
        
        return jsonify({
            'symbols': symbols,
            'query': query
        })
    
    except Exception as e:
        logger.error(f"Error searching symbols: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Financial Analyst Application")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    ) 