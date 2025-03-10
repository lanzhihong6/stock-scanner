<template>
  <n-card class="stock-card" :bordered="false" :class="{ 'is-analyzing': isAnalyzing }">
    <div class="card-header">
      <div class="header-main">
        <div class="header-left">
          <div class="stock-info">
            <div class="stock-code">{{ stock.code }}</div>
            <div class="stock-name" v-if="stock.name">{{ stock.name }}</div>
          </div>
          <div class="stock-price-info" v-if="stock.price !== undefined">
            <div class="stock-price">
              <span class="label">当前价格:</span>
              <span class="value">{{ stock.price.toFixed(2) }}</span>
            </div>
            <div class="stock-change" :class="{ 
              'up': calculatedChangePercent && calculatedChangePercent > 0,
              'down': calculatedChangePercent && calculatedChangePercent < 0
            }">
              <span class="label">涨跌幅:</span>
              <span class="value">{{ formatChangePercent(calculatedChangePercent) }}</span>
            </div>
          </div>
        </div>
        <div class="header-right">
          <n-button 
            size="small" 
            v-if="stock.analysisStatus === 'completed'"
            @click="copyStockAnalysis"
            class="copy-button"
            type="primary"
            secondary
            round
          >
            <template #icon>
              <n-icon><CopyOutline /></n-icon>
            </template>
            复制结果
          </n-button>
        </div>
      </div>
      <div class="analysis-status" v-if="stock.analysisStatus !== 'completed'">
        <n-tag 
          :type="getStatusType" 
          size="small" 
          round
          :bordered="false"
        >
          <template #icon>
            <n-icon>
              <component :is="getStatusIcon" />
            </n-icon>
          </template>
          {{ getStatusText }}
        </n-tag>
      </div>
    </div>
    
    <div class="stock-summary" v-if="stock.score !== undefined || stock.recommendation">
      <div class="summary-item score-item" v-if="stock.score !== undefined">
        <div class="summary-value" :class="getScoreClass(stock.score)">{{ stock.score }}</div>
        <div class="summary-label">评分</div>
      </div>
      <div class="summary-item recommendation-item" v-if="stock.recommendation">
        <div class="summary-value recommendation">{{ stock.recommendation }}</div>
        <div class="summary-label">推荐</div>
      </div>
    </div>
    
    <div class="analysis-date" v-if="stock.analysis_date">
      <n-tag type="info" size="small">
        <template #icon>
          <n-icon><CalendarOutline /></n-icon>
        </template>
        分析日期: {{ formatDate(stock.analysis_date) }}
      </n-tag>
    </div>
    
    <div class="technical-indicators" v-if="hasAnyTechnicalIndicator">
      <n-divider dashed style="margin: 12px 0 8px 0">技术指标</n-divider>
      
      <div class="indicators-grid">
        <div class="indicator-item" v-if="stock.rsi !== undefined">
          <div class="indicator-value" :class="getRsiClass(stock.rsi)">{{ stock.rsi.toFixed(2) }}</div>
          <div class="indicator-label">RSI</div>
        </div>
        
        <div class="indicator-item" v-if="stock.price_change !== undefined">
          <div class="indicator-value" :class="{ 
            'up': stock.price_change > 0,
            'down': stock.price_change < 0
          }">{{ formatPriceChange(stock.price_change) }}</div>
          <div class="indicator-label">涨跌额</div>
        </div>
        
        <div class="indicator-item" v-if="stock.ma_trend">
          <div class="indicator-value" :class="getTrendClass(stock.ma_trend)">
            {{ getChineseTrend(stock.ma_trend) }}
          </div>
          <div class="indicator-label">均线趋势</div>
        </div>
        
        <div class="indicator-item" v-if="stock.macd_signal">
          <div class="indicator-value" :class="getSignalClass(stock.macd_signal)">
            {{ getChineseSignal(stock.macd_signal) }}
          </div>
          <div class="indicator-label">MACD信号</div>
        </div>
        
        <div class="indicator-item" v-if="stock.volume_status">
          <div class="indicator-value" :class="getVolumeStatusClass(stock.volume_status)">
            {{ getChineseVolumeStatus(stock.volume_status) }}
          </div>
          <div class="indicator-label">成交量</div>
        </div>
      </div>
    </div>
    
    <n-divider />
    
    <div class="card-content">
      <template v-if="stock.analysisStatus === 'error'">
        <div class="error-status">
          <n-icon :component="AlertCircleIcon" class="error-icon" />
          <span>{{ stock.error || '未知错误' }}</span>
        </div>
      </template>
      
      <template v-else-if="stock.analysisStatus === 'analyzing'">
        <div class="analysis-result analysis-streaming" v-if="parsedAnalysis" v-html="parsedAnalysis" :key="analysisContentKey"></div>
      </template>
      
      <template v-else-if="stock.analysisStatus === 'completed'">
        <div class="analysis-result analysis-completed" v-html="parsedAnalysis"></div>
      </template>
    </div>
    
  </n-card>
