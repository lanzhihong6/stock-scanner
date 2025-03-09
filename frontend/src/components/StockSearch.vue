<template>
  <div class="stock-search-container">
    <n-input
      v-model:value="searchKeyword"
      placeholder="输入股票代码或名称搜索"
      @input="handleSearchInput"
      @blur="handleBlur"
      @focus="handleFocus"
      ref="searchInputRef"
    >
      <template #prefix>
        <n-icon :component="SearchIcon" />
      </template>
    </n-input>
    
    <div class="search-results" v-show="showResults">
      <div v-if="loading" class="loading-results">
        <n-spin size="small" />
        <span>搜索中...</span>
      </div>
      
      <div v-else-if="results.length === 0 && searchKeyword" class="no-results">
        未找到相关股票
      </div>
      
      <template v-else>
        <n-scrollbar style="max-height: 300px;">
          <div
            v-for="item in results"
            :key="item.symbol"
            class="search-result-item"
            @click="selectStock(item)"
          >
            <div class="result-symbol-name">
              <span class="result-symbol">{{ item.symbol }}</span>
              <span class="result-name">{{ item.name }}</span>
            </div>
            <div class="result-meta">
              <span class="result-market">{{ item.market }}</span>
              <span v-if="item.marketValue" class="result-market-value">
                市值: {{ formatMarketValue(item.marketValue) }}
              </span>
            </div>
          </div>
        </n-scrollbar>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { NInput, NIcon, NSpin, NScrollbar } from 'naive-ui';
import { Search as SearchIcon } from '@vicons/ionicons5';
import { apiService } from '@/services/api';
import { debounce, formatMarketValue as formatMarketValueFn } from '@/utils';
import type { SearchResult } from '@/types';

const props = defineProps<{
  marketType: string;
}>();

const emit = defineEmits<{
  (e: 'select', symbol: string): void;
}>();

const searchKeyword = ref('');
const results = ref<SearchResult[]>([]);
const loading = ref(false);
const showResults = ref(false);
const searchInputRef = ref<any>(null);

// 创建防抖搜索函数
const debouncedSearch = debounce(async (keyword: string) => {
  if (!keyword) {
    results.value = [];
    loading.value = false;
    return;
  }

  loading.value = true;
  
  try {
    if (props.marketType === 'US') {
      // 美股搜索
      const searchResults = await apiService.searchUsStocks(keyword);
      // 限制只显示前10个结果
      results.value = searchResults.slice(0, 10);
    } else {
      // 其他市场搜索 (后端需要实现对应的接口)
      results.value = [];
    }
  } catch (error) {
    console.error('搜索股票时出错:', error);
    results.value = [];
  } finally {
    loading.value = false;
  }
}, 300);

function handleSearchInput() {
  showResults.value = true;
  debouncedSearch(searchKeyword.value);
}

function selectStock(item: SearchResult) {
  emit('select', item.symbol);
  searchKeyword.value = '';
  showResults.value = false;
}

function handleBlur() {
  // 延迟隐藏，以便可以点击结果项
  setTimeout(() => {
    showResults.value = false;
  }, 200);
}

function handleFocus() {
  if (searchKeyword.value) {
    showResults.value = true;
  }
}

function formatMarketValue(value: number): string {
  return formatMarketValueFn(value);
}

// 点击外部时隐藏搜索结果
function handleClickOutside(event: MouseEvent) {
  if (
    searchInputRef.value &&
    !searchInputRef.value.$el.contains(event.target as Node)
  ) {
    showResults.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.stock-search-container {
  position: relative;
  width: 100%;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 10;
  margin-top: 0.25rem;
  background-color: var(--n-color);
  border-radius: 0.375rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--n-border-color);
}

.loading-results,
.no-results {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  color: var(--n-text-color-3);
  font-size: 0.875rem;
}

.search-result-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-result-item:hover {
  background-color: var(--n-color-hover);
}

.result-symbol-name {
  display: flex;
  flex-direction: column;
}

.result-symbol {
  font-weight: 500;
  color: var(--n-text-color);
}

.result-name {
  font-size: 0.75rem;
  color: var(--n-text-color-3);
  margin-top: 0.25rem;
}

.result-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.result-market,
.result-market-value {
  font-size: 0.75rem;
  color: var(--n-text-color-3);
}

.result-market-value {
  margin-top: 0.25rem;
}
</style>
