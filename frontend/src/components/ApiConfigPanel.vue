<template>
  <div class="api-config-section">
    <n-button
      class="toggle-button"
      size="small"
      @click="toggleConfig"
      :quaternary="true"
      :type="expanded ? 'primary' : 'default'"
    >
      <template #icon>
        <n-icon :component="expanded ? ChevronUpIcon : ChevronDownIcon" />
      </template>
      <span class="toggle-text">API配置 {{ expanded ? '收起' : '展开' }}</span>
    </n-button>
    
    <n-collapse-transition :show="expanded">
      <n-card class="api-config-card" :bordered="false">
        <n-alert title="OpenAI API配置" type="info" v-if="isApiInfoVisible" class="api-info-alert">
          <template #icon>
            <n-icon :component="InformationCircleIcon" />
          </template>
          <p>您可以配置自己的API，也可以使用系统默认配置。API密钥仅在您的浏览器中使用，不会发送到服务器存储。</p>
          <div class="alert-actions">
            <n-button text @click="isApiInfoVisible = false">
              <template #icon>
                <n-icon :component="CloseIcon" />
              </template>
            </n-button>
          </div>
        </n-alert>

        <n-grid :cols="24" :x-gap="16" :y-gap="16">
          <n-grid-item :span="24" :lg-span="14">
            <n-form-item label="API URL" path="apiUrl">
              <n-input 
                v-model:value="apiConfig.apiUrl" 
                placeholder="https://api.openai.com/v1/chat/completions"
                @update:value="handleConfigChange"
                round
              >
                <template #prefix>
                  <n-icon :component="GlobeIcon" />
                </template>
              </n-input>
              <template #feedback>
                <div class="url-feedback">
                  <span class="formatted-url">实际请求地址: {{ formattedUrl }}</span>
                  <div class="url-tips">
                    <div>提示: URL以/结尾将忽略v1路径</div>
                    <div>URL以#结尾将使用原始地址</div>
                  </div>
                </div>
              </template>
            </n-form-item>
          </n-grid-item>

          <n-grid-item :span="24" :lg-span="10">
            <n-form-item label="API Key" path="apiKey">
              <n-input 
                v-model:value="apiConfig.apiKey" 
                type="password" 
                placeholder="sk-..."
                show-password-on="click"
                @update:value="handleConfigChange"
                round
              >
                <template #prefix>
                  <n-icon :component="KeyIcon" />
                </template>
              </n-input>
            </n-form-item>
          </n-grid-item>

          <n-grid-item :span="12" :lg-span="12">
            <n-form-item label="模型" path="apiModel">
              <n-input
                v-model:value="apiConfig.apiModel"
                placeholder="输入或选择模型名称"
                @update:value="handleConfigChange"
                round
              >
                <template #prefix>
                  <n-icon :component="CodeIcon" />
                </template>
                <template #suffix>
                  <n-dropdown
                    trigger="click"
                    :options="modelOptions"
                    @select="selectModel"
                    placement="bottom-end"
                  >
                    <n-button quaternary circle size="small" class="model-dropdown-btn">
                      <template #icon>
                        <n-icon :component="ChevronDownIcon" />
                      </template>
                    </n-button>
                  </n-dropdown>
                </template>
              </n-input>
              <template #feedback>
                <div class="model-suggestions">
                  <div class="model-tip">您可以直接输入模型名称，或点击右侧按钮从下拉菜单选择</div>
                  <span>常用模型:</span>
                  <div class="model-chips">
                    <n-tag 
                      v-for="model in commonModels" 
                      :key="model.key"
                      size="small"
                      round
                      clickable
                      @click="selectModel(model.key)"
                    >
                      {{ model.label }}
                    </n-tag>
                  </div>
                </div>
              </template>
            </n-form-item>
          </n-grid-item>

          <n-grid-item :span="12" :lg-span="12">
            <n-form-item label="超时时间(秒)" path="apiTimeout">
              <n-input-number 
                v-model:value="apiTimeout" 
                placeholder="60"
                :min="1"
                :max="300"
                @update:value="handleTimeoutChange"
                :show-button="false"
                class="timeout-input"
              >
                <template #suffix>
                  <div class="timeout-controls">
                    <n-button size="tiny" quaternary @click="decreaseTimeout">
                      <template #icon><n-icon :component="RemoveIcon" /></template>
                    </n-button>
                    <n-button size="tiny" quaternary @click="increaseTimeout">
                      <template #icon><n-icon :component="AddIcon" /></template>
                    </n-button>
                  </div>
                </template>
              </n-input-number>
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <div class="api-actions">
          <div class="api-save-option">
            <n-button 
              tertiary
              size="small"
              @click="saveConfig"
              round
            >
              <template #icon>
                <n-icon :component="SaveIcon" />
              </template>
              保存配置到本地
            </n-button>
          </div>
          
          <div class="api-buttons">
            <n-button 
              type="primary" 
              :loading="testingConnection" 
              :disabled="!isConfigValid"
              @click="testConnection"
              round
            >
              <template #icon>
                <n-icon :component="CheckmarkIcon" />
              </template>
              测试连接
            </n-button>

            <n-button @click="resetConfig" round>
              <template #icon>
                <n-icon :component="RefreshIcon" />
              </template>
              重置
            </n-button>
          </div>
        </div>
        
        <n-divider v-if="connectionStatus" style="margin: 16px 0 12px" />
        
        <div v-if="connectionStatus" class="connection-status" :class="connectionStatus.type">
          <n-icon :component="connectionStatus.icon" class="status-icon" />
          <span class="status-message">{{ connectionStatus.message }}</span>
        </div>
      </n-card>
    </n-collapse-transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, markRaw } from 'vue';
