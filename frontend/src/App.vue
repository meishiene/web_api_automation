<template>
  <div id="app">
    <router-view v-if="isAuthPage" />

    <template v-else>
      <div class="layout-shell">
        <aside class="sidebar">
          <div class="sidebar-brand">
            <h1>自动化测试平台</h1>
          </div>

          <nav class="sidebar-nav">
            <button
              v-for="item in menuItems"
              :key="item.key"
              class="nav-item"
              :class="{ active: isActiveMenu(item), disabled: item.disabled }"
              :disabled="item.disabled"
              @click="goMenu(item)"
            >
              <span class="nav-icon" v-html="item.icon"></span>
              <span>{{ item.label }}</span>
            </button>
          </nav>

          <div class="sidebar-bottom">
            <button class="settings-btn" @click="toggleTheme">
              <span class="nav-icon" v-html="theme === 'dark' ? moonIcon : sunIcon"></span>
              <span>{{ theme === 'dark' ? '深色模式' : '浅色模式' }}</span>
            </button>
          </div>
        </aside>

        <div class="main-shell">
          <header class="topbar">
            <div class="topbar-search">
              <span class="search-icon" v-html="searchIcon"></span>
              <input type="text" placeholder="搜索项目、用例、接口、任务..." />
            </div>

            <div class="topbar-actions">
              <button class="icon-btn" aria-label="通知">
                <span v-html="bellIcon"></span>
                <span class="notify-dot"></span>
              </button>
              <div class="user-panel">
                <div class="user-avatar">{{ userInitials }}</div>
                <div class="user-copy">
                  <span>{{ username }}</span>
                  <small v-if="activeProjectId">项目 #{{ activeProjectId }}</small>
                </div>
              </div>
            </div>
          </header>

          <div class="tabbar">
            <button
              v-for="tab in tabs"
              :key="tab.path"
              class="tab-item"
              :class="{ active: activeTab === tab.path }"
              @click="switchTab(tab.path)"
            >
              <span>{{ tab.label }}</span>
              <button v-if="tabs.length > 1" class="tab-close" @click.stop="closeTab(tab.path)">
                ×
              </button>
            </button>
          </div>

          <main class="page-wrapper">
            <router-view />
          </main>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getActiveProjectId, setActiveProjectId } from '@/utils/projectContext'

const router = useRouter()
const route = useRoute()

const THEME_STORAGE_KEY = 'ttapi-ui-theme'
const theme = ref('light')
const tabs = ref([{ path: '/', label: '仪表盘' }])
const activeTab = ref('/')
const activeProjectId = ref(getActiveProjectId())

const isAuthPage = computed(() => ['/login', '/register'].includes(route.path))
const username = computed(() => localStorage.getItem('username') || '测试工程师')
const userInitials = computed(() => (username.value ? username.value.slice(0, 1).toUpperCase() : 'U'))

