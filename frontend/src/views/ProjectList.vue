<template>
  <section class="workspace-page">
    <div class="hero-card">
      <div>
        <span class="eyebrow">Workspace Dashboard</span>
        <h2>项目仪表盘</h2>
        <p>把项目、功能分区和主要入口放回一个更清晰的工作台里。</p>
      </div>
      <div class="hero-actions">
        <button class="secondary-btn" @click="goToOperationsOverview">运营总览</button>
        <button class="primary-btn" @click="showCreateModal = true">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          新建项目
        </button>
      </div>
    </div>

    <div class="stats-grid">
      <article class="stat-card">
        <span>项目总数</span>
        <strong>{{ projects.length }}</strong>
        <small>当前账号下已接入的平台项目</small>
      </article>
      <article class="stat-card accent">
        <span>最近创建</span>
        <strong>{{ latestProjectName }}</strong>
        <small>{{ latestProjectTime }}</small>
      </article>
      <article class="stat-card soft">
        <span>最近 7 天新增</span>
        <strong>{{ recentProjectCount }}</strong>
        <small>帮助快速判断近期活跃度</small>
      </article>
      <article class="stat-card warm">
        <span>当前筛选结果</span>
        <strong>{{ filteredProjects.length }}</strong>
        <small>配合搜索快速定位目标项目</small>
      </article>
    </div>

    <section class="panel-card">
      <div class="panel-head">
        <div>
          <h3>功能分区</h3>
          <p>围绕项目生命周期组织入口，降低在页面之间来回寻找的成本。</p>
        </div>
      </div>

      <div class="area-grid">
        <article class="area-card">
          <span class="area-tag">Assets</span>
          <h4>项目与资产</h4>
          <p>集中管理项目、环境变量和项目归属，是所有测试资产的入口。</p>
          <button class="area-link" @click="showCreateModal = true">新建项目</button>
        </article>

        <article class="area-card">
          <span class="area-tag">API</span>
          <h4>API 测试</h4>
          <p>从用例、套件、批次到执行详情，适合日常接口回归与问题定位。</p>
          <button class="area-link" @click="openLatestProjectRoute('api')">打开最近项目</button>
        </article>

        <article class="area-card">
          <span class="area-tag">Web</span>
          <h4>Web 自动化</h4>
          <p>聚焦页面步骤、执行产物和失败定位，补强当前 Web 模块体验。</p>
          <button class="area-link" @click="openLatestProjectRoute('web')">打开最近项目</button>
        </article>

        <article class="area-card">
          <span class="area-tag">Ops</span>
          <h4>报告与治理</h4>
          <p>查看运营总览、执行结果、报告和治理信号，把问题暴露在更前面。</p>
          <button class="area-link" @click="goToOperationsOverview">进入总览</button>
        </article>
      </div>
    </section>

    <section class="panel-card">
      <div class="panel-head">
        <div>
          <h3>项目列表</h3>
          <p>保留列表视图，支持快速浏览、搜索和按功能区跳转。</p>
        </div>

        <div class="panel-tools">
          <div class="search-box">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M21 21l-4.35-4.35M10.8 18a7.2 7.2 0 100-14.4 7.2 7.2 0 000 14.4z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
            <input v-model.trim="keyword" placeholder="搜索项目名称或描述..." />
          </div>
        </div>
      </div>

      <div v-if="loading" class="state-block">
        <div class="spinner"></div>
        <p>正在加载项目列表...</p>
      </div>

      <div v-else-if="filteredProjects.length === 0" class="state-block empty">
        <div class="empty-icon">WS</div>
        <h4>{{ keyword ? '没有匹配到项目' : '还没有项目' }}</h4>
        <p>{{ keyword ? '试试换个关键词，或创建一个新项目。' : '先创建一个项目，再进入 API 或 Web 测试工作区。' }}</p>
        <button @click="showCreateModal = true" class="primary-btn">立即创建</button>
      </div>

      <div v-else class="table-wrap">
        <table class="project-table">
          <thead>
            <tr>
              <th>项目</th>
              <th>描述</th>
              <th>创建时间</th>
              <th>快速入口</th>
              <th>管理</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="project in filteredProjects" :key="project.id">
              <td>
                <div class="project-cell">
                  <div class="project-badge">{{ project.name.slice(0, 1).toUpperCase() }}</div>
                  <div>
                    <strong>{{ project.name }}</strong>
                    <small>#{{ project.id }}</small>
                  </div>
                </div>
              </td>
              <td class="desc-cell">{{ project.description || '暂无项目描述，建议补充测试范围和模块边界。' }}</td>
              <td>{{ formatDate(project.created_at) }}</td>
              <td>
                <div class="quick-links">
                  <button class="quick-btn" @click="openProject(project.id)">API</button>
                  <button class="quick-btn" @click="openProjectWeb(project.id)">Web</button>
                  <button class="quick-btn" @click="openProjectReports(project.id)">报告</button>
                </div>
              </td>
              <td>
                <div class="row-actions">
                  <button class="primary-link" @click="openProject(project.id)">进入</button>
                  <button class="danger-link" @click="deleteProjectById(project.id)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="showCreateModal" class="modal-mask" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-head">
          <div>
            <h3>创建新项目</h3>
            <p>建议按系统、业务域或测试边界命名，便于后续功能分区使用。</p>
          </div>
          <button @click="closeModal" class="icon-btn">✕</button>
        </div>

        <form @submit.prevent="handleCreateProject" class="modal-form">
          <label class="field-block">
            <span>项目名称</span>
            <input v-model="newProject.name" type="text" placeholder="例如：用户中心接口" />
          </label>

          <label class="field-block">
            <span>项目描述</span>
            <textarea v-model="newProject.description" rows="4" placeholder="填写测试范围、业务模块或环境说明"></textarea>
          </label>

          <p v-if="createError" class="form-error">{{ createError }}</p>

          <div class="modal-actions">
            <button type="button" class="secondary-btn" @click="closeModal">取消</button>
            <button type="submit" class="primary-btn" :disabled="creating">
              {{ creating ? '创建中...' : '创建项目' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getProjects, createProject, deleteProject } from '@/api/projects'

const router = useRouter()
const projects = ref([])
const loading = ref(false)
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')
const keyword = ref('')

const newProject = ref({
  name: '',
  description: '',
})

const filteredProjects = computed(() => {
  if (!keyword.value) return projects.value
  return projects.value.filter((project) => {
    const name = project.name?.toLowerCase() || ''
    const description = project.description?.toLowerCase() || ''
    const query = keyword.value.toLowerCase()
    return name.includes(query) || description.includes(query)
  })
})

const latestProject = computed(() => {
  if (!projects.value.length) return null
  return [...projects.value].sort((a, b) => normalizeTimestamp(b.created_at) - normalizeTimestamp(a.created_at))[0]
})

const latestProjectName = computed(() => latestProject.value?.name || '--')
const latestProjectTime = computed(() => (latestProject.value ? formatDate(latestProject.value.created_at) : '暂无数据'))
const recentProjectCount = computed(() => {
  const now = Date.now()
  return projects.value.filter((project) => now - normalizeTimestamp(project.created_at) <= 7 * 24 * 3600 * 1000).length
})

const normalizeTimestamp = (value) => {
  if (!value) return 0
  const numeric = Number(value)
  return numeric > 1e12 ? numeric : numeric * 1000
}

const formatDate = (value) => {
  if (!value) return '--'
  return new Date(normalizeTimestamp(value)).toLocaleString('zh-CN')
}

const fetchProjects = async () => {
  loading.value = true
  try {
    projects.value = await getProjects()
  } catch (err) {
    alert('获取项目列表失败')
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  showCreateModal.value = false
  creating.value = false
  createError.value = ''
  newProject.value = { name: '', description: '' }
}

const handleCreateProject = async () => {
  if (!newProject.value.name.trim()) {
    createError.value = '项目名称不能为空'
    return
  }

  creating.value = true
  createError.value = ''

  try {
    await createProject(newProject.value)
    closeModal()
    await fetchProjects()
  } catch (err) {
    createError.value = err.response?.data?.detail || '创建失败'
  } finally {
    creating.value = false
  }
}

const deleteProjectById = async (id) => {
  if (!confirm('确定要删除这个项目吗？')) return

  try {
    await deleteProject(id)
    await fetchProjects()
  } catch (err) {
    alert('删除失败')
  }
}

const openProject = (projectId) => {
  router.push(`/project/${projectId}`)
}

const openProjectWeb = (projectId) => {
  router.push(`/project/${projectId}/web-test-cases`)
}

const openProjectReports = (projectId) => {
  router.push(`/project/${projectId}/reports`)
}

const openLatestProjectRoute = (type) => {
  if (!latestProject.value) {
    showCreateModal.value = true
    return
  }
  if (type === 'web') {
    openProjectWeb(latestProject.value.id)
    return
  }
  openProject(latestProject.value.id)
}

const goToOperationsOverview = () => {
  router.push('/operations/overview')
}

onMounted(fetchProjects)
</script>

<style scoped>
.workspace-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero-card,
.panel-card,
.stat-card,
.modal-card,
.area-card {
  background: var(--surface-card);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}

.hero-card {
  border-radius: var(--radius-lg);
  padding: 28px 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border-radius: 999px;
  background: var(--primary-soft);
  color: var(--primary-strong);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-card h2,
.panel-head h3,
.modal-head h3 {
  margin: 12px 0 8px;
  color: var(--text-strong);
}

.hero-card p,
.panel-head p,
.modal-head p {
  margin: 0;
  color: var(--text-muted);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  border-radius: var(--radius-md);
  padding: 20px;
}

.stat-card span {
  color: var(--text-muted);
  font-size: 13px;
}

.stat-card strong {
  display: block;
  margin-top: 10px;
  color: var(--text-strong);
  font-size: 32px;
  line-height: 1.05;
}

.stat-card small {
  display: block;
  margin-top: 10px;
  color: var(--text-muted);
  line-height: 1.5;
}

.stat-card.accent {
  background: linear-gradient(135deg, var(--primary-soft), transparent);
}

.stat-card.soft {
  background: linear-gradient(135deg, rgba(91, 124, 255, 0.10), transparent);
}

.stat-card.warm {
  background: linear-gradient(135deg, var(--accent-soft), transparent);
}

.panel-card {
  border-radius: var(--radius-lg);
  padding: 24px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.panel-tools {
  display: flex;
  align-items: center;
  gap: 12px;
}

.area-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.area-card {
  border-radius: 22px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.area-tag {
  display: inline-flex;
  align-self: flex-start;
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--surface-muted);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.area-card h4 {
  margin: 0;
  color: var(--text-strong);
  font-size: 18px;
}

.area-card p {
  margin: 0;
  color: var(--text-main);
  line-height: 1.7;
  min-height: 74px;
}

.area-link {
  align-self: flex-start;
  border: 0;
  background: transparent;
  color: var(--primary-strong);
  font-weight: 700;
  padding: 0;
}

.search-box {
  min-width: 320px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  background: var(--surface-muted);
  border: 1px solid var(--border-color);
  border-radius: 16px;
}

.search-box svg {
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}

.search-box input {
  width: 100%;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--text-main);
  height: 46px;
}

.table-wrap {
  overflow: auto;
  border: 1px solid var(--border-color);
  border-radius: 22px;
  background: var(--surface-solid);
}

.project-table {
  width: 100%;
  min-width: 980px;
  border-collapse: collapse;
}

.project-table th,
.project-table td {
  padding: 18px 20px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.project-table th {
  background: var(--surface-muted);
  color: var(--text-muted);
  font-size: 13px;
}

.project-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-cell strong {
  display: block;
  color: var(--text-strong);
}

.project-cell small {
  color: var(--text-muted);
}

.project-badge {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, var(--primary-soft), transparent);
  color: var(--primary-strong);
  font-weight: 800;
}

.desc-cell {
  max-width: 360px;
  color: var(--text-main);
  line-height: 1.6;
}

.quick-links,
.row-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-btn,
.primary-btn,
.secondary-btn,
.primary-link,
.danger-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 42px;
  border-radius: 14px;
  padding: 0 16px;
  font-weight: 700;
}

.quick-btn {
  border: 1px solid var(--border-color);
  background: var(--surface-muted);
  color: var(--text-main);
}

.primary-btn {
  border: 0;
  background: linear-gradient(135deg, var(--primary), var(--primary-strong));
  color: #fff;
  box-shadow: 0 12px 24px rgba(36, 107, 90, 0.22);
}

.primary-btn svg {
  width: 18px;
  height: 18px;
}

.secondary-btn {
  border: 1px solid var(--border-color);
  background: var(--surface-muted);
  color: var(--text-main);
}

.primary-link {
  border: 0;
  background: var(--primary-soft);
  color: var(--primary-strong);
}

.danger-link {
  border: 0;
  background: var(--danger-soft);
  color: var(--danger);
}

.state-block {
  min-height: 240px;
  border: 1px dashed var(--border-strong);
  border-radius: 22px;
  display: grid;
  place-items: center;
  text-align: center;
  color: var(--text-muted);
  padding: 32px;
}

.empty-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto 12px;
  display: grid;
  place-items: center;
  border-radius: 22px;
  background: var(--primary-soft);
  color: var(--primary-strong);
  font-weight: 800;
}

.spinner {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 3px solid rgba(36, 107, 90, 0.16);
  border-top-color: var(--primary);
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(9, 15, 22, 0.38);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 999;
}

.modal-card {
  width: min(560px, 100%);
  border-radius: 24px;
  padding: 24px;
  background: var(--surface-solid);
}

.modal-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.icon-btn {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--surface-muted);
  color: var(--text-main);
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-block span {
  color: var(--text-main);
  font-weight: 600;
}

.field-block input,
.field-block textarea {
  width: 100%;
  border: 1px solid var(--border-color);
  background: var(--surface-muted);
  border-radius: 16px;
  padding: 14px 16px;
  outline: none;
  color: var(--text-main);
}

.field-block input:focus,
.field-block textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(36, 107, 90, 0.10);
}

.form-error {
  margin: 0;
  color: var(--danger);
  background: var(--danger-soft);
  padding: 12px 14px;
  border-radius: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1180px) {
  .stats-grid,
  .area-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .stats-grid,
  .area-grid {
    grid-template-columns: 1fr;
  }

  .hero-card,
  .panel-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-box {
    min-width: 0;
    width: 100%;
  }
}

@media (max-width: 640px) {
  .panel-card,
  .hero-card,
  .modal-card {
    padding: 18px;
    border-radius: 20px;
  }

  .hero-actions,
  .modal-actions,
  .row-actions {
    flex-direction: column;
    width: 100%;
  }

  .primary-btn,
  .secondary-btn,
  .danger-link {
    width: 100%;
  }
}
</style>