import { 
  NButton, 
  NIcon, 
  NCard, 
  NCollapseTransition, 
  NGrid, 
  NGridItem, 
  NFormItem, 
  NInput,
  NInputNumber,
  NAlert,
  NDivider,
  NDropdown,
  NTag,
  useMessage
} from 'naive-ui';
import { 
  ChevronDown as ChevronDownIcon, 
  ChevronUp as ChevronUpIcon,
  InformationCircleOutline as InformationCircleIcon,
  Close as CloseIcon,
  Globe as GlobeIcon,
  Key as KeyIcon,
  CheckmarkCircleOutline as CheckmarkIcon,
  RefreshOutline as RefreshIcon,
  AddOutline as AddIcon,
  RemoveOutline as RemoveIcon,
  CheckmarkCircle as SuccessIcon,
  CloseCircle as ErrorIcon,
  CodeSlashOutline as CodeIcon,
  SaveOutline as SaveIcon
} from '@vicons/ionicons5';
import { apiService } from '@/services/api';
import { saveApiConfigToLocalStorage, loadApiConfig } from '@/utils';
import type { ApiConfig } from '@/types';

// 出于安全考虑，API KEY不会显示在前端
const props = defineProps<{
  defaultApiUrl?: string;
  defaultApiModel?: string;
  defaultApiTimeout?: string;
}>();

const emit = defineEmits<{
  (e: 'update:apiConfig', value: ApiConfig): void;
}>();

const message = useMessage();
const expanded = ref(false);
const testingConnection = ref(false);
const isApiInfoVisible = ref(true);

// 连接状态
const connectionStatus = ref<{
  type: 'success' | 'error';
  message: string;
  icon: any;
} | null>(null);

// 模型选项
const modelOptions = [
  { label: 'GPT-3.5', key: 'gpt-3.5-turbo' },
  { label: 'GPT-4o', key: 'gpt-4o' },
  { label: 'DeepSeek V3', key: 'deepseek-chat' },
  { label: 'DeepSeek R1', key: 'deepseek-reasoner' },
  { label: 'Claude 3.5 Sonnet', key: 'claude-3-5-sonnet' },
  { label: 'Claude 3.5 Sonnet 20241022', key: 'claude-3-5-sonnet-20241022' },
  { label: 'Gemini 1.5 Pro', key: 'gemini-1.5-pro' },
  { label: 'Gemini 1.5 Flash', key: 'gemini-1.5-flash' },
  { label: 'Gemini 2.0 Pro', key: 'gemini-2.0-pro' },
  { label: 'Gemini 2.0 Flash', key: 'gemini-2.0-flash' }
];

// 常用模型（用于快速选择）
const commonModels = [
  { label: 'GPT-3.5', key: 'gpt-3.5-turbo' },
  { label: 'GPT-4o', key: 'gpt-4o' },
  { label: 'Claude 3.5', key: 'claude-3-5-sonnet' },
  { label: 'Gemini 2.0', key: 'gemini-2.0-flash' },
  { label: 'DeepSeek V3', key: 'deepseek-chat' },
];

