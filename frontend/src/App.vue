<template>
  <div id="app">
    <template v-if="isAuthPage">
      <router-view />
    </template>

    <template v-else>
      <div class="app-shell">
        <aside class="sidebar">
          <div class="brand-block">
            <div class="brand-mark">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M12 3l7 4v10l-7 4-7-4V7l7-4z" stroke="currentColor" stroke-width="1.8"/>
                <path d="M8 9.5h8L11 14h5l-8 6 5-5H8l5-5.5z" fill="currentColor"/>
              </svg>
            </div>
            <div>
              <div class="brand-title">TTAPI</div>
              <div class="brand-subtitle">API Test Console</div>
            </div>
          </div>

          <nav class="sidebar-nav">
            <router-link to="/" class="nav-item" active-class="active">
              <span class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M4 13h7V4H4v9zm9 7h7V4h-7v16zM4 20h7v-5H4v5z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                </svg>
              </span>
              <span>项目管理</span>
            </router-link>

            <router-link
              v-if="currentProjectId"
              :to="`/project/${currentProjectId}`"
              class="nav-item"
              active-class="active"
            >
              <span class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M4 7.5A2.5 2.5 0 016.5 5h3l1.4 1.5H17.5A2.5 2.5 0 0120 9v8.5a2.5 2.5 0 01-2.5 2.5h-11A2.5 2.5 0 014 17.5v-10z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                </svg>
              </span>
              <span>当前项目</span>
            </router-link>

            <router-link
              v-if="currentProjectId"
              :to="`/project/${currentProjectId}/scheduling`"
              class="nav-item"
              active-class="active"
            >
              <span class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M4 12h5l2-6 2 12 2-6h5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
              <span>调度与Worker</span>
            </router-link>
          </nav>

          <div class="sidebar-footer">
            <div class="theme-note">
              <span class="theme-dot"></span>
              轻量后台风格
            </div>
          </div>
        </aside>

        <div class="shell-main">
          <header class="topbar">
            <div>
              <h1 class="topbar-title">{{ pageTitle }}</h1>
              <p class="topbar-subtitle">{{ pageSubtitle }}</p>
            </div>

            <div class="topbar-actions">
              <div class="status-chip">
                <span class="status-dot"></span>
                在线
              </div>
              <div class="user-card">
                <div class="user-avatar">{{ userInitials }}</div>
                <div class="user-meta">
                  <strong>{{ username }}</strong>
                  <span>User</span>
                </div>
                <button @click="handleLogout" class="ghost-btn">退出</button>
              </div>
            </div>
          </header>

          <main class="page-container">
            <router-view />
          </main>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const isAuthPage = computed(() => ['/login', '/register'].includes(route.path))
const currentProjectId = computed(() => route.params.projectId || '')
const currentUsername = computed(() => localStorage.getItem('username') || '')
const currentUserId = computed(() => localStorage.getItem('userId') || '')
const username = computed(() => currentUsername.value || (currentUserId.value ? `用户 ${currentUserId.value}` : '未登录用户'))
const userInitials = computed(() => (username.value ? username.value.slice(0, 1).toUpperCase() : 'U'))

const pageTitle = computed(() => {
  if (route.path.includes('/scheduling')) return 'Scheduling'
  if (route.path.startsWith('/project/')) return '测试用例'
  return '项目管理'
})

const pageSubtitle = computed(() => {
  if (route.path.includes('/scheduling')) return 'Monitor run_queue and worker heartbeats'
  if (route.path.startsWith('/project/')) return '维护接口用例并执行测试'
  return '统一管理你的 API 自动化测试项目'
})

