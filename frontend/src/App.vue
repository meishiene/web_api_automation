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
                <path d="M12 3l7 4v10l-7 4-7-4V7l7-4z" stroke="currentColor" stroke-width="1.8" />
                <path d="M8 9.5h8L11 14h5l-8 6 5-5H8l5-5.5z" fill="currentColor" />
              </svg>
            </div>
            <div class="brand-copy">
              <div class="brand-title">TTAPI</div>
              <div class="brand-subtitle">Automation Workspace</div>
            </div>
          </div>

          <div class="sidebar-section">
            <div class="sidebar-label">Workspace</div>
            <nav class="sidebar-nav">
              <router-link
                v-for="link in workspaceLinks"
                :key="link.to"
                :to="link.to"
                class="nav-item"
                :class="{ active: isLinkActive(link.to, link.matchPrefixes) }"
              >
                <span class="nav-icon" v-html="link.icon"></span>
                <span>{{ link.label }}</span>
              </router-link>
            </nav>
          </div>

          <div v-if="currentProjectId" class="sidebar-section project-zone">
            <div class="sidebar-label">Current Project</div>
            <div class="project-chip">
              <span class="project-chip-dot"></span>
              <span>Project #{{ currentProjectId }}</span>
            </div>
            <nav class="sidebar-nav">
              <router-link
                v-for="link in projectLinks"
                :key="link.to"
                :to="link.to"
                class="nav-item"
                :class="{ active: isLinkActive(link.to, link.matchPrefixes) }"
              >
                <span class="nav-icon" v-html="link.icon"></span>
                <span>{{ link.label }}</span>
              </router-link>
            </nav>
          </div>

          <div class="sidebar-footer">
            <button class="theme-toggle" @click="toggleTheme">
              <span class="theme-toggle-track">
                <span class="theme-toggle-thumb" :class="{ dark: theme === 'dark' }"></span>
              </span>
              <span>{{ theme === 'dark' ? '深色模式' : '浅色模式' }}</span>
            </button>

            <div class="sidebar-note">
              <span class="sidebar-note-dot"></span>
              平台完善工作线已启动
            </div>
          </div>
        </aside>

        <div class="shell-main">
          <header class="topbar">
            <div>
              <div class="page-kicker">{{ pageKicker }}</div>
              <h1 class="topbar-title">{{ pageTitle }}</h1>
              <p class="topbar-subtitle">{{ pageSubtitle }}</p>
            </div>

            <div class="topbar-actions">
              <div class="project-context" v-if="currentProjectId">
                <span>当前上下文</span>
                <strong>Project #{{ currentProjectId }}</strong>
              </div>

              <button class="icon-theme-btn" @click="toggleTheme" :aria-label="theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'">
                <svg v-if="theme === 'dark'" viewBox="0 0 24 24" fill="none">
                  <path d="M12 3v2.5M12 18.5V21M4.93 4.93l1.77 1.77M17.3 17.3l1.77 1.77M3 12h2.5M18.5 12H21M4.93 19.07l1.77-1.77M17.3 6.7l1.77-1.77M12 16a4 4 0 100-8 4 4 0 000 8z" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none">
                  <path d="M20 15.2A7.7 7.7 0 118.8 4 6.4 6.4 0 0020 15.2z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                </svg>
              </button>

              <div class="user-card">
                <div class="user-avatar">{{ userInitials }}</div>
                <div class="user-meta">
                  <strong>{{ username }}</strong>
                  <span>{{ theme === 'dark' ? 'Dark workspace' : 'Light workspace' }}</span>
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
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()
const theme = ref('light')
const THEME_STORAGE_KEY = 'ttapi-ui-theme'

