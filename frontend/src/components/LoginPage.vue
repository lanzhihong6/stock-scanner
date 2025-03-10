<template>
  <div class="login-container">
    <div class="login-background">
      <div class="login-shape shape1"></div>
      <div class="login-shape shape2"></div>
      <div class="login-shape shape3"></div>
      <div class="login-shape shape4"></div>
      <div class="login-shape shape5"></div>
      <div class="login-particle particle1"></div>
      <div class="login-particle particle2"></div>
      <div class="login-particle particle3"></div>
      <div class="login-particle particle4"></div>
      <div class="login-particle particle5"></div>
      <div class="login-particle particle6"></div>
    </div>
    
    <n-card class="login-card" :bordered="false">
      <div class="login-header">
        <div class="login-logo">
          <n-icon :component="BarChartIcon" color="#2080f0" size="36" class="logo-icon" />
        </div>
        <h1 class="login-title">股票AI分析系统</h1>
        <p class="login-subtitle">使用AI技术分析股票市场趋势</p>
      </div>
      
      <n-form
        ref="formRef"
        :model="formValue"
        :rules="rules"
        label-placement="left"
        label-width="0"
        require-mark-placement="right-hanging"
        class="login-form"
      >
        <n-form-item path="password">
          <n-input
            v-model:value="formValue.password"
            type="password"
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
            size="large"
            class="login-input"
          >
            <template #prefix>
              <n-icon :component="LockClosedIcon" />
            </template>
          </n-input>
        </n-form-item>
        
        <div class="login-button-container">
          <n-button
            type="primary"
            size="large"
            block
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </n-button>
        </div>
      </n-form>
      
      <div class="login-footer">
        <n-text depth="3">© {{ new Date().getFullYear() }} 股票AI分析系统</n-text>
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue';
import { useRouter } from 'vue-router';
import { 
  NCard, 
  NForm, 
  NFormItem, 
  NInput, 
  NButton, 
  NIcon,
  NText,
  useMessage,
  useNotification
} from 'naive-ui';
import type { FormInst, FormRules } from 'naive-ui';
import { 
  BarChartOutline as BarChartIcon, 
  LockClosedOutline as LockClosedIcon,
  NotificationsOutline as NotificationsIcon
} from '@vicons/ionicons5';
import { apiService } from '@/services/api';
import type { LoginRequest } from '@/types';

const message = useMessage();
const notification = useNotification();
const router = useRouter();
const formRef = ref<FormInst | null>(null);
const loading = ref(false);

const formValue = reactive({
  password: ''
});

const rules: FormRules = {
  password: [
    {
      required: true,
      message: '请输入密码'
    }
  ]
};

// 显示系统公告
const showAnnouncement = (content: string) => {
  if (!content) return;
  
  notification.info({
    title: '系统公告',
    content: () => h('div', { style: 'display: flex; align-items: center;' }, [
      h(NIcon, { component: NotificationsIcon, style: 'margin-right: 8px; font-size: 18px;' }),
      h('span', null, content)
    ]),
    duration: 10000,
    keepAliveOnHover: true,
    closable: true
  });
};

// 页面加载时检查是否已登录并获取系统公告
onMounted(async () => {
  try {
    // 获取系统配置
    const config = await apiService.getConfig();
    if (config.announcement) {
      showAnnouncement(config.announcement);
    }
    
    // 不重复检查是否需要登录，因为路由守卫已经做了这个检查
    // 直接检查是否已登录
    const token = localStorage.getItem('token');
    if (!token) {
      return; // 没有token，停留在登录页
    }
    
    const isAuthenticated = await apiService.checkAuth();
    console.log('登录页面认证检查结果:', isAuthenticated);
    
    if (isAuthenticated) {
      // 已登录，跳转到主页
      console.log('已登录，跳转到主页');
      router.push('/');
    }
  } catch (error) {
    console.error('认证检查或获取配置失败:', error);
  }
});

const handleLogin = () => {
  formRef.value?.validate(async (errors) => {
    if (errors) {
      return;
    }
    
    loading.value = true;
    
    try {
      const loginRequest: LoginRequest = {
        password: formValue.password
      };
      
      const response = await apiService.login(loginRequest);
      
      if (response.access_token) {
        message.success('登录成功');
        // 登录成功后跳转到主页
        router.push('/');
      } else {
        message.error(response.message || '登录失败');
      }
    } catch (error: any) {
      console.error('登录失败:', error);
      message.error(error.message || '登录失败');
    } finally {
      loading.value = false;
    }
  });
};
</script>

