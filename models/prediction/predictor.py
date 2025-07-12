"""
Market Prediction Module
Uses machine learning models to predict market movements
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class MarketPredictor:
    """Predicts market movements using machine learning models"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.target_column = 'target'
        self.prediction_horizon = 30  # days
        
    def predict(self, data: pd.DataFrame, macro_context: Dict, timeframe: str = '30d') -> Dict:
        """
        Generate market predictions
        
        Args:
            data: Historical market data
            macro_context: Macroeconomic context
            timeframe: Prediction timeframe
            
        Returns:
            Dictionary with predictions and confidence
        """
        try:
            if data.empty:
                raise ValueError("Empty dataset provided")
            
            # Prepare features
            features = self._prepare_features(data, macro_context)
            
            # Generate predictions using multiple models
            predictions = {
                'price_predictions': self._predict_price_movement(features, timeframe),
                'trend_predictions': self._predict_trend(features, timeframe),
                'volatility_predictions': self._predict_volatility(features, timeframe),
                'risk_assessment': self._assess_risk(features, macro_context),
                'scenario_analysis': self._generate_scenarios(features, macro_context),
                'confidence_metrics': self._calculate_confidence(features),
                'key_factors': self._identify_key_factors(features, macro_context)
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in market prediction: {str(e)}")
            raise
    
    def optimize_portfolio(self, portfolio_data: Dict, risk_tolerance: str, investment_amount: float) -> Dict:
        """
        Optimize portfolio allocation
        
        Args:
            portfolio_data: Dictionary with symbol as key and DataFrame as value
            risk_tolerance: Risk tolerance level ('conservative', 'moderate', 'aggressive')
            investment_amount: Total investment amount
            
        Returns:
            Dictionary with optimized portfolio
        """
        try:
            # Calculate expected returns and risks for each asset
            asset_analysis = {}
            for symbol, data in portfolio_data.items():
                asset_analysis[symbol] = self._analyze_asset(data)
            
            # Optimize allocation based on risk tolerance
            allocation = self._optimize_allocation(asset_analysis, risk_tolerance, investment_amount)
            
            # Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(allocation, asset_analysis)
            
            return {
                'allocation': allocation,
                'metrics': portfolio_metrics,
                'risk_profile': risk_tolerance,
                'recommendations': self._generate_portfolio_recommendations(allocation, asset_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error in portfolio optimization: {str(e)}")
            raise
    
    def _prepare_features(self, data: pd.DataFrame, macro_context: Dict) -> pd.DataFrame:
        """Prepare features for prediction"""
        try:
            features = data.copy()
            
            # Technical indicators
            features = self._add_technical_features(features)
            
            # Macroeconomic features
            features = self._add_macro_features(features, macro_context)
            
            # Time-based features
            features = self._add_time_features(features)
            
            # Lagged features
            features = self._add_lagged_features(features)
            
            # Remove NaN values
            features = features.dropna()
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}")
            raise
    
    def _add_technical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical analysis features"""
        try:
            # Price-based features
            data['price_change'] = data['Close'].pct_change()
            data['price_change_5d'] = data['Close'].pct_change(5)
            data['price_change_20d'] = data['Close'].pct_change(20)
            
            # Moving averages
            data['sma_5'] = data['Close'].rolling(5).mean()
            data['sma_20'] = data['Close'].rolling(20).mean()
            data['sma_50'] = data['Close'].rolling(50).mean()
            data['ema_12'] = data['Close'].ewm(span=12).mean()
            data['ema_26'] = data['Close'].ewm(span=26).mean()
            
            # Price relative to moving averages
            data['price_vs_sma_20'] = data['Close'] / data['sma_20'] - 1
            data['price_vs_sma_50'] = data['Close'] / data['sma_50'] - 1
            
            # Volatility features
            data['volatility_5d'] = data['price_change'].rolling(5).std()
            data['volatility_20d'] = data['price_change'].rolling(20).std()
            
            # Volume features
            data['volume_change'] = data['Volume'].pct_change()
            data['volume_sma_20'] = data['Volume'].rolling(20).mean()
            data['volume_ratio'] = data['Volume'] / data['volume_sma_20']
            
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            data['macd'] = data['ema_12'] - data['ema_26']
            data['macd_signal'] = data['macd'].ewm(span=9).mean()
            data['macd_histogram'] = data['macd'] - data['macd_signal']
            
            return data
            
        except Exception as e:
            logger.error(f"Error adding technical features: {str(e)}")
            raise
    
    def _add_macro_features(self, data: pd.DataFrame, macro_context: Dict) -> pd.DataFrame:
        """Add macroeconomic features"""
        try:
            # Add macro context as features (simplified)
            data['market_regime'] = 1 if macro_context.get('market_regime') == 'bull_market' else 0
            data['economic_cycle'] = 1 if macro_context.get('economic_cycle') == 'expansion' else 0
            data['risk_sentiment'] = 1 if macro_context.get('risk_sentiment', {}).get('overall_sentiment') == 'positive' else 0
            
            # Add time-invariant macro features
            for i in range(len(data)):
                data.loc[data.index[i], 'fed_rate'] = macro_context.get('interest_rates', {}).get('us_rates', {}).get('fed_funds', 5.25)
                data.loc[data.index[i], 'inflation_rate'] = macro_context.get('inflation', {}).get('us_inflation', {}).get('cpi', 3.2)
                data.loc[data.index[i], 'unemployment_rate'] = macro_context.get('employment', {}).get('us_employment', {}).get('unemployment_rate', 3.7)
            
            return data
            
        except Exception as e:
            logger.error(f"Error adding macro features: {str(e)}")
            raise
    
    def _add_time_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""
        try:
            data['day_of_week'] = data.index.dayofweek
            data['month'] = data.index.month
            data['quarter'] = data.index.quarter
            data['year'] = data.index.year
            
            # Market session features
            data['is_monday'] = (data['day_of_week'] == 0).astype(int)
            data['is_friday'] = (data['day_of_week'] == 4).astype(int)
            data['is_month_end'] = (data.index.day >= 25).astype(int)
            data['is_quarter_end'] = ((data['month'] % 3 == 0) & (data.index.day >= 25)).astype(int)
            
            return data
            
        except Exception as e:
            logger.error(f"Error adding time features: {str(e)}")
            raise
    
    def _add_lagged_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add lagged features"""
        try:
            # Lagged price changes
            for lag in [1, 2, 3, 5, 10]:
                data[f'price_change_lag_{lag}'] = data['price_change'].shift(lag)
                data[f'volume_change_lag_{lag}'] = data['volume_change'].shift(lag)
            
            # Rolling statistics
            data['price_rolling_mean_5'] = data['Close'].rolling(5).mean()
            data['price_rolling_std_5'] = data['Close'].rolling(5).std()
            data['volume_rolling_mean_5'] = data['Volume'].rolling(5).mean()
            
            return data
            
        except Exception as e:
            logger.error(f"Error adding lagged features: {str(e)}")
            raise
    
    def _predict_price_movement(self, features: pd.DataFrame, timeframe: str) -> Dict:
        """Predict price movement"""
        try:
            # Create target variable (future price change)
            features['target'] = features['Close'].shift(-1) / features['Close'] - 1
            
            # Remove rows with NaN target
            features = features.dropna()
            
            if len(features) < 100:
                raise ValueError("Insufficient data for prediction")
            
            # Select feature columns
            feature_cols = [col for col in features.columns if col not in ['target', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            # Split data
            split_idx = int(len(features) * 0.8)
            train_data = features.iloc[:split_idx]
            test_data = features.iloc[split_idx:]
            
            # Train models
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'linear_regression': LinearRegression()
            }
            
            predictions = {}
            for name, model in models.items():
                model.fit(train_data[feature_cols], train_data['target'])
                pred = model.predict(test_data[feature_cols])
                predictions[name] = pred[-1] if len(pred) > 0 else 0
            
            # Ensemble prediction
            ensemble_pred = np.mean(list(predictions.values()))
            
            return {
                'ensemble_prediction': ensemble_pred,
                'individual_predictions': predictions,
                'prediction_horizon': timeframe,
                'confidence': self._calculate_prediction_confidence(predictions)
            }
            
        except Exception as e:
            logger.error(f"Error predicting price movement: {str(e)}")
            return {'ensemble_prediction': 0, 'confidence': 0}
    
    def _predict_trend(self, features: pd.DataFrame, timeframe: str) -> Dict:
        """Predict trend direction"""
        try:
            # Create trend target (1 for uptrend, 0 for downtrend)
            features['trend_target'] = (features['Close'].shift(-5) > features['Close']).astype(int)
            
            # Remove rows with NaN target
            features = features.dropna()
            
            if len(features) < 100:
                raise ValueError("Insufficient data for trend prediction")
            
            # Select feature columns
            feature_cols = [col for col in features.columns if col not in ['trend_target', 'target', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            # Train trend model
            trend_model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # Split data
            split_idx = int(len(features) * 0.8)
            train_data = features.iloc[:split_idx]
            test_data = features.iloc[split_idx:]
            
            trend_model.fit(train_data[feature_cols], train_data['trend_target'])
            trend_prob = trend_model.predict(test_data[feature_cols])
            
            current_trend_prob = trend_prob[-1] if len(trend_prob) > 0 else 0.5
            
            return {
                'trend_probability': current_trend_prob,
                'trend_direction': 'bullish' if current_trend_prob > 0.6 else 'bearish' if current_trend_prob < 0.4 else 'neutral',
                'trend_strength': abs(current_trend_prob - 0.5) * 2
            }
            
        except Exception as e:
            logger.error(f"Error predicting trend: {str(e)}")
            return {'trend_probability': 0.5, 'trend_direction': 'neutral', 'trend_strength': 0}
    
    def _predict_volatility(self, features: pd.DataFrame, timeframe: str) -> Dict:
        """Predict volatility"""
        try:
            # Create volatility target
            features['volatility_target'] = features['price_change'].rolling(5).std()
            
            # Remove rows with NaN target
            features = features.dropna()
            
            if len(features) < 100:
                raise ValueError("Insufficient data for volatility prediction")
            
            # Select feature columns
            feature_cols = [col for col in features.columns if col not in ['volatility_target', 'trend_target', 'target', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            # Train volatility model
            vol_model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # Split data
            split_idx = int(len(features) * 0.8)
            train_data = features.iloc[:split_idx]
            test_data = features.iloc[split_idx:]
            
            vol_model.fit(train_data[feature_cols], train_data['volatility_target'])
            vol_pred = vol_model.predict(test_data[feature_cols])
            
            current_vol_pred = vol_pred[-1] if len(vol_pred) > 0 else features['volatility_target'].mean()
            
            return {
                'predicted_volatility': current_vol_pred,
                'volatility_regime': 'high' if current_vol_pred > 0.03 else 'low' if current_vol_pred < 0.01 else 'medium',
                'volatility_trend': 'increasing' if current_vol_pred > features['volatility_target'].mean() else 'decreasing'
            }
            
        except Exception as e:
            logger.error(f"Error predicting volatility: {str(e)}")
            return {'predicted_volatility': 0.02, 'volatility_regime': 'medium', 'volatility_trend': 'stable'}
    
    def _assess_risk(self, features: pd.DataFrame, macro_context: Dict) -> Dict:
        """Assess investment risk"""
        try:
            # Calculate various risk metrics
            current_volatility = features['volatility_20d'].iloc[-1] if 'volatility_20d' in features.columns else 0.02
            current_price = features['Close'].iloc[-1]
            price_position = (current_price - features['Close'].min()) / (features['Close'].max() - features['Close'].min())
            
            # Risk factors
            risk_factors = {
                'volatility_risk': 'high' if current_volatility > 0.03 else 'medium' if current_volatility > 0.02 else 'low',
                'price_position_risk': 'high' if price_position > 0.8 else 'low' if price_position < 0.2 else 'medium',
                'macro_risk': macro_context.get('geopolitical_risk', 50) / 100,
                'liquidity_risk': 'low',  # Simplified
                'concentration_risk': 'low'  # Simplified
            }
            
            # Overall risk score
            risk_score = self._calculate_overall_risk(risk_factors)
            
            return {
                'risk_score': risk_score,
                'risk_level': 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.4 else 'low',
                'risk_factors': risk_factors,
                'risk_mitigation': self._suggest_risk_mitigation(risk_factors)
            }
            
        except Exception as e:
            logger.error(f"Error assessing risk: {str(e)}")
            return {'risk_score': 0.5, 'risk_level': 'medium', 'risk_factors': {}, 'risk_mitigation': []}
    
    def _generate_scenarios(self, features: pd.DataFrame, macro_context: Dict) -> Dict:
        """Generate scenario analysis"""
        try:
            scenarios = {
                'bull_case': {
                    'probability': 0.3,
                    'price_change': 0.15,
                    'drivers': ['strong_earnings', 'fed_pivot', 'tech_innovation'],
                    'timeframe': '3_months'
                },
                'base_case': {
                    'probability': 0.5,
                    'price_change': 0.05,
                    'drivers': ['steady_growth', 'stable_policy', 'moderate_inflation'],
                    'timeframe': '3_months'
                },
                'bear_case': {
                    'probability': 0.2,
                    'price_change': -0.10,
                    'drivers': ['recession_fears', 'policy_tightening', 'geopolitical_tensions'],
                    'timeframe': '3_months'
                }
            }
            
            return scenarios
            
        except Exception as e:
            logger.error(f"Error generating scenarios: {str(e)}")
            return {}
    
    def _calculate_confidence(self, features: pd.DataFrame) -> Dict:
        """Calculate prediction confidence"""
        try:
            # Simplified confidence calculation
            data_quality = min(1.0, len(features) / 1000)  # More data = higher confidence
            feature_stability = 0.8  # Simplified
            model_agreement = 0.7  # Simplified
            
            overall_confidence = (data_quality + feature_stability + model_agreement) / 3
            
            return {
                'overall_confidence': overall_confidence,
                'data_quality': data_quality,
                'feature_stability': feature_stability,
                'model_agreement': model_agreement,
                'confidence_level': 'high' if overall_confidence > 0.8 else 'medium' if overall_confidence > 0.6 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return {'overall_confidence': 0.5, 'confidence_level': 'medium'}
    
    def _identify_key_factors(self, features: pd.DataFrame, macro_context: Dict) -> List[Dict]:
        """Identify key factors influencing predictions"""
        try:
            key_factors = [
                {
                    'factor': 'Technical Momentum',
                    'impact': 'positive' if features['rsi'].iloc[-1] < 70 else 'negative',
                    'strength': 'high',
                    'description': 'RSI and momentum indicators suggest current trend continuation'
                },
                {
                    'factor': 'Macroeconomic Environment',
                    'impact': 'positive' if macro_context.get('market_regime') == 'bull_market' else 'negative',
                    'strength': 'medium',
                    'description': 'Overall economic conditions support market direction'
                },
                {
                    'factor': 'Volatility Regime',
                    'impact': 'neutral',
                    'strength': 'medium',
                    'description': 'Current volatility levels are within normal range'
                }
            ]
            
            return key_factors
            
        except Exception as e:
            logger.error(f"Error identifying key factors: {str(e)}")
            return []
    
    # Portfolio optimization methods
    def _analyze_asset(self, data: pd.DataFrame) -> Dict:
        """Analyze individual asset for portfolio optimization"""
        try:
            returns = data['Close'].pct_change().dropna()
            
            analysis = {
                'expected_return': returns.mean() * 252,
                'volatility': returns.std() * np.sqrt(252),
                'sharpe_ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0,
                'max_drawdown': self._calculate_max_drawdown(returns),
                'correlation': 0.5  # Simplified
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing asset: {str(e)}")
            return {}
    
    def _optimize_allocation(self, asset_analysis: Dict, risk_tolerance: str, investment_amount: float) -> Dict:
        """Optimize portfolio allocation"""
        try:
            # Simplified optimization based on risk tolerance
            if risk_tolerance == 'conservative':
                # Higher allocation to low-volatility assets
                allocation = {symbol: 0.2 for symbol in asset_analysis.keys()}
            elif risk_tolerance == 'aggressive':
                # Higher allocation to high-return assets
                allocation = {symbol: 0.25 for symbol in asset_analysis.keys()}
            else:  # moderate
                # Balanced allocation
                allocation = {symbol: 1.0 / len(asset_analysis) for symbol in asset_analysis.keys()}
            
            # Calculate dollar amounts
            dollar_allocation = {symbol: allocation[symbol] * investment_amount for symbol in allocation.keys()}
            
            return {
                'percentage_allocation': allocation,
                'dollar_allocation': dollar_allocation,
                'total_investment': investment_amount
            }
            
        except Exception as e:
            logger.error(f"Error optimizing allocation: {str(e)}")
            return {}
    
    def _calculate_portfolio_metrics(self, allocation: Dict, asset_analysis: Dict) -> Dict:
        """Calculate portfolio metrics"""
        try:
            # Simplified portfolio metrics calculation
            total_return = sum(allocation['percentage_allocation'][symbol] * asset_analysis[symbol]['expected_return'] 
                             for symbol in asset_analysis.keys())
            
            total_risk = sum(allocation['percentage_allocation'][symbol] * asset_analysis[symbol]['volatility'] 
                           for symbol in asset_analysis.keys())
            
            return {
                'expected_return': total_return,
                'expected_volatility': total_risk,
                'sharpe_ratio': total_return / total_risk if total_risk > 0 else 0,
                'diversification_score': 0.8  # Simplified
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {str(e)}")
            return {}
    
    def _generate_portfolio_recommendations(self, allocation: Dict, asset_analysis: Dict) -> List[str]:
        """Generate portfolio recommendations"""
        try:
            recommendations = [
                "Consider rebalancing quarterly to maintain target allocation",
                "Monitor macroeconomic factors that may impact sector performance",
                "Review risk tolerance and adjust allocation if needed",
                "Consider adding international exposure for diversification"
            ]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    # Helper methods
    def _calculate_prediction_confidence(self, predictions: Dict) -> float:
        """Calculate confidence based on model agreement"""
        try:
            values = list(predictions.values())
            if len(values) == 0:
                return 0.5
            
            # Higher confidence if models agree
            std_dev = np.std(values)
            confidence = max(0.1, 1 - std_dev)
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating prediction confidence: {str(e)}")
            return 0.5
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return drawdown.min()
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {str(e)}")
            return 0.0
    
    def _calculate_overall_risk(self, risk_factors: Dict) -> float:
        """Calculate overall risk score"""
        try:
            # Simplified risk calculation
            risk_score = 0.0
            weights = {'volatility_risk': 0.3, 'price_position_risk': 0.2, 'macro_risk': 0.3, 'liquidity_risk': 0.1, 'concentration_risk': 0.1}
            
            for factor, weight in weights.items():
                if factor in risk_factors:
                    if isinstance(risk_factors[factor], str):
                        if risk_factors[factor] == 'high':
                            risk_score += weight * 0.8
                        elif risk_factors[factor] == 'medium':
                            risk_score += weight * 0.5
                        else:
                            risk_score += weight * 0.2
                    else:
                        risk_score += weight * risk_factors[factor]
            
            return min(1.0, risk_score)
            
        except Exception as e:
            logger.error(f"Error calculating overall risk: {str(e)}")
            return 0.5
    
    def _suggest_risk_mitigation(self, risk_factors: Dict) -> List[str]:
        """Suggest risk mitigation strategies"""
        try:
            suggestions = []
            
            if risk_factors.get('volatility_risk') == 'high':
                suggestions.append("Consider hedging strategies or options")
            
            if risk_factors.get('price_position_risk') == 'high':
                suggestions.append("Consider taking partial profits")
            
            if risk_factors.get('macro_risk', 0) > 0.6:
                suggestions.append("Monitor macroeconomic indicators closely")
            
            if not suggestions:
                suggestions.append("Current risk levels are manageable")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting risk mitigation: {str(e)}")
            return ["Consult with financial advisor"] 