const isAuthPage = computed(() => ['/login', '/register'].includes(route.path))
const currentProjectId = computed(() => String(route.params.projectId || ''))
const currentUsername = computed(() => localStorage.getItem('username') || '')
const currentUserId = computed(() => localStorage.getItem('userId') || '')
const username = computed(() => currentUsername.value || (currentUserId.value ? `用户 ${currentUserId.value}` : '未登录用户'))
const userInitials = computed(() => (username.value ? username.value.slice(0, 1).toUpperCase() : 'U'))

const workspaceLinks = [
  {
    to: '/',
    label: '项目仪表盘',
    matchPrefixes: ['/'],
    icon: `
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M4 13h7V4H4v9zm9 7h7V4h-7v16zM4 20h7v-5H4v5z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
      </svg>
    `,
  },
  {
    to: '/operations/overview',
    label: '运营总览',
    matchPrefixes: ['/operations/overview'],
    icon: `
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M4 18h16M7 14l3-3 3 2 4-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `,
  },
]

const projectLinks = computed(() => {
  if (!currentProjectId.value) return []
  const projectId = currentProjectId.value
  return [
    {
      to: `/project/${projectId}`,
      label: 'API 测试',
      matchPrefixes: [`/project/${projectId}`, `/project/${projectId}/runs/`],
      icon: `
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M8 7h11M8 12h11M8 17h11M4 7h.01M4 12h.01M4 17h.01" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
      `,
    },
    {
      to: `/project/${projectId}/web-test-cases`,
      label: 'Web 测试',
      matchPrefixes: [`/project/${projectId}/web-test-cases`, `/project/${projectId}/web-runs/`],
      icon: `
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M4 6.5A2.5 2.5 0 016.5 4h11A2.5 2.5 0 0120 6.5v7A2.5 2.5 0 0117.5 16h-11A2.5 2.5 0 014 13.5v-7zM8 20h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      `,
    },
    {
      to: `/project/${projectId}/executions`,
      label: '执行记录',
      matchPrefixes: [`/project/${projectId}/executions`],
      icon: `
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M6 6h12v12H6zM9 3v6M15 15h3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      `,
    },
    {
      to: `/project/${projectId}/reports`,
      label: '报告中心',
      matchPrefixes: [`/project/${projectId}/reports`],
      icon: `
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M6 18V9m6 9V5m6 13v-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
      `,
    },
    {
      to: `/project/${projectId}/batches`,
      label: '批次结果',
      matchPrefixes: [`/project/${projectId}/batches`],
      icon: `
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M5 7h14M5 12h14M5 17h9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
      `,
    },
    {
      to: `/project/${projectId}/environments`,
      label: '环境变量',
      matchPrefixes: [`/project/${projectId}/environments`],
      icon: `
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M8 5h8M12 5v14M7 12h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
      `,
    },
    {
      to: `/project/${projectId}/scheduling`,
      label: '调度编排',
      matchPrefixes: [`/project/${projectId}/scheduling`],
      icon: `
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M4 12h5l2-6 2 12 2-6h5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      `,
    },
    {
      to: `/project/${projectId}/integration-governance`,
      label: '集成治理',
      matchPrefixes: [`/project/${projectId}/integration-governance`],
      icon: `
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M12 4l7 4v8l-7 4-7-4V8l7-4zm0 4v8m4-6l-8 4" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/>
        </svg>
      `,
    },
  ]
})

const pageKicker = computed(() => {
  if (route.path.includes('/operations/overview')) return 'Workspace / Operations'
  if (route.path.includes('/reports')) return 'Project / Reports'
  if (route.path.includes('/executions')) return 'Project / Execution Center'
  if (route.path.includes('/web-test-cases')) return 'Project / Web Testing'
  if (route.path.includes('/scheduling')) return 'Project / Scheduling'
  if (route.path.includes('/integration-governance')) return 'Project / Governance'
  if (route.path.includes('/environments')) return 'Project / Environments'
  if (route.path.includes('/batches')) return 'Project / Batch Runs'
  if (route.path.startsWith('/project/')) return 'Project / API Testing'
  return 'Workspace / Dashboard'
})