const handleLogout = () => {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('userId')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<style>
:root {
  --bg-page: #f4f7f7;
  --bg-panel: rgba(238, 247, 246, 0.88);
  --bg-card: #ffffff;
  --bg-card-soft: #f7fbfa;
  --border-color: #dce8e5;
  --border-strong: #c6dad5;
  --text-strong: #18232f;
  --text-main: #304251;
  --text-muted: #7d8b98;
  --primary: #12b3a5;
  --primary-dark: #0d9488;
  --primary-soft: #dcf5f1;
  --danger: #f16464;
  --danger-soft: #ffe7e7;
  --warning: #f59e0b;
  --info: #5b7cff;
  --shadow-sm: 0 6px 18px rgba(17, 24, 39, 0.05);
  --shadow-md: 0 16px 40px rgba(17, 24, 39, 0.08);
  --radius-sm: 12px;
  --radius-md: 18px;
  --radius-lg: 24px;
}

* {
  box-sizing: border-box;
}

html,
body,
#app {
  min-height: 100%;
}

body {
  margin: 0;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background:
    radial-gradient(circle at top left, rgba(18, 179, 165, 0.12), transparent 28%),
    linear-gradient(180deg, #eef7f6 0%, #f7f9fb 100%);
  color: var(--text-main);
}

a {
  color: inherit;
}

button,
input,
textarea,
select {
  font: inherit;
}

button {
  cursor: pointer;
}

.app-shell {
  min-height: 100vh;
  display: flex;
}

.sidebar {
  width: 248px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(16px);
  border-right: 1px solid rgba(198, 218, 213, 0.8);
  padding: 22px 14px;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 10px 24px;
}

.brand-mark {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #11376b 0%, #19b8aa 100%);
  color: #fff;
  box-shadow: var(--shadow-sm);
}

.brand-mark svg {
  width: 24px;
  height: 24px;
}

.brand-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-strong);
  letter-spacing: 0.02em;
}

.brand-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 14px;
  border-radius: 14px;
  text-decoration: none;
  color: var(--text-main);
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgba(18, 179, 165, 0.08);
  color: var(--primary-dark);
}

.nav-item.active {
  background: var(--primary-soft);
  color: var(--primary-dark);
  font-weight: 700;
}

.nav-icon {
  width: 18px;
  height: 18px;
  display: inline-flex;
}

.nav-icon svg {
  width: 18px;
  height: 18px;
}

.sidebar-footer {
  margin-top: auto;
  padding: 16px 10px 0;
}

.theme-note {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
  font-size: 13px;
}

.theme-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--primary), #8ce3d5);
}

.shell-main {
  flex: 1;
  min-width: 0;
  padding: 18px 22px 22px;
}

.topbar {
  min-height: 92px;
  border-radius: 24px;
  padding: 24px 28px;
  background: rgba(255, 255, 255, 0.74);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(220, 232, 229, 0.9);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.topbar-title {
  margin: 0;
  font-size: 32px;
  line-height: 1.1;
  color: var(--text-strong);
}

.topbar-subtitle {
  margin: 8px 0 0;
  color: var(--text-muted);
  font-size: 14px;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.status-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border-color);
  color: var(--text-main);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #22c55e;
  box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.14);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--border-color);
}

.user-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary) 0%, #0f766e 100%);
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.user-meta strong {
  color: var(--text-strong);
  font-size: 14px;
}

.user-meta span {
  color: var(--text-muted);
  font-size: 12px;
}

.ghost-btn {
  border: 1px solid var(--border-color);
  background: #fff;
  color: var(--text-main);
  border-radius: 12px;
  padding: 10px 14px;
}

.ghost-btn:hover {
  border-color: var(--primary);
  color: var(--primary-dark);
}

.page-container {
  padding-top: 20px;
}

@media (max-width: 1100px) {
  .app-shell {
    flex-direction: column;
  }

  .sidebar {
    width: auto;
    height: auto;
    position: static;
    border-right: 0;
    border-bottom: 1px solid rgba(198, 218, 213, 0.8);
  }

  .sidebar-footer {
    display: none;
  }
}

@media (max-width: 820px) {
  .shell-main {
    padding: 14px;
  }

  .topbar {
    padding: 18px;
    border-radius: 20px;
    flex-direction: column;
    align-items: flex-start;
  }

  .topbar-title {
    font-size: 26px;
  }

  .topbar-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .user-card {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