<style scoped>
@keyframes float {
  0% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(5deg);
  }
  100% {
    transform: translateY(0px) rotate(0deg);
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.6;
  }
  100% {
    transform: scale(1);
    opacity: 0.8;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes floatParticle {
  0% {
    transform: translateY(0) translateX(0);
  }
  25% {
    transform: translateY(-15px) translateX(15px);
  }
  50% {
    transform: translateY(0) translateX(30px);
  }
  75% {
    transform: translateY(15px) translateX(15px);
  }
  100% {
    transform: translateY(0) translateX(0);
  }
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: fixed;
  top: 0;
  left: 0;
  overflow: hidden;
}

.login-background {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 0;
  top: 0;
  left: 0;
  overflow: hidden;
}

.login-shape {
  position: absolute;
  border-radius: 50%;
  animation: pulse 8s infinite ease-in-out;
}

.shape1 {
  width: 50vw;
  height: 50vw;
  max-width: 600px;
  max-height: 600px;
  background: linear-gradient(135deg, rgba(32, 128, 240, 0.2) 0%, rgba(32, 128, 240, 0.1) 100%);
  top: -15%;
  right: -10%;
  animation-delay: 0s;
}

.shape2 {
  width: 60vw;
  height: 60vw;
  max-width: 800px;
  max-height: 800px;
  background: linear-gradient(135deg, rgba(32, 128, 240, 0.1) 0%, rgba(32, 128, 240, 0.05) 100%);
  bottom: -30%;
  left: -15%;
  animation-delay: 2s;
}

.shape3 {
  width: 30vw;
  height: 30vw;
  max-width: 400px;
  max-height: 400px;
  background: linear-gradient(135deg, rgba(32, 128, 240, 0.15) 0%, rgba(32, 128, 240, 0.05) 100%);
  top: 20%;
  right: 15%;
  animation-delay: 4s;
}

.shape4 {
  width: 25vw;
  height: 25vw;
  max-width: 300px;
  max-height: 300px;
  background: linear-gradient(135deg, rgba(32, 128, 240, 0.1) 0%, rgba(32, 128, 240, 0.05) 100%);
  top: 60%;
  left: 10%;
  animation-delay: 1s;
}

.shape5 {
  width: 15vw;
  height: 15vw;
  max-width: 200px;
  max-height: 200px;
  background: linear-gradient(135deg, rgba(32, 128, 240, 0.15) 0%, rgba(32, 128, 240, 0.1) 100%);
  top: 30%;
  left: 20%;
  animation-delay: 3s;
}

.login-particle {
  position: absolute;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.6);
  animation: floatParticle 15s infinite ease-in-out;
}

.particle1 {
  width: 10px;
  height: 10px;
  top: 20%;
  left: 30%;
  animation-duration: 20s;
}

.particle2 {
  width: 15px;
  height: 15px;
  top: 40%;
  left: 70%;
  animation-duration: 25s;
}

.particle3 {
  width: 8px;
  height: 8px;
  top: 70%;
  left: 40%;
  animation-duration: 18s;
}

.particle4 {
  width: 12px;
  height: 12px;
  top: 30%;
  left: 60%;
  animation-duration: 22s;
}

.particle5 {
  width: 6px;
  height: 6px;
  top: 60%;
  left: 20%;
  animation-duration: 15s;
}

.particle6 {
  width: 10px;
  height: 10px;
  top: 80%;
  left: 80%;
  animation-duration: 30s;
}

.login-card {
  width: 420px;
  max-width: 90%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  z-index: 1;
  padding: 30px;
  animation: fadeIn 0.8s ease-out;
  transition: all 0.3s ease;
  position: relative;
}

.login-card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  transform: translateY(-5px);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-logo {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.logo-icon {
  animation: float 6s infinite ease-in-out;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px;
  background: linear-gradient(90deg, #2080f0, #44a4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.login-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.login-form {
  animation: fadeIn 0.8s ease-out 0.2s both;
}

.login-input {
  transition: all 0.3s ease;
}

.login-input:hover {
  transform: translateY(-2px);
}

.login-button-container {
  margin-top: 30px;
  margin-bottom: 20px;
  animation: fadeIn 0.8s ease-out 0.4s both;
}

.login-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 2px;
  transition: all 0.3s ease;
  background: linear-gradient(90deg, #2080f0, #44a4ff);
  border: none;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(32, 128, 240, 0.3);
  background: linear-gradient(90deg, #1c72d9, #3b9aff);
}

.login-footer {
  text-align: center;
  padding: 16px 0 0;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  margin-top: 20px;
  animation: fadeIn 0.8s ease-out 0.6s both;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    width: 90%;
    padding: 20px;
  }
  
  .login-title {
    font-size: 24px;
  }
  
  .login-subtitle {
    font-size: 12px;
  }
  
  .login-button {
    height: 44px;
    font-size: 14px;
  }
  
  /* 移动设备上的背景形状调整 */
  .shape1 {
    width: 70vw;
    height: 70vw;
    top: -30%;
    right: -20%;
  }
  
  .shape2 {
    width: 80vw;
    height: 80vw;
    bottom: -40%;
    left: -30%;
  }
  
  .shape3 {
    width: 50vw;
    height: 50vw;
    top: 50%;
    right: -20%;
  }
  
  .shape4, .shape5 {
    display: none;
  }
  
  .login-particle {
    display: none;
  }
}
</style> 