const pageTitle = computed(() => {
  if (route.path.includes('/operations/overview')) return '运营总览'
  if (route.path.includes('/reports')) return '报告中心'
  if (route.path.includes('/executions')) return '执行中心'
  if (route.path.includes('/web-test-cases')) return 'Web 测试'
  if (route.path.includes('/scheduling')) return '调度编排'
  if (route.path.includes('/integration-governance')) return '集成治理'
  if (route.path.includes('/environments')) return '环境与变量'
  if (route.path.includes('/batches')) return '批次结果'
  if (route.path.startsWith('/project/')) return 'API 测试'
  return '项目仪表盘'
})

const pageSubtitle = computed(() => {
  if (route.path.includes('/operations/overview')) return '统一查看跨项目风险信号、重试积压与治理趋势'
  if (route.path.includes('/reports')) return '聚合 API 与 Web 结果，面向问题定位和质量判断'
  if (route.path.includes('/executions')) return '统一查看 API / Web 执行记录与失败状态'
  if (route.path.includes('/web-test-cases')) return '管理页面步骤、定位器与执行产物'
  if (route.path.includes('/scheduling')) return '查看队列、Worker 与调度执行状态'
  if (route.path.includes('/integration-governance')) return '处理通知、事件、缺陷与治理动作'
  if (route.path.includes('/environments')) return '集中管理环境、变量组和敏感变量'
  if (route.path.includes('/batches')) return '按批次追踪回归执行结果和明细'
  if (route.path.startsWith('/project/')) return '围绕当前项目管理用例、执行结果与测试资产'
  return '用更清晰的结构组织项目、功能分区和主要工作入口'
})

const isLinkActive = (to, matchPrefixes = []) => {
  if (to === '/' && route.path === '/') return true
  return matchPrefixes.some((prefix) => prefix !== '/' && route.path.startsWith(prefix))
}

const applyTheme = (value) => {
  document.documentElement.dataset.theme = value
  document.body.dataset.theme = value
  localStorage.setItem(THEME_STORAGE_KEY, value)
}

const toggleTheme = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
}

const handleLogout = () => {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('userId')
  localStorage.removeItem('username')
  router.push('/login')
}

onMounted(() => {
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY)
  theme.value = savedTheme === 'dark' ? 'dark' : 'light'
  applyTheme(theme.value)
})

watch(theme, (value) => {
  applyTheme(value)
})
</script>