const dashboardIcon = '<svg viewBox="0 0 24 24" fill="none"><path d="M4 13h7V4H4v9zm9 7h7V4h-7v16zM4 20h7v-5H4v5z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'
const folderIcon = '<svg viewBox="0 0 24 24" fill="none"><path d="M4 7.5A2.5 2.5 0 016.5 5h3l1.4 1.5H17.5A2.5 2.5 0 0120 9v8.5a2.5 2.5 0 01-2.5 2.5h-11A2.5 2.5 0 014 17.5v-10z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'
const casesIcon = '<svg viewBox="0 0 24 24" fill="none"><path d="M9 7h8M9 12h8M9 17h8M5 7h.01M5 12h.01M5 17h.01" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
const globeIcon = '<svg viewBox="0 0 24 24" fill="none"><path d="M12 20c4.418 0 8-3.582 8-8s-3.582-8-8-8-8 3.582-8 8 3.582 8 8 8zm0 0c2.21 0 4-3.582 4-8s-1.79-8-4-8-4 3.582-4 8 1.79 8 4 8zm-7-8h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
const monitorIcon = '<svg viewBox="0 0 24 24" fill="none"><path d="M4 6.5A2.5 2.5 0 016.5 4h11A2.5 2.5 0 0120 6.5v7A2.5 2.5 0 0117.5 16h-11A2.5 2.5 0 014 13.5v-7zM8 20h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
const clockIcon = '<svg viewBox="0 0 24 24" fill="none"><path d="M12 7v5l3 2m5-2a8 8 0 11-16 0 8 8 0 0116 0z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
const reportIcon = '<svg viewBox="0 0 24 24" fill="none"><path d="M6 18V9m6 9V5m6 13v-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
const searchIcon = '<svg viewBox="0 0 24 24" fill="none"><path d="M21 21l-4.35-4.35M10.8 18a7.2 7.2 0 100-14.4 7.2 7.2 0 000 14.4z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
const bellIcon = '<svg viewBox="0 0 24 24" fill="none"><path d="M6 9a6 6 0 1112 0v4l1.5 2H4.5L6 13V9zm4.5 8a1.5 1.5 0 003 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
const sunIcon = '<svg viewBox="0 0 24 24" fill="none"><path d="M12 3v2.5M12 18.5V21M4.93 4.93l1.77 1.77M17.3 17.3l1.77 1.77M3 12h2.5M18.5 12H21M4.93 19.07l1.77-1.77M17.3 6.7l1.77-1.77M12 16a4 4 0 100-8 4 4 0 000 8z" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>'
const moonIcon = '<svg viewBox="0 0 24 24" fill="none"><path d="M20 15.2A7.7 7.7 0 118.8 4 6.4 6.4 0 0020 15.2z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'

const menuItems = computed(() => {
  const pid = activeProjectId.value
  return [
    { key: 'dashboard', label: '仪表盘', path: '/', icon: dashboardIcon, disabled: false },
    { key: 'projects', label: '项目管理', path: '/projects', icon: folderIcon, disabled: false },
    { key: 'testcases', label: '测试用例', path: '/testcases', icon: casesIcon, disabled: false },
    { key: 'api-test', label: 'API测试', path: pid ? `/project/${pid}` : '/projects', icon: globeIcon, disabled: !pid },
    { key: 'ui-automation', label: 'UI自动化', path: pid ? `/project/${pid}/web-test-cases` : '/projects', icon: monitorIcon, disabled: !pid },
    { key: 'tasks', label: '任务管理', path: pid ? `/project/${pid}/scheduling` : '/projects', icon: clockIcon, disabled: !pid },
    { key: 'reports', label: '测试报告', path: pid ? `/project/${pid}/reports` : '/projects', icon: reportIcon, disabled: !pid },
  ]
})

const resolveTabLabel = (path) => {
  if (path === '/') return '仪表盘'
  if (path === '/projects') return '项目管理'
  if (path === '/testcases') return '测试用例'
  if (path.startsWith('/project/') && path.includes('/web-test-cases')) return 'UI自动化'
  if (path.startsWith('/project/') && path.includes('/scheduling')) return '任务管理'
  if (path.startsWith('/project/') && path.includes('/reports')) return '测试报告'
  if (path.startsWith('/project/') && path.includes('/executions')) return '执行中心'
  if (path.startsWith('/project/') && path.includes('/environments')) return '环境治理'
  if (path.startsWith('/project/') && path.includes('/integration-governance')) return '集成治理'
  if (path.startsWith('/project/') && path.includes('/batches')) return '批次结果'
  if (path.startsWith('/project/') && path.includes('/runs/')) return '运行详情'
  if (path.startsWith('/project/') && path.includes('/web-runs/')) return 'UI运行详情'
  if (path.startsWith('/project/')) return 'API测试'
  return '工作台'
}

