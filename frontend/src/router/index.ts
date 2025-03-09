import { createRouter, createWebHashHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { apiService } from '@/services/api';
import StockAnalysisApp from '@/components/StockAnalysisApp.vue';
import LoginPage from '@/components/LoginPage.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: StockAnalysisApp,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  console.log(`路由跳转: 从 ${from.path} 到 ${to.path}`);
  
  // 如果已经在登录页面，直接通过
  if (to.path === '/login') {
    next();
    return;
  }
  
  // 检查路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    console.log('当前路由需要认证');
    
    try {
      // 先检查系统是否需要登录
      const requireLogin = await apiService.checkNeedLogin();
      console.log('系统是否需要登录:', requireLogin);
      
      if (!requireLogin) {
        // 系统不需要登录，直接通过
        console.log('系统不需要登录，允许访问');
        next();
        return;
      }
      
      // 系统需要登录，检查本地是否有token
      const token = localStorage.getItem('token');
      if (!token) {
        console.log('本地没有token，跳转到登录页');
        next({ name: 'Login' });
        return;
      }
      
      const isAuthenticated = await apiService.checkAuth();
      console.log('认证检查结果:', isAuthenticated);
      
      if (!isAuthenticated) {
        // 未登录，重定向到登录页
        console.log('认证失败，跳转到登录页');
        next({ name: 'Login' });
      } else {
        // 已登录，允许访问
        console.log('认证成功，允许访问');
        next();
      }
    } catch (error) {
      console.error('认证检查失败:', error);
      // 认证检查失败，重定向到登录页
      next({ name: 'Login' });
    }
  } else {
    // 不需要认证的路由，直接访问
    console.log('当前路由不需要认证，直接访问');
    next();
  }
});

export default router; 