<style>
:root,
:root[data-theme='light'] {
  --bg-page: linear-gradient(180deg, #f5f7fb 0%, #eef3f8 100%);
  --bg-accent: radial-gradient(circle at top left, rgba(49, 120, 102, 0.14), transparent 28%);
  --surface-shell: rgba(255, 255, 255, 0.72);
  --surface-card: rgba(255, 255, 255, 0.88);
  --surface-solid: #ffffff;
  --surface-muted: #f4f6f8;
  --surface-elevated: rgba(247, 250, 252, 0.92);
  --border-color: rgba(184, 194, 204, 0.72);
  --border-strong: rgba(160, 171, 184, 0.9);
  --text-strong: #17212b;
  --text-main: #30404e;
  --text-muted: #70808f;
  --primary: #246b5a;
  --primary-strong: #184c40;
  --primary-soft: rgba(36, 107, 90, 0.12);
  --accent: #b5742f;
  --accent-soft: rgba(181, 116, 47, 0.14);
  --danger: #c44e4e;
  --danger-soft: rgba(196, 78, 78, 0.12);
  --success: #1d8b6b;
  --success-soft: rgba(29, 139, 107, 0.14);
  --shadow-sm: 0 8px 20px rgba(15, 23, 42, 0.06);
  --shadow-md: 0 18px 48px rgba(15, 23, 42, 0.10);
  --radius-sm: 12px;
  --radius-md: 18px;
  --radius-lg: 26px;
}

:root[data-theme='dark'] {
  --bg-page: linear-gradient(180deg, #0d1319 0%, #121a22 100%);
  --bg-accent: radial-gradient(circle at top left, rgba(64, 149, 124, 0.18), transparent 24%);
  --surface-shell: rgba(17, 24, 32, 0.86);
  --surface-card: rgba(20, 28, 36, 0.90);
  --surface-solid: #131b23;
  --surface-muted: #18212b;
  --surface-elevated: rgba(27, 37, 48, 0.92);
  --border-color: rgba(79, 93, 107, 0.66);
  --border-strong: rgba(97, 114, 130, 0.95);
  --text-strong: #f1f5f9;
  --text-main: #d5dee8;
  --text-muted: #94a3b8;
  --primary: #5aa88d;
  --primary-strong: #8fd0bc;
  --primary-soft: rgba(90, 168, 141, 0.16);
  --accent: #d5a15d;
  --accent-soft: rgba(213, 161, 93, 0.16);
  --danger: #ea7b7b;
  --danger-soft: rgba(234, 123, 123, 0.18);
  --success: #61cfa4;
  --success-soft: rgba(97, 207, 164, 0.16);
  --shadow-sm: 0 10px 30px rgba(2, 6, 12, 0.34);
  --shadow-md: 0 22px 54px rgba(2, 6, 12, 0.42);
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
  font-family: 'IBM Plex Sans', 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
  background: var(--bg-accent), var(--bg-page);
  color: var(--text-main);
  transition: background 0.24s ease, color 0.24s ease;
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
  width: 286px;
  background: var(--surface-shell);
  backdrop-filter: blur(18px);
  border-right: 1px solid var(--border-color);
  padding: 22px 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: sticky;
  top: 0;
  height: 100vh;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 10px;
}

.brand-mark {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, var(--primary-strong), var(--primary));
  color: #fff;
  box-shadow: var(--shadow-sm);
}

.brand-mark svg {
  width: 24px;
  height: 24px;
}

.brand-copy {
  min-width: 0;
}

.brand-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-strong);
  letter-spacing: 0.02em;
}

.brand-subtitle {
  color: var(--text-muted);
  font-size: 12px;
  margin-top: 2px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar-label {
  padding: 0 12px;
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 46px;
  padding: 11px 14px;
  border-radius: 14px;
  text-decoration: none;
  color: var(--text-main);
  transition: background 0.18s ease, color 0.18s ease, transform 0.18s ease;
}

.nav-item:hover {
  background: var(--primary-soft);
  color: var(--primary-strong);
  transform: translateX(2px);
}

.nav-item.active {
  background: linear-gradient(135deg, var(--primary-soft), transparent);
  color: var(--text-strong);
  border: 1px solid rgba(36, 107, 90, 0.18);
}

.nav-icon {
  width: 18px;
  height: 18px;
  display: inline-flex;
  flex: none;
}

.nav-icon svg {
  width: 18px;
  height: 18px;
}

.project-zone {
  padding: 14px 0 0;
  border-top: 1px solid var(--border-color);
}

.project-chip {
  margin: 0 12px 4px;
  padding: 10px 12px;
  border-radius: 16px;
  background: var(--surface-card);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-main);
}

.project-chip-dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: var(--accent);
  box-shadow: 0 0 0 6px var(--accent-soft);
}

.sidebar-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.theme-toggle {
  width: 100%;
  border: 1px solid var(--border-color);
  background: var(--surface-card);
  color: var(--text-main);
  border-radius: 16px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.theme-toggle-track {
  width: 46px;
  height: 24px;
  border-radius: 999px;
  background: var(--surface-muted);
  border: 1px solid var(--border-color);
  padding: 2px;
  display: flex;
  align-items: center;
}

.theme-toggle-thumb {
  width: 18px;
  height: 18px;
  border-radius: 999px;
  background: var(--accent);
  transition: transform 0.2s ease, background 0.2s ease;
}

.theme-toggle-thumb.dark {
  transform: translateX(22px);
  background: var(--primary);
}

.sidebar-note {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 4px;
  color: var(--text-muted);
  font-size: 13px;
}

.sidebar-note-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--success);
  box-shadow: 0 0 0 5px var(--success-soft);
}