</template>

<script setup lang="ts">
import { computed, watch, ref } from 'vue';
import { NCard, NDivider, NIcon, NTag, NButton, useMessage } from 'naive-ui';
import { 
  AlertCircleOutline as AlertCircleIcon,
  CalendarOutline,
  CopyOutline,
  HourglassOutline,
  ReloadOutline
} from '@vicons/ionicons5';
import { parseMarkdown } from '@/utils';
import type { StockInfo } from '@/types';

const props = defineProps<{
  stock: StockInfo;
}>();

const isAnalyzing = computed(() => {
  return props.stock.analysisStatus === 'analyzing';
});

const lastAnalysisLength = ref(0);

// 监听分析内容变化
watch(() => props.stock.analysis, (newVal) => {
  if (newVal && props.stock.analysisStatus === 'analyzing') {
    lastAnalysisLength.value = newVal.length;
  }
}, { immediate: true });

// 添加一个计算属性，用于监控分析内容是否更新
const analysisContentKey = ref(0);
watch(() => props.stock.analysis, (newVal, oldVal) => {
  if (newVal && oldVal && newVal.length > oldVal.length && props.stock.analysisStatus === 'analyzing') {
    analysisContentKey.value++;
  }
}, { immediate: false });

const parsedAnalysis = computed(() => {
  if (props.stock.analysis) {
    let result = parseMarkdown(props.stock.analysis);
    
    // 为关键词添加样式类
    result = highlightKeywords(result);
    
    return result;
  }
  return '';
});

// 关键词高亮处理函数
function highlightKeywords(html: string): string {
  // 买入/卖出/持有信号
  html = html.replace(/(<strong>)(买入|卖出|持有)(<\/strong>)/g, '$1<span class="buy">$2</span>$3');
  
  // 上涨/增长相关词
  html = html.replace(/(<strong>)(上涨|看涨|增长|增加|上升)(<\/strong>)/g, '$1<span class="up">$2</span>$3');
  
  // 下跌/减少相关词
  html = html.replace(/(<strong>)(下跌|看跌|减少|降低|下降)(<\/strong>)/g, '$1<span class="down">$2</span>$3');
  
  // 技术指标相关词
  html = html.replace(/(<strong>)(RSI|MACD|MA|KDJ|均线|成交量|布林带|Bollinger|移动平均|相对强弱|背离)(<\/strong>)/g, 
                      '$1<span class="indicator">$2</span>$3');
  
  // 高亮重要的百分比数字 (如 +12.34%, -12.34%)
  html = html.replace(/([+-]?\d+\.?\d*\s*%)/g, '<span class="number">$1</span>');
  
  // 高亮重要的数值 (如带小数位的数字)
  html = html.replace(/(\s|>)(\d+\.\d+)(\s|<)/g, '$1<span class="number">$2</span>$3');
  
  return html;
}

// 获取涨跌幅
const calculatedChangePercent = computed(() => {
  if (props.stock.changePercent !== undefined) {
    return props.stock.changePercent;
  }
  return undefined;
});

const hasAnyTechnicalIndicator = computed(() => {
  return props.stock.rsi !== undefined || 
         props.stock.price_change !== undefined || 
         props.stock.ma_trend !== undefined || 
         props.stock.macd_signal !== undefined || 
         props.stock.volume_status !== undefined;
});

function formatChangePercent(percent: number | undefined): string {
  if (percent === undefined) return '--';
  
  const sign = percent > 0 ? '+' : '';
  return `${sign}${percent.toFixed(2)}%`;
}

function formatPriceChange(change: number | undefined | null): string {
  if (change === undefined || change === null) return '--';
  const sign = change > 0 ? '+' : '';
  return `${sign}${change.toFixed(2)}`;
}

function formatDate(dateStr: string | undefined | null): string {
  if (!dateStr) return '--';
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return dateStr;
    }
    return date.toISOString().split('T')[0];
  } catch (e) {
    return dateStr;
  }
}

function getScoreClass(score: number): string {
  if (score >= 80) return 'score-high';
  if (score >= 70) return 'score-medium-high';
  if (score >= 60) return 'score-medium';
  if (score >= 40) return 'score-medium-low';
  return 'score-low';
}