const isActiveMenu = (item) => {
  if (item.key === 'dashboard') return route.path === '/' || route.path === '/operations/overview'
  if (item.key === 'projects') return route.path === '/projects'
  if (item.key === 'testcases') return route.path === '/testcases'
  if (!activeProjectId.value || item.disabled) return false
  const pid = activeProjectId.value
  if (item.key === 'api-test') {
    return route.path === `/project/${pid}` || route.path.startsWith(`/project/${pid}/runs/`) || route.path.startsWith(`/project/${pid}/environments`) || route.path.startsWith(`/project/${pid}/integration-governance`)
  }
  if (item.key === 'ui-automation') {
    return route.path.startsWith(`/project/${pid}/web-test-cases`) || route.path.startsWith(`/project/${pid}/web-runs/`)
  }
  if (item.key === 'tasks') {
    return route.path.startsWith(`/project/${pid}/scheduling`) || route.path.startsWith(`/project/${pid}/batches`)
  }
  if (item.key === 'reports') {
    return route.path.startsWith(`/project/${pid}/reports`) || route.path.startsWith(`/project/${pid}/executions`)
  }
  return false
}

const goMenu = (item) => {
  if (item.disabled) return
  router.push(item.path)
}

const switchTab = (path) => {
  activeTab.value = path
  router.push(path)
}

const closeTab = (path) => {
  const nextTabs = tabs.value.filter((tab) => tab.path !== path)
  if (!nextTabs.length) return
  tabs.value = nextTabs
  if (activeTab.value === path) {
    const fallback = nextTabs[nextTabs.length - 1]
    activeTab.value = fallback.path
    router.push(fallback.path)
  }
}

const applyTheme = (value) => {
  document.documentElement.dataset.theme = value
  document.body.dataset.theme = value
  localStorage.setItem(THEME_STORAGE_KEY, value)
}

const toggleTheme = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
}

watch(
  () => route.path,
  (path) => {
    const routeProjectId = Number(route.params.projectId)
    if (Number.isFinite(routeProjectId) && routeProjectId > 0) {
      activeProjectId.value = routeProjectId
      setActiveProjectId(routeProjectId)
    }

    activeTab.value = path
    const label = resolveTabLabel(path)
    if (!tabs.value.find((tab) => tab.path === path)) {
      tabs.value = [...tabs.value, { path, label }]
    }
  },
  { immediate: true }
)

watch(theme, (value) => {
  applyTheme(value)
})

onMounted(() => {
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY)
  theme.value = savedTheme === 'dark' ? 'dark' : 'light'
  applyTheme(theme.value)
})
</script>

<style>
:root,
:root[data-theme='light'] {
  --bg-page: #f5f6f8;
  --bg-card: #ffffff;
  --bg-muted: #f5f7fa;
  --text-strong: #303133;
  --text-main: #606266;
  --text-muted: #909399;
  --border-color: #e1e4e8;
  --border-color-strong: #dcdfe6;
  --primary: #3498db;
  --primary-strong: #2980b9;
  --success: #27ae60;
  --danger: #e74c3c;
  --warning: #f39c12;
  --surface-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  --radius: 4px;
  --sidebar-bg: #2c3e50;
  --sidebar-bg-active: #34495e;
  --sidebar-text: #bdc3c7;
  --sidebar-text-active: #ffffff;
}

:root[data-theme='dark'] {
  --bg-page: #111827;
  --bg-card: #1f2937;
  --bg-muted: #111827;
  --text-strong: #f3f4f6;
  --text-main: #d1d5db;
  --text-muted: #9ca3af;
  --border-color: #374151;
  --border-color-strong: #4b5563;
  --primary: #60a5fa;
  --primary-strong: #3b82f6;
  --success: #34d399;
  --danger: #f87171;
  --warning: #fbbf24;
  --surface-shadow: 0 1px 2px rgba(0, 0, 0, 0.18);
  --radius: 4px;
  --sidebar-bg: #0f172a;
  --sidebar-bg-active: #1e293b;
  --sidebar-text: #94a3b8;
  --sidebar-text-active: #f8fafc;
}

