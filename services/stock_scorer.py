import pandas as pd
import numpy as np
from typing import Dict, Optional, Any, List, Tuple
from logger import get_logger

# 获取日志器
logger = get_logger()

class StockScorer:
    """
    股票评分服务
    负责根据技术指标计算股票的综合评分
    """
    
    def __init__(self):
        """初始化股票评分服务"""
        logger.debug("初始化StockScorer")
    
    def calculate_score(self, df: pd.DataFrame) -> int:
        """
        计算股票评分（满分100分）
        
        Args:
            df: 包含技术指标的DataFrame
            
        Returns:
            股票评分（0-100的整数）
        """
        try:
            # 使用最新的数据点进行评分
            latest = df.iloc[-1]
            
            # 初始得分为0
            score = 0
            
            # 移动平均线评分（25分）
            if latest['MA5'] > latest['MA20'] > latest['MA60']:
                # 短期、中期和长期均线呈多头排列
                score += 25
            elif latest['MA5'] > latest['MA20']:
                # 短期均线在中期均线之上
                score += 15
            elif latest['Close'] > latest['MA20']:
                # 股价在中期均线之上
                score += 10
                
            # RSI评分（25分）
            rsi = latest['RSI']
            if 45 <= rsi <= 55:
                # RSI在中间区域，可能即将爆发
                score += 15
            elif 55 < rsi < 70:
                # RSI在强势区域但未超买
                score += 25
            elif 30 < rsi < 45:
                # RSI在弱势区域但未超卖
                score += 10
            elif rsi >= 70:
                # RSI超买
                score += 5
            elif rsi <= 30:
                # RSI超卖
                score += 15
                
            # MACD得分（20分）
            if latest['MACD'] > latest['Signal']:
                score += 20
                
            # 成交量得分（30分）
            if latest['Volume_Ratio'] > 1.5:
                score += 30
            elif latest['Volume_Ratio'] > 1:
                score += 15
                
            return score
            
        except Exception as e:
            logger.error(f"计算评分时出错: {str(e)}")
            logger.exception(e)
            raise
            
    def get_recommendation(self, score: int) -> str:
        """
        根据评分获取投资建议
        
        Args:
            score: 股票评分（0-100）
            
        Returns:
            投资建议文本
        """
        if score >= 80:
            return "强烈推荐"
        elif score >= 70:
            return "推荐"
        elif score >= 60:
            return "谨慎推荐"
        elif score >= 40:
            return "观望"
        elif score >= 20:
            return "不推荐"
        else:
            return "强烈不推荐"
            
    def batch_score_stocks(self, stock_dfs: Dict[str, pd.DataFrame]) -> List[Tuple[str, int, str]]:
        """
        批量评分多只股票
        
        Args:
            stock_dfs: 字典，键为股票代码，值为DataFrame
            
        Returns:
            评分结果列表，每项为(股票代码, 评分, 推荐)的三元组
        """
        results = []
        
        for stock_code, df in stock_dfs.items():
            try:
                score = self.calculate_score(df)
                recommendation = self.get_recommendation(score)
                results.append((stock_code, score, recommendation))
            except Exception as e:
                logger.error(f"评分股票 {stock_code} 时出错: {str(e)}")
                
        # 按评分降序排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results 