function getRsiClass(rsi: number): string {
  if (rsi >= 70) return 'rsi-overbought';
  if (rsi <= 30) return 'rsi-oversold';
  return '';
}

function getTrendClass(trend: string): string {
  if (trend === 'UP') return 'trend-up';
  if (trend === 'DOWN') return 'trend-down';
  return 'trend-neutral';
}

function getSignalClass(signal: string): string {
  if (signal === 'BUY') return 'signal-buy';
  if (signal === 'SELL') return 'signal-sell';
  return 'signal-neutral';
}

function getVolumeStatusClass(status: string): string {
  if (status === 'HIGH') return 'volume-high';
  if (status === 'LOW') return 'volume-low';
  return 'volume-normal';
}

function getChineseTrend(trend: string): string {
  const trendMap: Record<string, string> = {
    'UP': '上升',
    'DOWN': '下降',
    'NEUTRAL': '平稳'
  };
  
  return trendMap[trend] || trend;
}

function getChineseSignal(signal: string): string {
  const signalMap: Record<string, string> = {
    'BUY': '买入',
    'SELL': '卖出',
    'HOLD': '持有',
    'NEUTRAL': '中性'
  };
  
  return signalMap[signal] || signal;
}

function getChineseVolumeStatus(status: string): string {
  const statusMap: Record<string, string> = {
    'HIGH': '放量',
    'LOW': '缩量',
    'NORMAL': '正常'
  };
  
  return statusMap[status] || status;
}

const message = useMessage();

// 添加复制功能
async function copyStockAnalysis() {
  if (!props.stock.analysis) {
    message.warning('暂无分析结果可复制');
    return;
  }

  try {
    let result = `【${props.stock.code} ${props.stock.name || ''}】\n`;
    
    // 添加分析日期
    if (props.stock.analysis_date) {
      result += `分析日期: ${formatDate(props.stock.analysis_date)}\n`;
    }
    
    // 添加评分和推荐信息
    if (props.stock.score !== undefined) {
      result += `评分: ${props.stock.score}\n`;
    }
    
    if (props.stock.recommendation) {
      result += `推荐: ${props.stock.recommendation}\n`;
    }
    
    // 添加技术指标信息
    if (props.stock.rsi !== undefined) {
      result += `RSI: ${props.stock.rsi.toFixed(2)}\n`;
    }
    
    if (props.stock.price_change !== undefined) {
      const sign = props.stock.price_change > 0 ? '+' : '';
      result += `涨跌额: ${sign}${props.stock.price_change.toFixed(2)}\n`;
    }
    
    if (props.stock.ma_trend) {
      result += `均线趋势: ${getChineseTrend(props.stock.ma_trend)}\n`;
    }
    
    if (props.stock.macd_signal) {
      result += `MACD信号: ${getChineseSignal(props.stock.macd_signal)}\n`;
    }
    
    if (props.stock.volume_status) {
      result += `成交量: ${getChineseVolumeStatus(props.stock.volume_status)}\n`;
    }
    
    // 添加分析结果
    result += `\n${props.stock.analysis}\n`;
    
    await navigator.clipboard.writeText(result);
    message.success('已复制分析结果到剪贴板');
  } catch (error) {
    message.error('复制失败，请手动复制');
    console.error('复制分析结果时出错:', error);
  }
}

// 添加状态相关的计算属性
const getStatusType = computed(() => {
  switch (props.stock.analysisStatus) {
    case 'waiting':
      return 'default';
    case 'analyzing':
      return 'info';
    case 'error':
      return 'error';
    default:
      return 'default';
  }
});

const getStatusIcon = computed(() => {
  switch (props.stock.analysisStatus) {
    case 'waiting':
      return HourglassOutline;
    case 'analyzing':
      return ReloadOutline;
    case 'error':
      return AlertCircleIcon;
    default:
      return HourglassOutline;
  }
});

const getStatusText = computed(() => {
  switch (props.stock.analysisStatus) {
    case 'waiting':
      return '等待分析';
    case 'analyzing':
      return '正在分析';
    case 'error':
      return '分析出错';
    default:
      return '';
  }
});
</script>

<style scoped>
.stock-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.stock-card.is-analyzing {
  border-left: 3px solid var(--n-info-color);
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px 8px 8px;
  margin-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.09);
  position: relative;
  background: linear-gradient(to bottom, rgba(240, 240, 245, 0.3), transparent);
  border-radius: 8px 8px 0 0;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  gap: 16px;
  align-items: center;
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 100px;
}

.stock-code {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--n-text-color);
  line-height: 1.2;
  letter-spacing: -0.01em;
}

