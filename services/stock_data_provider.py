import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import os
from typing import Dict, List, Optional, Tuple, Any
from logger import get_logger
import re

# 获取日志器
logger = get_logger()

class StockDataProvider:
    """
    异步股票数据提供服务
    负责获取股票、基金等金融产品的历史数据
    """
    
    def __init__(self):
        """初始化数据提供者服务"""
        logger.debug("初始化StockDataProvider")
    
    async def get_stock_data(self, stock_code: str, market_type: str = 'A', 
                            start_date: Optional[str] = None, 
                            end_date: Optional[str] = None) -> pd.DataFrame:
        """
        异步获取股票或基金数据
        
        Args:
            stock_code: 股票代码
            market_type: 市场类型，默认为'A'股
            start_date: 开始日期，格式YYYYMMDD，默认为一年前
            end_date: 结束日期，格式YYYYMMDD，默认为今天
            
        Returns:
            包含历史数据的DataFrame
        """
        # 使用线程池执行同步的akshare调用
        return await asyncio.to_thread(
            self._get_stock_data_sync, 
            stock_code, 
            market_type, 
            start_date, 
            end_date
        )
    
    def _get_stock_data_sync(self, stock_code: str, market_type: str = 'A', 
                           start_date: Optional[str] = None, 
                           end_date: Optional[str] = None) -> pd.DataFrame:
        """
        同步获取股票数据的实现
        将被异步方法调用
        """
        import akshare as ak
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
            
        # 确保日期格式统一（移除可能的'-'符号）
        if isinstance(start_date, str) and '-' in start_date:
            start_date = start_date.replace('-', '')
        if isinstance(end_date, str) and '-' in end_date:
            end_date = end_date.replace('-', '')
            
        try:
            if market_type == 'A':
                logger.debug(f"获取A股数据: {stock_code}")
                
                df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
                
            elif market_type in ['HK']:
                logger.debug(f"获取港股数据: {stock_code}")
                df = ak.stock_hk_daily(
                    symbol=stock_code,
                    adjust="qfq"
                )
                
                # 在获取数据后进行日期过滤
                try:
                    if not isinstance(df.index, pd.DatetimeIndex):
                        # 如果存在命名为'date'的列，将其设为索引
                        if 'date' in df.columns:
                            df['date'] = pd.to_datetime(df['date'])
                            df.set_index('date', inplace=True)
                        else:
                            # 尝试将第一列转换为日期索引
                            date_col = df.columns[0]
                            df[date_col] = pd.to_datetime(df[date_col])
                            df.set_index(date_col, inplace=True)
                    
                    # 转换日期字符串为日期对象
                    if start_date:
                        if start_date.isdigit() and len(start_date) == 8:
                            start_date_dt = pd.to_datetime(start_date, format='%Y%m%d')
                        else:
                            start_date_dt = pd.to_datetime(start_date)
                    else:
                        start_date_dt = pd.to_datetime((datetime.now() - timedelta(days=365)).strftime('%Y%m%d'))
                        
                    if end_date:
                        if end_date.isdigit() and len(end_date) == 8:
                            end_date_dt = pd.to_datetime(end_date, format='%Y%m%d')
                        else:
                            end_date_dt = pd.to_datetime(end_date)
                    else:
                        end_date_dt = pd.to_datetime(datetime.now().strftime('%Y%m%d'))
                    
                    # 过滤日期范围
                    df = df[(df.index >= start_date_dt) & (df.index <= end_date_dt)]
                    logger.debug(f"港股日期过滤后数据点数: {len(df)}")
                    
                except Exception as e:
                    logger.warning(f"港股日期过滤出错: {str(e)}，使用原始数据")
                
            elif market_type in ['US']:
                logger.debug(f"获取美股数据: {stock_code}")
                try:
                    df = ak.stock_us_daily(
                        symbol=stock_code,
                        adjust="qfq"
                    )
                    logger.debug(f"美股数据原始列: {df.columns.tolist()}")
                    logger.debug(f"美股数据形状: {df.shape}")
                    
                    # 确保索引是日期时间类型
                    if not isinstance(df.index, pd.DatetimeIndex):
                        # 如果存在命名为'date'的列，将其设为索引
                        if 'date' in df.columns:
                            df['date'] = pd.to_datetime(df['date'])
                            df.set_index('date', inplace=True)
                            logger.debug("已将'date'列设置为索引")
                        else:
                            # 否则将当前索引转换为日期类型
                            df.index = pd.to_datetime(df.index)
                            logger.debug("已将索引转换为DatetimeIndex")
                    
                    # 计算美股的成交额（Amount）= 成交量（Volume）× 收盘价（Close）
                    volume_col = next((col for col in df.columns if col.lower() == 'volume'), None)
                    close_col = next((col for col in df.columns if col.lower() == 'close'), None)
                    
                    if volume_col and close_col:
                        df['amount'] = df[volume_col] * df[close_col]
                        logger.debug("已为美股数据计算成交额(amount)字段")
                    else:
                        logger.warning(f"美股数据缺少volume或close列，无法计算amount。当前列: {df.columns.tolist()}")
                        # 添加空的amount列，避免后续处理错误
                        df['amount'] = 0.0
                        
                    # 将所有列名转为小写以进行统一处理
                    df.columns = [col.lower() for col in df.columns]
                    
                except Exception as e:
                    logger.error(f"获取美股数据失败 {stock_code}: {str(e)}")
                    raise ValueError(f"获取美股数据失败 {stock_code}: {str(e)}")
                
                # 将字符串日期转换为日期时间对象进行比较
                try:
                    # 尝试多种格式解析日期
                    # 如果日期是数字格式（20220101），使用适当的格式
                    if start_date.isdigit() and len(start_date) == 8:
                        start_date_dt = pd.to_datetime(start_date, format='%Y%m%d')
                    else:
                        # 否则让pandas自动推断格式
                        start_date_dt = pd.to_datetime(start_date)
                        
                    if end_date.isdigit() and len(end_date) == 8:
                        end_date_dt = pd.to_datetime(end_date, format='%Y%m%d')
                    else:
                        end_date_dt = pd.to_datetime(end_date)
                except Exception as e:
                    logger.warning(f"日期转换出错: {str(e)}，使用默认值")
                    # 如果转换失败，使用合理的默认值
                    start_date_dt = pd.to_datetime('20000101', format='%Y%m%d')
                    end_date_dt = pd.to_datetime(datetime.now().strftime('%Y%m%d'), format='%Y%m%d')
                
                # 过滤日期
                try:
                    df = df[(df.index >= start_date_dt) & (df.index <= end_date_dt)]
                    logger.debug(f"日期过滤后数据点数: {len(df)}")
                except Exception as e:
                    logger.warning(f"日期过滤出错: {str(e)}，返回原始数据")
                    
            elif market_type in ['ETF', 'LOF']:
                logger.debug(f"获取{market_type}基金数据: {stock_code}")
                df = ak.fund_etf_hist_sina(
                    symbol=stock_code,
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', '')
                )
                
            else:
                error_msg = f"不支持的市场类型: {market_type}"
                logger.error(f"[市场类型错误] {error_msg}")
                raise ValueError(error_msg)
                
            # 标准化列名
            if market_type == 'A':
                # 根据实际数据结构调整列名映射
                # 实际数据列：['日期', '股票代码', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
                df.columns = ['Date', 'Code', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Amplitude', 'Change_pct', 'Change', 'Turnover']
            elif market_type in ['HK', 'US']:
                # 美股数据列可能不同，需要通过映射处理
                columns_mapping = {
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume',
                    'amount': 'Amount'
                }
                
                # 创建新的DataFrame以确保列顺序和存在性
                new_df = pd.DataFrame(index=df.index)
                
                # 遍历映射，填充新DataFrame
                for orig_col, new_col in columns_mapping.items():
                    if orig_col in df.columns:
                        new_df[new_col] = df[orig_col]
                    else:
                        # 如果原始列不存在，创建一个填充0的列
                        logger.warning(f"数据中缺少{orig_col}列，使用0值填充")
                        new_df[new_col] = 0.0
                
                # 替换原始df
                df = new_df
                
            elif market_type in ['ETF', 'LOF']:
                # 基金数据可能有不同的列
                df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Amount']
                
            # 确保日期列是日期类型
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                
            # 确保按日期升序排序
            df.sort_index(inplace=True)
                
            logger.info(f"成功获取{market_type}数据 {stock_code}, 数据点数: {len(df)}")
            return df
            
        except Exception as e:
            error_msg = f"获取{market_type}数据失败 {stock_code}: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            # 使用空的DataFrame并添加错误信息，而不是抛出异常
            # 这样上层调用者可以检查是否有错误并适当处理
            df = pd.DataFrame()
            df.error = error_msg  # 添加错误属性
            return df
            
    async def get_multiple_stocks_data(self, stock_codes: List[str], 
                                     market_type: str = 'A',
                                     start_date: Optional[str] = None, 
                                     end_date: Optional[str] = None,
                                     max_concurrency: int = 5) -> Dict[str, pd.DataFrame]:
        """
        异步批量获取多只股票数据
        
        Args:
            stock_codes: 股票代码列表
            market_type: 市场类型，默认为'A'股
            start_date: 开始日期，格式YYYYMMDD
            end_date: 结束日期，格式YYYYMMDD
            max_concurrency: 最大并发数，默认为5
            
        Returns:
            字典，键为股票代码，值为对应的DataFrame
        """
        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def get_with_semaphore(code):
            async with semaphore:
                try:
                    return code, await self.get_stock_data(code, market_type, start_date, end_date)
                except Exception as e:
                    logger.error(f"获取股票 {code} 数据时出错: {str(e)}")
                    return code, None
        
        # 创建异步任务
        tasks = [get_with_semaphore(code) for code in stock_codes]
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks)
        
        # 构建结果字典，过滤掉失败的请求
        return {code: df for code, df in results if df is not None}