* { box-sizing: border-box; }
html, body, #app { min-height: 100%; }
body {
  margin: 0;
  font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
  background: var(--bg-page);
  color: var(--text-main);
}
a { color: inherit; text-decoration: none; }
button, input, textarea, select { font: inherit; }
button { cursor: pointer; }

.layout-shell { display: flex; min-height: 100vh; background: var(--bg-page); overflow: hidden; }
.sidebar {
  width: 200px;
  background: var(--sidebar-bg);
  color: var(--sidebar-text-active);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}
.sidebar-brand {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.sidebar-brand h1 { margin: 0; font-size: 18px; font-weight: 500; color: #fff; }
.sidebar-nav { padding: 8px 0; display: flex; flex-direction: column; }
.nav-item {
  width: 100%;
  border: 0;
  background: transparent;
  color: var(--sidebar-text);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 16px;
  text-align: left;
  font-size: 14px;
  transition: background 0.18s ease, color 0.18s ease;
}
.nav-item:hover { background: var(--sidebar-bg-active); color: var(--sidebar-text-active); }
.nav-item.active {
  background: var(--sidebar-bg-active);
  color: var(--sidebar-text-active);
  border-left: 3px solid var(--primary);
}
.nav-item.disabled { opacity: 0.45; cursor: not-allowed; }
.nav-icon { width: 16px; height: 16px; display: inline-flex; }
.nav-icon svg { width: 16px; height: 16px; }
.sidebar-bottom {
  margin-top: auto;
  padding: 16px;
  border-top: 1px solid rgba(255,255,255,0.08);
}
.settings-btn {
  width: 100%;
  border: 0;
  background: transparent;
  color: var(--sidebar-text);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  font-size: 14px;
  border-radius: var(--radius);
}
.settings-btn:hover { background: var(--sidebar-bg-active); color: var(--sidebar-text-active); }
.main-shell { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.topbar {
  height: 60px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  gap: 16px;
}
.topbar-search {
  position: relative;
  width: 100%;
  max-width: 500px;
  display: flex;
  align-items: center;
}
.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  display: inline-flex;
}
.search-icon svg { width: 16px; height: 16px; }
.topbar-search input {
  width: 100%;
  height: 36px;
  padding: 0 14px 0 40px;
  border: 1px solid var(--border-color-strong);
  border-radius: var(--radius);
  background: var(--bg-muted);
  color: var(--text-main);
  outline: none;
}
.topbar-search input:focus { border-color: var(--primary); background: var(--bg-card); }
.topbar-actions { display: flex; align-items: center; gap: 12px; }
.icon-btn {
  position: relative;
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: var(--radius);
  background: transparent;
  color: var(--text-main);
  display: grid;
  place-items: center;
}
.icon-btn:hover { background: var(--bg-muted); }
.icon-btn svg { width: 18px; height: 18px; }
.notify-dot {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--danger);
}
.user-panel {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 16px;
  border-left: 1px solid var(--border-color);
}
.user-copy { display: flex; flex-direction: column; gap: 2px; }
.user-copy span { font-size: 14px; color: var(--text-main); }
.user-copy small { font-size: 12px; color: var(--text-muted); }
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 13px;
  font-weight: 700;
}
.tabbar {
  height: 40px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 8px;
  overflow-x: auto;
}
.tab-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 32px;
  border: 0;
  border-radius: var(--radius);
  padding: 0 14px;
  background: var(--bg-muted);
  color: var(--text-main);
  font-size: 13px;
  flex-shrink: 0;
}
.tab-item.active { background: var(--primary); color: #fff; }
.tab-close {
  border: 0;
  background: transparent;
  color: inherit;
  padding: 0;
  font-size: 14px;
  line-height: 1;
}
.page-wrapper { flex: 1; overflow: auto; }

@media (max-width: 1100px) {
  .layout-shell { flex-direction: column; }
  .sidebar { width: auto; }
}
</style>