.stock-name {
  font-size: 0.875rem;
  color: var(--n-text-color-3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

.stock-price-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-left: 8px;
  border-left: 1px dashed rgba(0, 0, 0, 0.09);
}

.stock-price, .stock-change {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.stock-price .label,
.stock-change .label {
  font-size: 0.875rem;
  color: var(--n-text-color-3);
}

.stock-price .value {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--n-text-color);
}

.stock-change .value {
  font-size: 1rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.03);
}

.up .value {
  color: var(--n-error-color);
  background-color: rgba(208, 48, 80, 0.08);
}

.down .value {
  color: var(--n-success-color);
  background-color: rgba(24, 160, 88, 0.08);
}

.header-right {
  display: flex;
  align-items: center;
}

.copy-button {
  transition: all 0.3s ease;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.copy-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.copy-button:active {
  transform: translateY(0);
}

.analysis-status {
  display: flex;
  align-items: center;
  margin-top: 4px;
}

.analysis-status :deep(.n-tag) {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.analysis-status :deep(.n-tag .n-icon) {
  margin-right: 4px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.copy-button:active {
  transform: translateY(0);
}

.analysis-status {
  display: flex;
  align-items: center;
}

.analysis-status :deep(.n-tag) {
  display: flex;
  align-items: center;
  gap: 4px;
}

.analysis-status :deep(.n-tag .n-icon) {
  margin-right: 4px;
}

.up .value {
  color: var(--n-error-color);
}

.down .value {
  color: var(--n-success-color);
}

.stock-summary {
  display: flex;
  justify-content: space-around;
  margin: 0.75rem 0;
  padding: 0.5rem;
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 0.5rem;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 700;
}

.summary-label {
  font-size: 0.75rem;
  color: var(--n-text-color-3);
  margin-top: 0.25rem;
}

.analysis-date {
  margin: 0.5rem 0;
  display: flex;
  justify-content: flex-end;
}

.technical-indicators {
  margin-top: 0.5rem;
}

.indicators-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.indicator-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.indicator-value {
  font-size: 0.875rem;
  font-weight: 600;
}

.indicator-label {
  font-size: 0.75rem;
  color: var(--n-text-color-3);
  margin-top: 0.25rem;
}

.score-high {
  color: #18a058;
}

.score-medium-high {
  color: #63e2b7;
}

.score-medium {
  color: #f0a020;
}

.score-medium-low {
  color: #f5a623;
}

.score-low {
  color: #d03050;
}

.rsi-overbought {
  color: #d03050;
}

.rsi-oversold {
  color: #18a058;
}

.trend-up {
  color: #d03050;
}

.trend-down {
  color: #18a058;
}

.trend-neutral {
  color: #f0a020;
}

.signal-buy {
  color: #d03050;
}

.signal-sell {
  color: #18a058;
}

.signal-neutral {
  color: #f0a020;
}

.volume-high {
  color: #d03050;
}

.volume-low {
  color: #18a058;
}

.volume-normal {
  color: #f0a020;
}

.recommendation {
  color: #2080f0;
}

.up {
  color: var(--n-error-color);
}

.down {
  color: var(--n-success-color);
}

.card-content {
  flex: 1;
  min-height: 100px;
  margin-bottom: 0.5rem;
  text-align: left;
  display: flex;
  flex-direction: column;
}

.error-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--n-error-color);
  font-size: 0.875rem;
  margin: 0.75rem 1rem;
  padding: 0.5rem;
  background-color: rgba(208, 48, 80, 0.1);
  border-radius: 4px;
}

.error-icon {
  color: var(--n-error-color);
}

.analysis-result {
  font-size: 0.875rem;
  line-height: 1.6;
  text-align: left;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.01);
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.05);
  max-height: 400px;
  overflow-y: auto;
  word-break: break-word;
  hyphens: auto;
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  
  /* 自定义滚动条样式 */
  scrollbar-width: thin; /* Firefox */
  scrollbar-color: rgba(32, 128, 240, 0.3) transparent; /* Firefox */
}

/* Webkit浏览器的滚动条样式 */
.analysis-result::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.analysis-result::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.analysis-result::-webkit-scrollbar-thumb {
  background-color: rgba(32, 128, 240, 0.3);
  border-radius: 3px;
  transition: background-color 0.3s ease;
}

.analysis-result::-webkit-scrollbar-thumb:hover {
  background-color: rgba(32, 128, 240, 0.5);
}

/* 在不滚动时隐藏滚动条，滚动时显示 */
.analysis-result:not(:hover)::-webkit-scrollbar-thumb {
  background-color: rgba(32, 128, 240, 0.1);
}

.analysis-streaming {
  position: relative;
  border-left: 2px solid var(--n-info-color);
  animation: fadePulse 2s infinite;
}

