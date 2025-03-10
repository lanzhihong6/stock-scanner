// API接口相关类型
export interface ApiConfig {
  apiUrl: string;
  apiKey: string;
  apiModel: string;
  apiTimeout: string;
  saveApiConfig: boolean;
}

// 登录相关类型
export interface LoginRequest {
  password: string;
}

export interface LoginResponse {
  access_token?: string;
  token_type?: string;
  success?: boolean;
  message?: string;
}

export interface StockInfo {
  code: string;
  name: string;
  marketType: string;
  price?: number;
  changePercent?: number;
  marketValue?: number;
  analysis?: string;
  analysisStatus: 'waiting' | 'analyzing' | 'completed' | 'error';
  error?: string;
  score?: number;
  recommendation?: string;
  price_change?: number;
  rsi?: number;
  ma_trend?: string;
  macd_signal?: string;
  volume_status?: string;
  analysis_date?: string;
}

export interface SearchResult {
  symbol: string;
  name: string;
  market: string;
  marketValue?: number;
}

export interface MarketStatus {
  isOpen: boolean;
  nextTime: string;
}

export interface MarketTimeInfo {
  currentTime: string;
  cnMarket: MarketStatus;
  hkMarket: MarketStatus;
  usMarket: MarketStatus;
}

// 分析请求和响应
export interface AnalyzeRequest {
  stock_codes: string[];
  market_type: string;
  api_url?: string;
  api_key?: string;
  api_model?: string;
  api_timeout?: number;
}

export interface TestApiRequest {
  api_url: string;
  api_key: string;
  api_model?: string;
  api_timeout: number;
}

export interface TestApiResponse {
  success: boolean;
  message: string;
  status_code?: number;
}

// 流式响应类型
export interface StreamInitMessage {
  stream_type: 'single' | 'batch';
  stock_code?: string;
  stock_codes?: string[];
}

export interface StreamAnalysisUpdate {
  stock_code: string;
  analysis?: string;
  status: 'analyzing' | 'completed' | 'error';
  error?: string;
  name?: string;
  price?: number;
  change_percent?: number;
  price_change_value?: number;
  market_value?: number;
  score?: number;
  recommendation?: string;
  price_change?: number;
  rsi?: number;
  ma_trend?: string;
  macd_signal?: string;
  volume_status?: string;
  analysis_date?: string;
  ai_analysis_chunk?: string;
}
