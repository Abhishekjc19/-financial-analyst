"""
Macroeconomic Analysis Module
Analyzes global economic indicators and market sentiment
"""

import pandas as pd
import numpy as np
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class MacroeconomicAnalyzer:
    """Analyzes macroeconomic indicators and market sentiment"""
    
    def __init__(self):
        self.indicators = {}
        self.sentiment_data = {}
        self.cache_duration = 3600  # 1 hour
        
    def get_global_indicators(self) -> Dict:
        """
        Get global economic indicators
        
        Returns:
            Dictionary with economic indicators
        """
        try:
            indicators = {
                'us_economy': self._get_us_economic_indicators(),
                'global_markets': self._get_global_market_indicators(),
                'commodities': self._get_commodity_indicators(),
                'currencies': self._get_currency_indicators(),
                'interest_rates': self._get_interest_rate_indicators(),
                'inflation': self._get_inflation_indicators(),
                'employment': self._get_employment_indicators(),
                'geopolitical': self._get_geopolitical_indicators()
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error getting global indicators: {str(e)}")
            return {}
    
    def get_current_context(self) -> Dict:
        """
        Get current macroeconomic context for predictions
        
        Returns:
            Dictionary with current economic context
        """
        try:
            context = {
                'market_regime': self._determine_market_regime(),
                'economic_cycle': self._determine_economic_cycle(),
                'risk_sentiment': self._get_risk_sentiment(),
                'sector_rotation': self._get_sector_rotation_signals(),
                'global_growth': self._get_global_growth_outlook(),
                'policy_environment': self._get_policy_environment(),
                'geopolitical_risk': self._get_geopolitical_risk_score()
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting current context: {str(e)}")
            return {}
    
    def get_market_sentiment(self) -> Dict:
        """
        Get current market sentiment
        
        Returns:
            Dictionary with sentiment indicators
        """
        try:
            sentiment = {
                'fear_greed_index': self._get_fear_greed_index(),
                'vix_analysis': self._get_vix_analysis(),
                'put_call_ratio': self._get_put_call_ratio(),
                'advance_decline': self._get_advance_decline_ratio(),
                'market_breadth': self._get_market_breadth(),
                'institutional_flows': self._get_institutional_flows(),
                'retail_sentiment': self._get_retail_sentiment(),
                'news_sentiment': self._get_news_sentiment()
            }
            
            return sentiment
            
        except Exception as e:
            logger.error(f"Error getting market sentiment: {str(e)}")
            return {}
    
    def _get_us_economic_indicators(self) -> Dict:
        """Get US economic indicators"""
        try:
            # This would typically fetch from FRED API
            # For now, return mock data
            return {
                'gdp_growth': 2.1,
                'unemployment_rate': 3.7,
                'inflation_rate': 3.2,
                'fed_funds_rate': 5.25,
                'consumer_confidence': 108.0,
                'manufacturing_pmi': 49.0,
                'services_pmi': 52.0,
                'retail_sales_growth': 2.5,
                'housing_starts': 1.35,
                'industrial_production': 102.5,
                'capacity_utilization': 78.5,
                'trade_balance': -67.4,
                'budget_deficit': -1.7,
                'debt_to_gdp': 120.0
            }
        except Exception as e:
            logger.error(f"Error getting US economic indicators: {str(e)}")
            return {}
    
    def _get_global_market_indicators(self) -> Dict:
        """Get global market indicators"""
        try:
            return {
                'global_gdp_growth': 2.8,
                'emerging_markets_growth': 4.2,
                'developed_markets_growth': 1.8,
                'global_trade_volume': 1.5,
                'commodity_prices': {
                    'oil': 75.0,
                    'gold': 1950.0,
                    'copper': 3.85,
                    'agricultural': 125.0
                },
                'currency_strength': {
                    'usd': 100.0,
                    'eur': 95.0,
                    'jpy': 150.0,
                    'gbp': 125.0,
                    'cny': 7.2
                }
            }
        except Exception as e:
            logger.error(f"Error getting global market indicators: {str(e)}")
            return {}
    
    def _get_commodity_indicators(self) -> Dict:
        """Get commodity market indicators"""
        try:
            return {
                'energy': {
                    'crude_oil': {'price': 75.0, 'trend': 'neutral'},
                    'natural_gas': {'price': 2.8, 'trend': 'bearish'},
                    'coal': {'price': 120.0, 'trend': 'bullish'}
                },
                'metals': {
                    'gold': {'price': 1950.0, 'trend': 'bullish'},
                    'silver': {'price': 24.5, 'trend': 'bullish'},
                    'copper': {'price': 3.85, 'trend': 'neutral'},
                    'aluminum': {'price': 2.2, 'trend': 'bearish'}
                },
                'agriculture': {
                    'corn': {'price': 4.8, 'trend': 'neutral'},
                    'wheat': {'price': 5.6, 'trend': 'bearish'},
                    'soybeans': {'price': 13.2, 'trend': 'neutral'},
                    'cotton': {'price': 0.85, 'trend': 'bullish'}
                }
            }
        except Exception as e:
            logger.error(f"Error getting commodity indicators: {str(e)}")
            return {}
    
    def _get_currency_indicators(self) -> Dict:
        """Get currency market indicators"""
        try:
            return {
                'major_pairs': {
                    'eur_usd': {'rate': 1.08, 'trend': 'bearish'},
                    'gbp_usd': {'rate': 1.25, 'trend': 'neutral'},
                    'usd_jpy': {'rate': 150.0, 'trend': 'bullish'},
                    'usd_cad': {'rate': 1.35, 'trend': 'neutral'}
                },
                'emerging_currencies': {
                    'usd_cny': {'rate': 7.2, 'trend': 'neutral'},
                    'usd_brl': {'rate': 4.9, 'trend': 'bearish'},
                    'usd_inr': {'rate': 83.0, 'trend': 'neutral'},
                    'usd_mxn': {'rate': 17.5, 'trend': 'bearish'}
                },
                'dollar_index': 100.5,
                'dollar_trend': 'bullish'
            }
        except Exception as e:
            logger.error(f"Error getting currency indicators: {str(e)}")
            return {}
    
    def _get_interest_rate_indicators(self) -> Dict:
        """Get interest rate indicators"""
        try:
            return {
                'us_rates': {
                    'fed_funds': 5.25,
                    '10y_treasury': 4.2,
                    '30y_treasury': 4.5,
                    '2y_treasury': 4.8,
                    'yield_curve': 'inverted'
                },
                'global_rates': {
                    'ecb_rate': 4.0,
                    'boj_rate': -0.1,
                    'boe_rate': 5.25,
                    'pbc_rate': 3.85
                },
                'real_rates': {
                    'us_real_rate': 1.8,
                    'global_real_rate': 1.2
                }
            }
        except Exception as e:
            logger.error(f"Error getting interest rate indicators: {str(e)}")
            return {}
    
    def _get_inflation_indicators(self) -> Dict:
        """Get inflation indicators"""
        try:
            return {
                'us_inflation': {
                    'cpi': 3.2,
                    'core_cpi': 4.1,
                    'pce': 2.9,
                    'core_pce': 3.7,
                    'trend': 'declining'
                },
                'global_inflation': {
                    'eurozone': 2.9,
                    'uk': 4.6,
                    'japan': 3.2,
                    'china': 0.1,
                    'trend': 'mixed'
                },
                'inflation_expectations': {
                    '5y_breakeven': 2.3,
                    '10y_breakeven': 2.4,
                    'survey_based': 2.8
                }
            }
        except Exception as e:
            logger.error(f"Error getting inflation indicators: {str(e)}")
            return {}
    
    def _get_employment_indicators(self) -> Dict:
        """Get employment indicators"""
        try:
            return {
                'us_employment': {
                    'unemployment_rate': 3.7,
                    'labor_force_participation': 62.5,
                    'job_openings': 8.7,
                    'quit_rate': 2.3,
                    'wage_growth': 4.1
                },
                'global_employment': {
                    'eurozone_unemployment': 6.5,
                    'uk_unemployment': 4.2,
                    'japan_unemployment': 2.6,
                    'china_unemployment': 5.2
                }
            }
        except Exception as e:
            logger.error(f"Error getting employment indicators: {str(e)}")
            return {}
    
    def _get_geopolitical_indicators(self) -> Dict:
        """Get geopolitical risk indicators"""
        try:
            return {
                'trade_tensions': {
                    'us_china': 'moderate',
                    'us_eu': 'low',
                    'global_trade': 'stable'
                },
                'political_stability': {
                    'us': 'stable',
                    'europe': 'stable',
                    'asia': 'moderate',
                    'emerging_markets': 'variable'
                },
                'regulatory_environment': {
                    'financial_regulation': 'tightening',
                    'tech_regulation': 'increasing',
                    'environmental_policy': 'expanding'
                }
            }
        except Exception as e:
            logger.error(f"Error getting geopolitical indicators: {str(e)}")
            return {}
    
    def _determine_market_regime(self) -> str:
        """Determine current market regime"""
        try:
            # This would analyze multiple factors to determine regime
            # For now, return a simplified assessment
            return 'bull_market'
        except Exception as e:
            logger.error(f"Error determining market regime: {str(e)}")
            return 'unknown'
    
    def _determine_economic_cycle(self) -> str:
        """Determine current economic cycle phase"""
        try:
            # This would analyze GDP, employment, inflation, etc.
            return 'late_expansion'
        except Exception as e:
            logger.error(f"Error determining economic cycle: {str(e)}")
            return 'unknown'
    
    def _get_risk_sentiment(self) -> Dict:
        """Get current risk sentiment"""
        try:
            return {
                'overall_sentiment': 'neutral',
                'risk_appetite': 'moderate',
                'flight_to_quality': False,
                'risk_off_indicators': ['moderate'],
                'risk_on_indicators': ['moderate']
            }
        except Exception as e:
            logger.error(f"Error getting risk sentiment: {str(e)}")
            return {}
    
    def _get_sector_rotation_signals(self) -> Dict:
        """Get sector rotation signals"""
        try:
            return {
                'leading_sectors': ['technology', 'healthcare'],
                'lagging_sectors': ['energy', 'materials'],
                'rotation_phase': 'growth_to_value',
                'momentum_sectors': ['technology', 'consumer_discretionary']
            }
        except Exception as e:
            logger.error(f"Error getting sector rotation signals: {str(e)}")
            return {}
    
    def _get_global_growth_outlook(self) -> Dict:
        """Get global growth outlook"""
        try:
            return {
                'us_growth': 2.1,
                'eurozone_growth': 0.8,
                'china_growth': 5.0,
                'global_growth': 2.8,
                'growth_momentum': 'slowing',
                'recession_probability': 0.25
            }
        except Exception as e:
            logger.error(f"Error getting global growth outlook: {str(e)}")
            return {}
    
    def _get_policy_environment(self) -> Dict:
        """Get current policy environment"""
        try:
            return {
                'monetary_policy': 'tightening',
                'fiscal_policy': 'neutral',
                'regulatory_policy': 'tightening',
                'trade_policy': 'protectionist',
                'policy_uncertainty': 'moderate'
            }
        except Exception as e:
            logger.error(f"Error getting policy environment: {str(e)}")
            return {}
    
    def _get_geopolitical_risk_score(self) -> float:
        """Get geopolitical risk score (0-100)"""
        try:
            # This would analyze various geopolitical factors
            return 35.0
        except Exception as e:
            logger.error(f"Error getting geopolitical risk score: {str(e)}")
            return 50.0
    
    def _get_fear_greed_index(self) -> Dict:
        """Get fear and greed index"""
        try:
            return {
                'value': 65,
                'category': 'greed',
                'components': {
                    'momentum': 70,
                    'market_volatility': 60,
                    'market_momentum': 65,
                    'put_call_ratio': 55,
                    'junk_bond_demand': 70,
                    'market_volume': 60
                }
            }
        except Exception as e:
            logger.error(f"Error getting fear greed index: {str(e)}")
            return {}
    
    def _get_vix_analysis(self) -> Dict:
        """Get VIX analysis"""
        try:
            return {
                'current_vix': 18.5,
                'vix_percentile': 45,
                'vix_trend': 'declining',
                'fear_level': 'low',
                'expected_volatility': 'normal'
            }
        except Exception as e:
            logger.error(f"Error getting VIX analysis: {str(e)}")
            return {}
    
    def _get_put_call_ratio(self) -> Dict:
        """Get put-call ratio analysis"""
        try:
            return {
                'ratio': 0.85,
                'interpretation': 'neutral',
                'trend': 'declining',
                'sentiment': 'moderately_bullish'
            }
        except Exception as e:
            logger.error(f"Error getting put-call ratio: {str(e)}")
            return {}
    
    def _get_advance_decline_ratio(self) -> Dict:
        """Get advance-decline ratio"""
        try:
            return {
                'ratio': 1.2,
                'interpretation': 'bullish',
                'market_breadth': 'positive',
                'participation': 'broad'
            }
        except Exception as e:
            logger.error(f"Error getting advance-decline ratio: {str(e)}")
            return {}
    
    def _get_market_breadth(self) -> Dict:
        """Get market breadth indicators"""
        try:
            return {
                'new_highs': 150,
                'new_lows': 45,
                'high_low_ratio': 3.33,
                'interpretation': 'bullish',
                'participation': 'broad'
            }
        except Exception as e:
            logger.error(f"Error getting market breadth: {str(e)}")
            return {}
    
    def _get_institutional_flows(self) -> Dict:
        """Get institutional money flows"""
        try:
            return {
                'net_flows': 2.5,  # billions
                'direction': 'inflow',
                'sectors': {
                    'technology': 1.2,
                    'healthcare': 0.8,
                    'financials': -0.3,
                    'energy': -0.2
                }
            }
        except Exception as e:
            logger.error(f"Error getting institutional flows: {str(e)}")
            return {}
    
    def _get_retail_sentiment(self) -> Dict:
        """Get retail investor sentiment"""
        try:
            return {
                'sentiment': 'bullish',
                'confidence': 65,
                'activity_level': 'high',
                'favorite_sectors': ['technology', 'meme_stocks']
            }
        except Exception as e:
            logger.error(f"Error getting retail sentiment: {str(e)}")
            return {}
    
    def _get_news_sentiment(self) -> Dict:
        """Get news sentiment analysis"""
        try:
            return {
                'overall_sentiment': 'positive',
                'sentiment_score': 0.65,
                'news_volume': 'high',
                'key_topics': ['earnings', 'fed_policy', 'tech_innovation']
            }
        except Exception as e:
            logger.error(f"Error getting news sentiment: {str(e)}")
            return {} 