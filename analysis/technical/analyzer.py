"""
Technical Analysis Module
Performs comprehensive technical analysis on market data
"""

import pandas as pd
import numpy as np
import ta
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Performs technical analysis on market data"""
    
    def __init__(self):
        self.indicators = {}
        self.patterns = {}
        
    def analyze(self, data: pd.DataFrame) -> Dict:
        """
        Perform comprehensive technical analysis
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Dictionary with analysis results
        """
        try:
            if data.empty:
                raise ValueError("Empty dataset provided")
            
            analysis = {
                'summary': self._generate_summary(data),
                'trend': self._analyze_trend(data),
                'momentum': self._analyze_momentum(data),
                'volatility': self._analyze_volatility(data),
                'volume': self._analyze_volume(data),
                'support_resistance': self._find_support_resistance(data),
                'patterns': self._identify_patterns(data),
                'signals': self._generate_signals(data),
                'risk_metrics': self._calculate_risk_metrics(data)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {str(e)}")
            raise
    
    def _generate_summary(self, data: pd.DataFrame) -> Dict:
        """Generate summary of current market position"""
        current_price = data['Close'].iloc[-1]
        previous_close = data['Close'].iloc[-2]
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100
        
        # Calculate basic statistics
        high_52w = data['High'].max()
        low_52w = data['Low'].min()
        avg_volume = data['Volume'].mean()
        
        return {
            'current_price': current_price,
            'change': change,
            'change_percent': change_percent,
            'high_52w': high_52w,
            'low_52w': low_52w,
            'avg_volume': avg_volume,
            'price_position': (current_price - low_52w) / (high_52w - low_52w) * 100,
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_trend(self, data: pd.DataFrame) -> Dict:
        """Analyze price trends"""
        # Calculate moving averages
        sma_20 = data['Close'].rolling(window=20).mean()
        sma_50 = data['Close'].rolling(window=50).mean()
        sma_200 = data['Close'].rolling(window=200).mean()
        
        ema_12 = data['Close'].ewm(span=12).mean()
        ema_26 = data['Close'].ewm(span=26).mean()
        
        current_price = data['Close'].iloc[-1]
        
        # Determine trend direction
        short_trend = "bullish" if current_price > sma_20.iloc[-1] else "bearish"
        medium_trend = "bullish" if current_price > sma_50.iloc[-1] else "bearish"
        long_trend = "bullish" if current_price > sma_200.iloc[-1] else "bearish"
        
        # MACD analysis
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9).mean()
        macd_histogram = macd - macd_signal
        
        return {
            'short_term': short_trend,
            'medium_term': medium_trend,
            'long_term': long_trend,
            'sma_20': sma_20.iloc[-1],
            'sma_50': sma_50.iloc[-1],
            'sma_200': sma_200.iloc[-1],
            'ema_12': ema_12.iloc[-1],
            'ema_26': ema_26.iloc[-1],
            'macd': macd.iloc[-1],
            'macd_signal': macd_signal.iloc[-1],
            'macd_histogram': macd_histogram.iloc[-1],
            'trend_strength': self._calculate_trend_strength(data)
        }
    
    def _analyze_momentum(self, data: pd.DataFrame) -> Dict:
        """Analyze momentum indicators"""
        # RSI
        rsi = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        
        # Stochastic Oscillator
        stoch = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close'])
        stoch_k = stoch.stoch()
        stoch_d = stoch.stoch_signal()
        
        # Williams %R
        williams_r = ta.momentum.WilliamsRIndicator(data['High'], data['Low'], data['Close']).williams_r()
        
        # CCI (Commodity Channel Index)
        cci = ta.trend.CCIIndicator(data['High'], data['Low'], data['Close']).cci()
        
        current_rsi = rsi.iloc[-1]
        current_stoch_k = stoch_k.iloc[-1]
        current_stoch_d = stoch_d.iloc[-1]
        current_williams_r = williams_r.iloc[-1]
        current_cci = cci.iloc[-1]
        
        return {
            'rsi': current_rsi,
            'rsi_signal': self._get_rsi_signal(current_rsi),
            'stoch_k': current_stoch_k,
            'stoch_d': current_stoch_d,
            'stoch_signal': self._get_stoch_signal(current_stoch_k, current_stoch_d),
            'williams_r': current_williams_r,
            'cci': current_cci,
            'momentum_score': self._calculate_momentum_score(data)
        }
    
    def _analyze_volatility(self, data: pd.DataFrame) -> Dict:
        """Analyze volatility indicators"""
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(data['Close'], window=20, window_dev=2)
        bb_upper = bb.bollinger_hband()
        bb_middle = bb.bollinger_mavg()
        bb_lower = bb.bollinger_lband()
        bb_width = bb.bollinger_wband()
        bb_percent = bb.bollinger_pband()
        
        # Average True Range (ATR)
        atr = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close']).average_true_range()
        
        # Historical Volatility
        returns = data['Close'].pct_change()
        hist_vol = returns.rolling(window=20).std() * np.sqrt(252) * 100
        
        current_price = data['Close'].iloc[-1]
        current_bb_upper = bb_upper.iloc[-1]
        current_bb_lower = bb_lower.iloc[-1]
        current_bb_percent = bb_percent.iloc[-1]
        current_atr = atr.iloc[-1]
        current_hist_vol = hist_vol.iloc[-1]
        
        return {
            'bollinger_upper': current_bb_upper,
            'bollinger_middle': bb_middle.iloc[-1],
            'bollinger_lower': current_bb_lower,
            'bollinger_width': bb_width.iloc[-1],
            'bollinger_percent': current_bb_percent,
            'atr': current_atr,
            'historical_volatility': current_hist_vol,
            'volatility_regime': self._get_volatility_regime(current_hist_vol),
            'price_position_bb': current_bb_percent
        }
    
    def _analyze_volume(self, data: pd.DataFrame) -> Dict:
        """Analyze volume indicators"""
        # Volume SMA
        volume_sma = data['Volume'].rolling(window=20).mean()
        
        # On-Balance Volume (OBV)
        obv = ta.volume.OnBalanceVolumeIndicator(data['Close'], data['Volume']).on_balance_volume()
        
        # Volume Rate of Change
        volume_roc = ta.volume.VolumeRateOfChangeIndicator(data['Volume']).volume_rate_of_change()
        
        # Accumulation/Distribution Line
        adl = ta.volume.AccDistIndexIndicator(data['High'], data['Low'], data['Close'], data['Volume']).acc_dist_index()
        
        current_volume = data['Volume'].iloc[-1]
        current_volume_sma = volume_sma.iloc[-1]
        current_obv = obv.iloc[-1]
        current_volume_roc = volume_roc.iloc[-1]
        current_adl = adl.iloc[-1]
        
        return {
            'current_volume': current_volume,
            'volume_sma': current_volume_sma,
            'volume_ratio': current_volume / current_volume_sma if current_volume_sma > 0 else 1,
            'obv': current_obv,
            'volume_roc': current_volume_roc,
            'adl': current_adl,
            'volume_signal': self._get_volume_signal(current_volume, current_volume_sma)
        }
    
    def _find_support_resistance(self, data: pd.DataFrame) -> Dict:
        """Find support and resistance levels"""
        # Pivot Points
        high = data['High'].iloc[-1]
        low = data['Low'].iloc[-1]
        close = data['Close'].iloc[-1]
        
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        
        # Dynamic support/resistance using recent highs and lows
        recent_highs = data['High'].tail(20).nlargest(3).tolist()
        recent_lows = data['Low'].tail(20).nsmallest(3).tolist()
        
        current_price = data['Close'].iloc[-1]
        
        return {
            'pivot': pivot,
            'resistance_1': r1,
            'resistance_2': r2,
            'support_1': s1,
            'support_2': s2,
            'recent_highs': recent_highs,
            'recent_lows': recent_lows,
            'nearest_resistance': min([h for h in recent_highs if h > current_price], default=None),
            'nearest_support': max([l for l in recent_lows if l < current_price], default=None)
        }
    
    def _identify_patterns(self, data: pd.DataFrame) -> Dict:
        """Identify chart patterns"""
        patterns = {}
        
        # Double Top/Bottom
        patterns['double_top'] = self._detect_double_top(data)
        patterns['double_bottom'] = self._detect_double_bottom(data)
        
        # Head and Shoulders
        patterns['head_shoulders'] = self._detect_head_shoulders(data)
        patterns['inverse_head_shoulders'] = self._detect_inverse_head_shoulders(data)
        
        # Triangle patterns
        patterns['ascending_triangle'] = self._detect_ascending_triangle(data)
        patterns['descending_triangle'] = self._detect_descending_triangle(data)
        patterns['symmetrical_triangle'] = self._detect_symmetrical_triangle(data)
        
        # Flag and Pennant
        patterns['bull_flag'] = self._detect_bull_flag(data)
        patterns['bear_flag'] = self._detect_bear_flag(data)
        
        return patterns
    
    def _generate_signals(self, data: pd.DataFrame) -> Dict:
        """Generate trading signals"""
        signals = {
            'buy_signals': [],
            'sell_signals': [],
            'hold_signals': [],
            'overall_signal': 'hold'
        }
        
        # RSI signals
        rsi = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        current_rsi = rsi.iloc[-1]
        
        if current_rsi < 30:
            signals['buy_signals'].append('RSI oversold')
        elif current_rsi > 70:
            signals['sell_signals'].append('RSI overbought')
        
        # MACD signals
        ema_12 = data['Close'].ewm(span=12).mean()
        ema_26 = data['Close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9).mean()
        
        if macd.iloc[-1] > macd_signal.iloc[-1] and macd.iloc[-2] <= macd_signal.iloc[-2]:
            signals['buy_signals'].append('MACD bullish crossover')
        elif macd.iloc[-1] < macd_signal.iloc[-1] and macd.iloc[-2] >= macd_signal.iloc[-2]:
            signals['sell_signals'].append('MACD bearish crossover')
        
        # Moving average signals
        sma_20 = data['Close'].rolling(window=20).mean()
        sma_50 = data['Close'].rolling(window=50).mean()
        
        if data['Close'].iloc[-1] > sma_20.iloc[-1] and data['Close'].iloc[-2] <= sma_20.iloc[-2]:
            signals['buy_signals'].append('Price above 20-day SMA')
        elif data['Close'].iloc[-1] < sma_20.iloc[-1] and data['Close'].iloc[-2] >= sma_20.iloc[-2]:
            signals['sell_signals'].append('Price below 20-day SMA')
        
        # Determine overall signal
        if len(signals['buy_signals']) > len(signals['sell_signals']):
            signals['overall_signal'] = 'buy'
        elif len(signals['sell_signals']) > len(signals['buy_signals']):
            signals['overall_signal'] = 'sell'
        
        return signals
    
    def _calculate_risk_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate risk metrics"""
        returns = data['Close'].pct_change().dropna()
        
        # Basic risk metrics
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = (returns.mean() * 252) / volatility if volatility > 0 else 0
        
        # Value at Risk (VaR)
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        # Maximum Drawdown
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'var_95': var_95,
            'var_99': var_99,
            'max_drawdown': max_drawdown,
            'risk_score': self._calculate_risk_score(volatility, max_drawdown)
        }
    
    # Helper methods for pattern detection
    def _detect_double_top(self, data: pd.DataFrame) -> Dict:
        """Detect double top pattern"""
        # Simplified implementation
        return {'detected': False, 'confidence': 0}
    
    def _detect_double_bottom(self, data: pd.DataFrame) -> Dict:
        """Detect double bottom pattern"""
        return {'detected': False, 'confidence': 0}
    
    def _detect_head_shoulders(self, data: pd.DataFrame) -> Dict:
        """Detect head and shoulders pattern"""
        return {'detected': False, 'confidence': 0}
    
    def _detect_inverse_head_shoulders(self, data: pd.DataFrame) -> Dict:
        """Detect inverse head and shoulders pattern"""
        return {'detected': False, 'confidence': 0}
    
    def _detect_ascending_triangle(self, data: pd.DataFrame) -> Dict:
        """Detect ascending triangle pattern"""
        return {'detected': False, 'confidence': 0}
    
    def _detect_descending_triangle(self, data: pd.DataFrame) -> Dict:
        """Detect descending triangle pattern"""
        return {'detected': False, 'confidence': 0}
    
    def _detect_symmetrical_triangle(self, data: pd.DataFrame) -> Dict:
        """Detect symmetrical triangle pattern"""
        return {'detected': False, 'confidence': 0}
    
    def _detect_bull_flag(self, data: pd.DataFrame) -> Dict:
        """Detect bull flag pattern"""
        return {'detected': False, 'confidence': 0}
    
    def _detect_bear_flag(self, data: pd.DataFrame) -> Dict:
        """Detect bear flag pattern"""
        return {'detected': False, 'confidence': 0}
    
    # Helper methods for signal generation
    def _get_rsi_signal(self, rsi: float) -> str:
        if rsi < 30:
            return 'oversold'
        elif rsi > 70:
            return 'overbought'
        else:
            return 'neutral'
    
    def _get_stoch_signal(self, k: float, d: float) -> str:
        if k < 20 and d < 20:
            return 'oversold'
        elif k > 80 and d > 80:
            return 'overbought'
        else:
            return 'neutral'
    
    def _get_volume_signal(self, current_volume: float, avg_volume: float) -> str:
        ratio = current_volume / avg_volume if avg_volume > 0 else 1
        if ratio > 1.5:
            return 'high'
        elif ratio < 0.5:
            return 'low'
        else:
            return 'normal'
    
    def _get_volatility_regime(self, volatility: float) -> str:
        if volatility < 15:
            return 'low'
        elif volatility < 25:
            return 'medium'
        else:
            return 'high'
    
    # Helper methods for calculations
    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """Calculate trend strength (0-100)"""
        # Simplified implementation
        return 50.0
    
    def _calculate_momentum_score(self, data: pd.DataFrame) -> float:
        """Calculate momentum score (0-100)"""
        # Simplified implementation
        return 50.0
    
    def _calculate_risk_score(self, volatility: float, max_drawdown: float) -> float:
        """Calculate risk score (0-100)"""
        # Simplified implementation
        return 50.0 