import asyncio
import pandas as pd
from typing import List, Dict, Any, Optional
from logger import get_logger
from datetime import datetime, timedelta

# 获取日志器
logger = get_logger()

class FundServiceAsync:
    """
    异步基金服务
    提供基金数据的异步搜索和获取功能
    """
    
    def __init__(self):
        """初始化异步基金服务"""
        logger.debug("初始化FundServiceAsync")
        
        # 添加缓存
        self._etf_cache = None
        self._lof_cache = None
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=30)  # 缓存30分钟
    
    async def search_funds(self, keyword: str, market_type: str = 'ETF') -> List[Dict[str, Any]]:
        """
        异步搜索基金代码
        
        Args:
            keyword: 搜索关键词
            market_type: 市场类型，'ETF'或'LOF'
            
        Returns:
            匹配的基金列表
        """
        try:
            logger.info(f"异步搜索基金: {keyword}, 类型: {market_type}")
            
            # 获取基金数据
            df = await self._get_funds_data(market_type)
            
            # 模糊匹配搜索（同时匹配代码和名称）
            mask = (df['name'].str.contains(keyword, case=False, na=False) | 
                   df['symbol'].str.contains(keyword, case=False, na=False))
            results = df[mask]
            
            # 格式化返回结果并处理 NaN 值
            formatted_results = []
            for _, row in results.iterrows():
                formatted_results.append({
                    'name': row['name'] if pd.notna(row['name']) else '',
                    'symbol': str(row['symbol']) if pd.notna(row['symbol']) else '',
                    'price': float(row['price']) if pd.notna(row['price']) else 0.0,
                    'volume': float(row['volume']) if pd.notna(row['volume']) else 0.0,
                    'market_value': float(row['market_value']) if pd.notna(row['market_value']) else 0.0,
                    'total_value': float(row['total_value']) if pd.notna(row['total_value']) else 0.0,
                })
                # 限制只返回前10个结果
                if len(formatted_results) >= 10:
                    break
            
            logger.info(f"基金搜索完成，找到 {len(formatted_results)} 个匹配项（限制显示前10个）")
            return formatted_results
            
        except Exception as e:
            error_msg = f"搜索基金代码失败: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            raise Exception(error_msg)
    
    async def _get_funds_data(self, market_type: str = 'ETF') -> pd.DataFrame:
        """
        异步获取基金数据，支持缓存
        
        Args:
            market_type: 市场类型，'ETF'或'LOF'
            
        Returns:
            包含基金数据的DataFrame
        """
        # 检查缓存是否有效
        now = datetime.now()
        cache_valid = (
            self._cache_timestamp is not None and 
            (now - self._cache_timestamp) < self._cache_duration
        )
        
        if market_type == 'ETF' and cache_valid and self._etf_cache is not None:
            logger.debug("使用ETF缓存数据")
            return self._etf_cache
        elif market_type == 'LOF' and cache_valid and self._lof_cache is not None:
            logger.debug("使用LOF缓存数据")
            return self._lof_cache
        
        # 缓存无效，重新获取数据
        try:
            logger.debug(f"从API获取{market_type}数据")
            
            # 使用线程池执行同步的akshare调用
            if market_type == 'ETF':
                df = await asyncio.to_thread(self._get_etf_data)
                self._etf_cache = df
            else:
                df = await asyncio.to_thread(self._get_lof_data)
                self._lof_cache = df
                
            self._cache_timestamp = now
            return df
            
        except Exception as e:
            logger.error(f"获取{market_type}数据失败: {str(e)}")
            logger.exception(e)
            raise
    
    def _get_etf_data(self) -> pd.DataFrame:
        """
        获取ETF数据（同步方法，将被异步方法调用）
        
        Returns:
            包含ETF数据的DataFrame
        """
        import akshare as ak
        
        try:
            # 获取ETF基金数据
            df = ak.fund_etf_spot_em()
            
            # 转换列名
            df = df.rename(columns={
                "代码": "symbol",
                "名称": "name",
                "最新价": "price",
                "涨跌额": "price_change",
                "涨跌幅": "price_change_percent",
                "成交量": "volume",
                "流通市值": "market_value",
                "总市值": "total_value",
                "基金折价率": "discount_rate",
            })
            
            return df
            
        except Exception as e:
            logger.error(f"获取ETF数据失败: {str(e)}")
            logger.exception(e)
            raise Exception(f"获取ETF数据失败: {str(e)}")
    
    def _get_lof_data(self) -> pd.DataFrame:
        """
        获取LOF数据（同步方法，将被异步方法调用）
        
        Returns:
            包含LOF数据的DataFrame
        """
        import akshare as ak
        
        try:
            # 获取LOF基金数据
            df = ak.fund_lof_spot_em()
            
            # 转换列名
            df = df.rename(columns={
                "代码": "symbol",
                "名称": "name",
                "最新价": "price",
                "涨跌额": "price_change",
                "涨跌幅": "price_change_percent",
                "成交量": "volume",
                "流通市值": "market_value",
                "总市值": "total_value",
                "基金折价率": "discount_rate",
            })
            
            return df
            
        except Exception as e:
            logger.error(f"获取LOF数据失败: {str(e)}")
            logger.exception(e)
            raise Exception(f"获取LOF数据失败: {str(e)}")
            
    async def get_fund_detail(self, symbol: str, market_type: str = 'ETF') -> Dict[str, Any]:
        """
        异步获取单个基金详细信息
        
        Args:
            symbol: 基金代码
            market_type: 市场类型，'ETF'或'LOF'
            
        Returns:
            基金详细信息
        """
        try:
            logger.info(f"获取{market_type}基金详情: {symbol}")
            
            # 获取基金数据
            df = await self._get_funds_data(market_type)
            
            # 精确匹配基金代码
            result = df[df['symbol'] == symbol]
            
            if len(result) == 0:
                raise Exception(f"未找到基金代码: {symbol}")
            
            # 获取第一行数据
            row = result.iloc[0]
            
            # 格式化为字典
            fund_detail = {
                'name': row['name'] if pd.notna(row['name']) else '',
                'symbol': str(row['symbol']) if pd.notna(row['symbol']) else '',
                'price': float(row['price']) if pd.notna(row['price']) else 0.0,
                'price_change': float(row['price_change']) if pd.notna(row['price_change']) else 0.0,
                'price_change_percent': float(row['price_change_percent'].strip('%'))/100 if pd.notna(row['price_change_percent']) else 0.0,
                'volume': float(row['volume']) if pd.notna(row['volume']) else 0.0,
                'market_value': float(row['market_value']) if pd.notna(row['market_value']) else 0.0,
                'total_value': float(row['total_value']) if pd.notna(row['total_value']) else 0.0,
                'discount_rate': float(row['discount_rate'].strip('%'))/100 if pd.notna(row['discount_rate']) else 0.0
            }
            
            logger.info(f"获取基金详情成功: {symbol}")
            return fund_detail
            
        except Exception as e:
            error_msg = f"获取基金详情失败: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            raise Exception(error_msg) 