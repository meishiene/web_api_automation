<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <header v-if="showHeader" class="header">
      <div class="header-content">
        <div class="logo-section">
          <div class="logo">
            <svg class="logo-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
            <span class="logo-text">API测试平台</span>
          </div>
        </div>
        <nav class="nav-menu">
          <router-link to="/" class="nav-link" active-class="active">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
            </svg>
            项目管理
          </router-link>
        </nav>
        <div class="user-section">
          <div class="user-info">
            <div class="user-avatar">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </div>
            <span class="username">{{ username }}</span>
          </div>
          <button @click="handleLogout" class="logout-btn">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.59L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
            </svg>
            退出登录
          </button>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- 页脚 -->
    <footer v-if="showHeader" class="footer">
      <div class="footer-content">
        <p>&copy; 2026 API自动化测试平台. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const username = ref('')

const showHeader = computed(() => {
  return !['/login', '/register'].includes(route.path)
})

onMounted(() => {
  const userId = localStorage.getItem('userId')
  if (userId) {
    username.value = `用户 ${userId}`
  }
})

const handleLogout = () => {
  localStorage.removeItem('userId')
  router.push('/login')
}
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary-color: #6366f1;
  --primary-dark: #4f46e5;
  --primary-light: #a5b4fc;
  --secondary-color: #f59e0b;
  --success-color: #10b981;
  --error-color: #ef4444;
  --warning-color: #f59e0b;
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --border-radius: 8px;
  --border-radius-lg: 12px;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, var(--gray-50) 0%, var(--gray-100) 100%);
  color: var(--gray-800);
  line-height: 1.6;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--gray-200);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 4rem;
}

.logo-section {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--primary-color);
}

.logo-icon {
  width: 2rem;
  height: 2rem;
  color: var(--primary-color);
}

.logo-text {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 导航菜单 */
.nav-menu {
  display: flex;
  gap: 2rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  color: var(--gray-600);
  text-decoration: none;
  font-weight: 500;
  border-radius: var(--border-radius);
  transition: all 0.2s ease;
  position: relative;
}

.nav-link:hover {
  color: var(--primary-color);
  background: var(--primary-light);
}

.nav-link.active {
  color: var(--primary-color);
  background: var(--primary-light);
}

.nav-link svg {
  width: 1.25rem;
  height: 1.25rem;
}

/* 用户区域 */
.user-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: var(--gray-50);
  border-radius: var(--border-radius);
}

.user-avatar {
  width: 2rem;
  height: 2rem;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-avatar svg {
  width: 1rem;
  height: 1rem;
}

.username {
  font-weight: 500;
  color: var(--gray-700);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--error-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}

.logout-btn svg {
  width: 1rem;
  height: 1rem;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  padding: 2rem 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* 页脚 */
.footer {
  background: var(--gray-800);
  color: var(--gray-400);
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 1rem;
    height: auto;
    flex-direction: column;
    gap: 1rem;
    padding-top: 1rem;
    padding-bottom: 1rem;
  }

  .nav-menu {
    gap: 1rem;
  }

  .user-section {
    flex-direction: column;
    gap: 0.5rem;
  }

  .main-content {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .nav-menu {
    display: none;
  }

  .logo-text {
    display: none;
  }
}
</style>
