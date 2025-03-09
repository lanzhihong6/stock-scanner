import axios from 'axios';
import type { AnalyzeRequest, TestApiRequest, TestApiResponse, SearchResult, LoginRequest, LoginResponse } from '@/types';

// API前缀
const API_PREFIX = '/api';

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: API_PREFIX
});

// 请求拦截器，添加token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器，处理401错误
axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // 清除token
      localStorage.removeItem('token');
      // 不要在这里跳转，避免循环重定向
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // 用户登录
  login: async (request: LoginRequest): Promise<LoginResponse> => {
    try {
      const response = await axiosInstance.post('/login', request);
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
      }
      return response.data;
    } catch (error: any) {
      if (error.response) {
        return {
          success: false,
          message: error.response.data.detail || '登录失败',
        };
      }
      return {
        success: false,
        message: error.message || '登录失败'
      };
    }
  },

  // 检查认证状态
  checkAuth: async (): Promise<boolean> => {
    try {
      const response = await axiosInstance.get('/check_auth');
      return response.data.authenticated === true;
    } catch (error) {
      // 认证失败，清除token
      localStorage.removeItem('token');
      return false;
    }
  },

  // 登出
  logout: () => {
    localStorage.removeItem('token');
    // 简化登出逻辑
    window.location.href = '/login';
  },

  // 分析股票
  analyzeStocks: async (request: AnalyzeRequest) => {
    return axiosInstance.post('/analyze', request, {
      responseType: 'stream'
    });
  },

  // 测试API连接
  testApiConnection: async (request: TestApiRequest): Promise<TestApiResponse> => {
    try {
      const response = await axiosInstance.post('/test_api_connection', request);
      return response.data;
    } catch (error: any) {
      if (error.response) {
        return error.response.data;
      }
      return {
        success: false,
        message: error.message || '连接失败'
      };
    }
  },

  // 搜索美股
  searchUsStocks: async (keyword: string): Promise<SearchResult[]> => {
    try {
      const response = await axiosInstance.get('/search_us_stocks', {
        params: { keyword }
      });
      return response.data.results || [];
    } catch (error) {
      console.error('搜索美股时出错:', error);
      return [];
    }
  },
  
  // 获取配置
  getConfig: async () => {
    try {
      const response = await axiosInstance.get('/config');
      return response.data;
    } catch (error) {
      console.error('获取配置时出错:', error);
      return {
        announcement: '',
        default_api_url: '',
        default_api_model: '',
        default_api_timeout: '60'
      };
    }
  },

  // 检查是否需要登录
  checkNeedLogin: async (): Promise<boolean> => {
    try {
      const response = await axiosInstance.get('/need_login');
      return response.data.require_login;
    } catch (error) {
      console.error('检查是否需要登录时出错:', error);
      // 默认为需要登录，确保安全
      return true;
    }
  }
};