/* 改进流式输出的动画效果，消除闪烁 */
.analysis-streaming > :deep(*) {
  animation: none;
}

/* 添加打字机光标效果 */
.analysis-streaming::after {
  content: '|';
  display: inline-block;
  color: var(--n-info-color);
  animation: blink 1s step-end infinite;
  margin-left: 2px;
  font-weight: bold;
  vertical-align: middle;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.analysis-completed {
  border-left: 2px solid var(--n-success-color);
}

@keyframes fadePulse {
  0% { border-left-color: var(--n-info-color); }
  50% { border-left-color: rgba(31, 126, 212, 0.4); }
  100% { border-left-color: var(--n-info-color); }
}

/* 优化标题样式，增加颜色显示 */
.analysis-result :deep(h1), .analysis-result :deep(h2), .analysis-result :deep(h3) {
  margin: 1.25rem 0 0.75rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding-bottom: 0.4rem;
  font-weight: 600;
}

.analysis-result :deep(h1) {
  font-size: 1.4rem;
  color: #2080f0;
}

.analysis-result :deep(h2) {
  font-size: 1.2rem;
  color: #2080f0;
}

.analysis-result :deep(h3) {
  font-size: 1.1rem;
  color: #2080f0;
}

/* 优化列表样式 */
.analysis-result :deep(ul), .analysis-result :deep(ol) {
  margin: 0.75rem 0;
  padding-left: 1.5rem;
}

.analysis-result :deep(ul) li, .analysis-result :deep(ol) li {
  margin-bottom: 0.3rem;
}

/* 优化段落样式 */
.analysis-result :deep(p) {
  margin: 0.75rem 0;
  text-align: left;
}

/* 优化代码样式 */
.analysis-result :deep(code) {
  background: rgba(0, 0, 0, 0.05);
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.85em;
}

.analysis-result :deep(pre) {
  background: rgba(0, 0, 0, 0.05);
  padding: 0.75rem;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0.75rem 0;
  border-left: 3px solid #2080f0;
  max-width: 100%;
  white-space: pre-wrap; /* 允许代码块自动换行 */
}

.analysis-result :deep(pre code) {
  background: transparent;
  padding: 0;
}

/* 优化引用样式 */
.analysis-result :deep(blockquote) {
  margin: 0.75rem 0;
  padding: 0.5rem 1rem;
  border-left: 3px solid #f0a020;
  background-color: rgba(240, 160, 32, 0.05);
  color: var(--n-text-color-2);
}

/* 优化表格样式 */
.analysis-result :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.75rem 0;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  table-layout: fixed; /* 固定表格布局 */
  max-width: 100%;
}

.analysis-result :deep(th), .analysis-result :deep(td) {
  padding: 0.6rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  word-break: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
}

.analysis-result :deep(th) {
  background-color: rgba(32, 128, 240, 0.1);
  color: #2080f0;
  font-weight: 600;
  text-align: left;
}

.analysis-result :deep(tr:nth-child(even)) {
  background-color: rgba(0, 0, 0, 0.02);
}

/* 优化文本强调和术语显示 */
.analysis-result :deep(strong) {
  font-weight: 600;
  color: #2080f0;
}

/* 特定指标和信号的样式 */
.analysis-result :deep(.buy), 
.analysis-result :deep(.sell), 
.analysis-result :deep(.hold) {
  color: #d03050;
  background-color: rgba(208, 48, 80, 0.1);
  padding: 0 0.3rem;
  border-radius: 2px;
  font-weight: 600;
}

.analysis-result :deep(.up), 
.analysis-result :deep(.increase) {
  color: #d03050;
  font-weight: 600;
}

.analysis-result :deep(.down), 
.analysis-result :deep(.decrease) {
  color: #18a058;
  font-weight: 600;
}

.analysis-result :deep(.indicator) {
  color: #2080f0;
  background-color: rgba(32, 128, 240, 0.1);
  padding: 0 0.3rem;
  border-radius: 2px;
  font-weight: 600;
}

.analysis-result :deep(.number) {
  font-family: 'Consolas', monospace;
  font-weight: 600;
  color: #f0a020;
}

/* 优化链接样式 */
.analysis-result :deep(a) {
  color: #2080f0;
  text-decoration: none;
  border-bottom: 1px dotted #2080f0;
  transition: all 0.2s ease;
  font-weight: 500;
}

.analysis-result :deep(a:hover) {
  color: #36ad6a;
  border-bottom: 1px solid #36ad6a;
}

/* 优化图片样式 */
.analysis-result :deep(img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0.75rem auto;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