// API配置
const apiConfig = ref<ApiConfig>({
  apiUrl: props.defaultApiUrl || '',
  apiKey: '',
  apiModel: props.defaultApiModel || '',
  apiTimeout: props.defaultApiTimeout || '60',
  saveApiConfig: true // 默认启用保存配置
});

const apiTimeout = computed({
  get: () => parseInt(apiConfig.value.apiTimeout) || 60,
  set: (val: number) => {
    apiConfig.value.apiTimeout = val.toString();
  }
});

const isConfigValid = computed(() => {
  return apiConfig.value.apiUrl && apiConfig.value.apiKey;
});

const formattedUrl = computed(() => {
  return formatApiUrl(apiConfig.value.apiUrl);
});

function toggleConfig() {
  expanded.value = !expanded.value;
}

function handleConfigChange() {
  console.log('API配置变更:', apiConfig.value);
  
  // 不再在每次配置变更时自动保存
  // 仅向父组件发送更新事件
  emit('update:apiConfig', { ...apiConfig.value });
}

function handleTimeoutChange(value: number | null) {
  if (value !== null) {
    apiConfig.value.apiTimeout = value.toString();
    
    // 仅通知父组件更新，不自动保存
    emit('update:apiConfig', { ...apiConfig.value });
  }
}

function increaseTimeout() {
  if (apiTimeout.value < 300) {
    apiTimeout.value += 10;
    
    // 通知父组件
    emit('update:apiConfig', { ...apiConfig.value });
  }
}

function decreaseTimeout() {
  if (apiTimeout.value > 10) {
    apiTimeout.value -= 10;
    
    // 通知父组件
    emit('update:apiConfig', { ...apiConfig.value });
  }
}

function formatApiUrl(url: string): string {
  if (!url) return '';
  
  try {
    // 使用与后端一致的URL格式化逻辑
    if (url.endsWith('/')) {
      return `${url}chat/completions`;
    } else if (url.endsWith('#')) {
      return url.replace('#', '');
    } else {
      return `${url}/v1/chat/completions`;
    }
  } catch (e) {
    // 如果URL格式错误，则返回原始字符串
    return url;
  }
}

async function testConnection() {
  if (!isConfigValid.value) {
    message.error('请填写完整的API配置信息');
    return;
  }
  
  testingConnection.value = true;
  connectionStatus.value = null;
  
  try {
    const response = await apiService.testApiConnection({
      api_url: apiConfig.value.apiUrl,
      api_key: apiConfig.value.apiKey,
      api_model: apiConfig.value.apiModel || undefined,
      api_timeout: parseInt(apiConfig.value.apiTimeout) || 60
    });
    
    if (response.success) {
      message.success('API连接测试成功');
      connectionStatus.value = {
        type: 'success',
        message: '连接成功！API配置有效。',
        icon: markRaw(SuccessIcon)
      };
    } else {
      message.error(`API连接测试失败: ${response.message}`);
      connectionStatus.value = {
        type: 'error',
        message: `连接失败: ${response.message}`,
        icon: markRaw(ErrorIcon)
      };
    }
  } catch (error: any) {
    message.error(`测试连接出错: ${error.message || '未知错误'}`);
    connectionStatus.value = {
      type: 'error',
      message: `连接错误: ${error.message || '未知错误'}`,
      icon: markRaw(ErrorIcon)
    };
  } finally {
    testingConnection.value = false;
  }
}

function resetConfig() {
  apiConfig.value = {
    apiUrl: props.defaultApiUrl || '',
    apiKey: '',
    apiModel: props.defaultApiModel || '',
    apiTimeout: props.defaultApiTimeout || '60',
    saveApiConfig: true
  };
  
  // 清除本地存储
  if (window.localStorage) {
    localStorage.removeItem('apiConfig');
    message.success('已重置API配置并清除本地存储');
  } else {
    message.success('已重置API配置');
  }
  
  connectionStatus.value = null;
  emit('update:apiConfig', { ...apiConfig.value });
}

