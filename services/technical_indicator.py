import pandas as pd
import numpy as np
from typing import Dict, Optional, Any
from logger import get_logger

# 获取日志器
logger = get_logger()

class TechnicalIndicator:
    """
    技术指标计算服务
    负责计算常见的股票技术指标
    """
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """
        初始化技术指标计算服务
        
        Args:
            params: 技术指标参数配置
        """
        # 默认参数设置
        self.params = params or {
            'ma_periods': {'short': 5, 'medium': 20, 'long': 60},
            'rsi_period': 14,
            'bollinger_period': 20,
            'bollinger_std': 2,
            'volume_ma_period': 20,
            'atr_period': 14
        }
        
        logger.debug(f"初始化TechnicalIndicator，参数: {self.params}")
    
    def calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        """
        计算指数移动平均线
        
        Args:
            series: 价格序列
            period: 周期
            
        Returns:
            EMA序列
        """
        return series.ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, series: pd.Series, period: int) -> pd.Series:
        """
        计算相对强弱指标(RSI)
        
        Args:
            series: 价格序列
            period: 周期
            
        Returns:
            RSI序列
        """
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, series: pd.Series) -> tuple:
        """
        计算MACD指标
        
        Args:
            series: 价格序列
            
        Returns:
            (MACD线, 信号线, 柱状图)的元组
        """
        ema12 = self.calculate_ema(series, 12)
        ema26 = self.calculate_ema(series, 26)
        
        macd = ema12 - ema26
        signal = self.calculate_ema(macd, 9)
        histogram = macd - signal
        
        return macd, signal, histogram
    
    def calculate_bollinger_bands(self, series: pd.Series, period: int, std_dev: float) -> tuple:
        """
        计算布林带
        
        Args:
            series: 价格序列
            period: 周期
            std_dev: 标准差倍数
            
        Returns:
            (中轨, 上轨, 下轨)的元组
        """
        middle = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        
        upper = middle + std_dev * std
        lower = middle - std_dev * std
        
        return middle, upper, lower
    
    def calculate_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        计算平均真实波幅(ATR)
        
        Args:
            df: 包含High, Low, Close列的DataFrame
            period: 周期
            
        Returns:
            ATR序列
        """
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有技术指标
        
        Args:
            df: 原始价格数据，包含Open, High, Low, Close, Volume列
            
        Returns:
            添加了技术指标的DataFrame
        """
        try:
            # 复制数据框
            result_df = df.copy()
            
            # 移动平均线
            for name, period in self.params['ma_periods'].items():
                result_df[f'MA{period}'] = result_df['Close'].rolling(window=period).mean()
            
            # RSI
            result_df['RSI'] = self.calculate_rsi(result_df['Close'], self.params['rsi_period'])
            
            # MACD
            macd, signal, histogram = self.calculate_macd(result_df['Close'])
            result_df['MACD'] = macd
            result_df['Signal'] = signal
            result_df['Histogram'] = histogram
            
            # 布林带
            middle, upper, lower = self.calculate_bollinger_bands(
                result_df['Close'], 
                self.params['bollinger_period'], 
                self.params['bollinger_std']
            )
            result_df['BB_Middle'] = middle
            result_df['BB_Upper'] = upper
            result_df['BB_Lower'] = lower
            
            # 成交量移动平均
            result_df['Volume_MA'] = result_df['Volume'].rolling(window=self.params['volume_ma_period']).mean()
            
            # 成交量比率
            result_df['Volume_Ratio'] = result_df['Volume'] / result_df['Volume_MA']
            
            # ATR
            result_df['ATR'] = self.calculate_atr(result_df, self.params['atr_period'])
            
            # 波动率 (过去20天收盘价的标准差/均值)
            result_df['Volatility'] = result_df['Close'].rolling(window=20).std() / result_df['Close'].rolling(window=20).mean() * 100
            
            return result_df
            
        except Exception as e:
            logger.error(f"计算技术指标时出错: {str(e)}")
            logger.exception(e)
            raise 