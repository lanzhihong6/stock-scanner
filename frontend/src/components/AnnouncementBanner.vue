<template>
  <div v-if="showAnnouncement" class="announcement-container">
    <n-card class="announcement-card">
      <template #header>
        <div class="announcement-header">
          <n-icon size="18" :component="InformationCircleIcon" class="info-icon" />
          <span>系统公告</span>
        </div>
      </template>
      <div class="announcement-content" v-html="processedContent"></div>
      <div class="announcement-timer">{{ remainingTimeText }}</div>
      <template #action>
        <n-button quaternary circle size="small" @click="closeAnnouncement">
          <template #icon>
            <n-icon :component="CloseIcon" />
          </template>
        </n-button>
      </template>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { NCard, NIcon, NButton } from 'naive-ui';
import { InformationCircleOutline as InformationCircleIcon } from '@vicons/ionicons5';
import { Close as CloseIcon } from '@vicons/ionicons5';

const props = defineProps<{
  content: string;
  autoCloseTime?: number;
}>();

const showAnnouncement = ref(true);
const remainingTime = ref(props.autoCloseTime || 5);
const timer = ref<number | null>(null);

const remainingTimeText = computed(() => {
  return `${remainingTime.value}秒后自动关闭`;
});

const processedContent = computed(() => {
  // 处理文本中的URL
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  return props.content.replace(
    urlRegex, 
    '<a href="$1" target="_blank" class="announcement-link">$1</a>'
  );
});

function closeAnnouncement() {
  showAnnouncement.value = false;
  if (timer.value !== null) {
    window.clearInterval(timer.value);
    timer.value = null;
  }
}

function updateTimer() {
  if (remainingTime.value <= 1) {
    closeAnnouncement();
  } else {
    remainingTime.value--;
  }
}

onMounted(() => {
  timer.value = window.setInterval(updateTimer, 1000);
});

onBeforeUnmount(() => {
  if (timer.value !== null) {
    window.clearInterval(timer.value);
  }
});
</script>

<style scoped>
.announcement-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  max-width: 24rem;
  z-index: 50;
  animation: fadeInDown 0.3s ease-out;
}

.announcement-card {
  border-left: 4px solid var(--n-primary-color);
}

.announcement-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.info-icon {
  color: var(--n-primary-color);
}

.announcement-content {
  margin-bottom: 0.5rem;
  white-space: pre-line;
}

.announcement-timer {
  font-size: 0.75rem;
  color: var(--n-text-color-disabled);
}

.announcement-link {
  color: var(--n-primary-color);
  text-decoration: underline;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