// 选择模型
function selectModel(key: string) {
  console.log('选择模型:', key);
  apiConfig.value.apiModel = key;
  
  // 通知父组件
  emit('update:apiConfig', { ...apiConfig.value });
}

// 显式保存配置的函数
function saveConfig() {
  saveApiConfigToLocalStorage({
    apiUrl: apiConfig.value.apiUrl,
    apiKey: apiConfig.value.apiKey,
    apiModel: apiConfig.value.apiModel,
    apiTimeout: apiConfig.value.apiTimeout,
    saveApiConfig: true
  });
  message.success('已将配置保存到本地');
}

onMounted(() => {
  // 加载保存的配置
  const savedConfig = loadApiConfig();
  
  if (savedConfig.saveApiConfig) {
    apiConfig.value = {
      apiUrl: savedConfig.apiUrl || props.defaultApiUrl || '',
      apiKey: savedConfig.apiKey || '',
      apiModel: savedConfig.apiModel || props.defaultApiModel || '',
      apiTimeout: savedConfig.apiTimeout || props.defaultApiTimeout || '60',
      saveApiConfig: true
    };
    
    // 通知父组件配置已加载
    emit('update:apiConfig', { ...apiConfig.value });
  }
});
</script>

<style scoped>
.api-config-section {
  margin-bottom: 1.5rem;
  position: relative;
}

.toggle-button {
  margin-bottom: 0.75rem;
  font-weight: 500;
  transition: all 0.3s ease;
  border-radius: 16px;
  padding: 4px 12px;
}

.toggle-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.toggle-text {
  margin-left: 4px;
}

.api-config-card {
  margin-bottom: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  background: linear-gradient(to bottom, rgba(240, 240, 245, 0.5), rgba(250, 250, 252, 0.8));
  padding: 16px;
  transition: all 0.3s ease;
}

.api-info-alert {
  margin-bottom: 16px;
  border-radius: 8px;
}

.url-feedback {
  padding: 6px 0;
}

.formatted-url {
  color: var(--n-text-color-info);
  font-size: 0.85rem;
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.url-tips {
  color: var(--n-text-color-info);
  font-size: 0.75rem;
  opacity: 0.8;
  line-height: 1.4;
}

.alert-actions {
  margin-top: 0.5rem;
  text-align: right;
}

.api-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  flex-wrap: wrap;
  gap: 12px;
}

.api-save-option {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 16px;
}

.api-save-option button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-weight: 500;
  background-color: rgba(0, 0, 0, 0.02);
  transition: all 0.2s ease;
}

.api-save-option button:hover {
  background-color: rgba(32, 128, 240, 0.08);
  transform: translateY(-1px);
}

.api-save-option button .n-icon {
  font-size: 16px;
}

.api-buttons {
  display: flex;
  gap: 0.75rem;
}

.timeout-input {
  width: 100%;
}

.timeout-controls {
  display: flex;
  align-items: center;
  margin-left: 8px;
}

.connection-status {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-radius: 8px;
  margin-top: 8px;
  font-weight: 500;
  animation: fadeIn 0.3s ease;
}

.connection-status.success {
  background-color: rgba(24, 160, 88, 0.1);
  color: var(--n-success-color);
}

.connection-status.error {
  background-color: rgba(208, 48, 80, 0.1);
  color: var(--n-error-color);
}

.status-icon {
  margin-right: 8px;
  font-size: 1.25rem;
}

.status-message {
  font-size: 0.9rem;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .api-actions {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .api-buttons {
    width: 100%;
    justify-content: space-between;
  }
}

.model-suggestions {
  margin-top: 6px;
  font-size: 0.75rem;
  color: var(--n-text-color-3);
}

.model-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}

.model-chips :deep(.n-tag) {
  cursor: pointer;
  transition: all 0.2s ease;
}

.model-chips :deep(.n-tag:hover) {
  background-color: rgba(32, 128, 240, 0.1);
  transform: translateY(-1px);
}

.model-tip {
  margin-bottom: 6px;
  font-size: 0.75rem;
  color: var(--n-text-color-3);
  font-style: italic;
}

.model-dropdown-btn {
  background-color: rgba(32, 128, 240, 0.1);
  transition: all 0.2s ease;
}

.model-dropdown-btn:hover {
  background-color: rgba(32, 128, 240, 0.2);
  transform: translateY(-1px);
}
</style>