.shell-main {
  flex: 1;
  min-width: 0;
  padding: 18px 22px 24px;
}

.topbar {
  min-height: 96px;
  border-radius: 28px;
  padding: 22px 26px;
  background: var(--surface-card);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.page-kicker {
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.topbar-title {
  margin: 10px 0 6px;
  font-size: 32px;
  line-height: 1.08;
  color: var(--text-strong);
}

.topbar-subtitle {
  margin: 0;
  color: var(--text-muted);
  font-size: 14px;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.project-context {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 11px 14px;
  border-radius: 16px;
  background: var(--surface-elevated);
  border: 1px solid var(--border-color);
}

.project-context span {
  color: var(--text-muted);
  font-size: 12px;
}

.project-context strong {
  color: var(--text-strong);
}

.icon-theme-btn {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  border: 1px solid var(--border-color);
  background: var(--surface-elevated);
  color: var(--text-main);
  display: grid;
  place-items: center;
}

.icon-theme-btn svg {
  width: 20px;
  height: 20px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 18px;
  background: var(--surface-elevated);
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
  background: linear-gradient(135deg, var(--primary-strong), var(--primary));
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
  background: var(--surface-solid);
  color: var(--text-main);
  border-radius: 12px;
  padding: 10px 14px;
}

.page-container {
  padding-top: 20px;
}

:root[data-theme='dark'] .hero-card,
:root[data-theme='dark'] .panel-card,
:root[data-theme='dark'] .stat-card,
:root[data-theme='dark'] .modal-card,
:root[data-theme='dark'] .result-panel,
:root[data-theme='dark'] .result-mini-card,
:root[data-theme='dark'] .project-card,
:root[data-theme='dark'] .table-wrap {
  background: var(--surface-card) !important;
  border-color: var(--border-color) !important;
  box-shadow: var(--shadow-sm) !important;
}

:root[data-theme='dark'] .queue-table th,
:root[data-theme='dark'] .data-table th,
:root[data-theme='dark'] .report-table thead th,
:root[data-theme='dark'] .cases-table thead th {
  background: var(--surface-muted) !important;
  color: var(--text-muted) !important;
}

:root[data-theme='dark'] .search-box,
:root[data-theme='dark'] .inline-input,
:root[data-theme='dark'] .field-block input,
:root[data-theme='dark'] .field-block textarea,
:root[data-theme='dark'] .field-block select,
:root[data-theme='dark'] .project-meta,
:root[data-theme='dark'] .secondary-btn,
:root[data-theme='dark'] .icon-btn,
:root[data-theme='dark'] .ghost-btn,
:root[data-theme='dark'] .theme-toggle {
  background: var(--surface-muted) !important;
  color: var(--text-main) !important;
  border-color: var(--border-color) !important;
}

:root[data-theme='dark'] .state-block {
  border-color: var(--border-color) !important;
  color: var(--text-muted) !important;
}

:root[data-theme='dark'] .result-panel pre,
:root[data-theme='dark'] .payload-pre {
  background: var(--surface-muted) !important;
  color: var(--text-main) !important;
}

@media (max-width: 1180px) {
  .app-shell {
    flex-direction: column;
  }

  .sidebar {
    width: auto;
    height: auto;
    position: static;
    border-right: 0;
    border-bottom: 1px solid var(--border-color);
  }
}

@media (max-width: 860px) {
  .shell-main {
    padding: 14px;
  }

  .topbar {
    padding: 18px;
    border-radius: 22px;
    flex-direction: column;
    align-items: flex-start;
  }

  .topbar-title {
    font-size: 27px;
  }

  .topbar-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .user-card {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
