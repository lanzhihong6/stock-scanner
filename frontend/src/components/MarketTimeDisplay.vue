<template>
  <n-card class="market-time-card">
    <n-grid :x-gap="16" :y-gap="16" :cols="gridCols">
      <!-- 当前时间 -->
      <n-grid-item>
        <div class="time-block">
          <p class="time-label">当前时间</p>
          <p class="current-time">{{ marketInfo.currentTime }}</p>
        </div>
      </n-grid-item>
      
      <!-- A股状态 -->
      <n-grid-item>
        <div class="time-block">
          <p class="time-label">A股市场</p>
          <div class="market-status" :class="marketInfo.cnMarket.isOpen ? 'status-open' : 'status-closed'">
            <n-tag v-if="marketInfo.cnMarket.isOpen" type="success" size="medium" round>
              <template #icon><n-icon size="18"><pulse-icon /></n-icon></template>
              交易中
            </n-tag>
            <n-tag v-else type="default" size="medium" round>
              <template #icon><n-icon size="18"><time-icon /></n-icon></template>
              已休市
            </n-tag>
          </div>
          <p class="time-counter">{{ marketInfo.cnMarket.nextTime }}</p>
        </div>
      </n-grid-item>

      <!-- 港股状态 -->
      <n-grid-item>
        <div class="time-block">
          <p class="time-label">港股市场</p>
          <div class="market-status" :class="marketInfo.hkMarket.isOpen ? 'status-open' : 'status-closed'">
            <n-tag v-if="marketInfo.hkMarket.isOpen" type="success" size="medium" round>
              <template #icon><n-icon size="18"><pulse-icon /></n-icon></template>
              交易中
            </n-tag>
            <n-tag v-else type="default" size="medium" round>
              <template #icon><n-icon size="18"><time-icon /></n-icon></template>
              已休市
            </n-tag>
          </div>
          <p class="time-counter">{{ marketInfo.hkMarket.nextTime }}</p>
        </div>
      </n-grid-item>
      
      <!-- 美股状态 -->
      <n-grid-item>
        <div class="time-block">
          <p class="time-label">美股市场</p>
          <div class="market-status" :class="marketInfo.usMarket.isOpen ? 'status-open' : 'status-closed'">
            <n-tag v-if="marketInfo.usMarket.isOpen" type="success" size="medium" round>
              <template #icon><n-icon size="18"><pulse-icon /></n-icon></template>
              交易中
            </n-tag>
            <n-tag v-else type="default" size="medium" round>
              <template #icon><n-icon size="18"><time-icon /></n-icon></template>
              已休市
            </n-tag>
          </div>
          <p class="time-counter">{{ marketInfo.usMarket.nextTime }}</p>
        </div>
      </n-grid-item>
    </n-grid>
  </n-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { NCard, NGrid, NGridItem, NTag, NIcon } from 'naive-ui';
import { 
  PulseOutline as PulseIcon,
  TimeOutline as TimeIcon
} from '@vicons/ionicons5';
import { updateMarketTimeInfo } from '@/utils';
import type { MarketTimeInfo } from '@/types';

const props = defineProps({
  isMobile: {
    type: Boolean,
    default: false
  }
});

const marketInfo = ref<MarketTimeInfo>({
  currentTime: '',
  cnMarket: { isOpen: false, nextTime: '' },
  hkMarket: { isOpen: false, nextTime: '' },
  usMarket: { isOpen: false, nextTime: '' }
});

const gridCols = computed(() => {
  return props.isMobile ? 1 : 4;
});

let intervalId: number | null = null;

function updateMarketTime() {
  marketInfo.value = updateMarketTimeInfo();
}

onMounted(() => {
  updateMarketTime(); // 立即更新一次
  intervalId = window.setInterval(updateMarketTime, 1000);
});

onBeforeUnmount(() => {
  if (intervalId !== null) {
    window.clearInterval(intervalId);
    intervalId = null;
  }
});
</script>

<style scoped>
.market-time-card {
  margin-bottom: 1.5rem;
  padding: 0.5rem;
}

.time-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0.5rem;
}

.time-label {
  font-size: 1rem;
  color: var(--n-text-color-3);
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.current-time {
  font-size: 1.75rem;
  font-weight: bold;
  color: var(--n-text-color);
}

.market-status {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 32px;
}

.market-status :deep(.n-tag) {
  padding: 0 12px;
  height: 32px;
  font-size: 1rem;
}

.market-status :deep(.n-tag__icon) {
  margin-right: 6px;
}

.status-open :deep(.n-tag) {
  background-color: rgba(var(--success-color), 0.15);
  border: 1px solid var(--n-success-color);
  animation: pulse 2s infinite;
}

.status-closed :deep(.n-tag) {
  background-color: rgba(var(--n-text-color-3), 0.1);
}

.time-counter {
  font-size: 0.875rem;
  color: var(--n-text-color-3);
  margin-top: 0.5rem;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(var(--success-color), 0.4);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(var(--success-color), 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(var(--success-color), 0);
  }
}
</style>
