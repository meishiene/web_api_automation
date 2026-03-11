<template>
  <section class="dashboard-page">
    <div class="hero-card">
      <div>
        <span class="eyebrow">Workspace</span>
        <h2>项目总览</h2>
        <p>用更清晰的方式管理 API 测试项目，快速进入用例维护与执行。</p>
      </div>
      <button @click="showCreateModal = true" class="primary-btn">
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        新建项目
      </button>
    </div>

    <div class="stats-grid">
      <article class="stat-card">
        <span>项目总数</span>
        <strong>{{ projects.length }}</strong>
        <small>当前账号下的全部项目</small>
      </article>
      <article class="stat-card accent">
        <span>最近创建</span>
        <strong>{{ latestProjectName }}</strong>
        <small>{{ latestProjectTime }}</small>
      </article>
      <article class="stat-card soft">
        <span>当前状态</span>
        <strong>Ready</strong>
        <small>可继续创建、查看和删除项目</small>
      </article>
    </div>

    <section class="panel-card">
      <div class="panel-head">
        <div>
          <h3>项目列表</h3>
          <p>点击项目即可进入测试用例管理页面。</p>
        </div>
        <div class="panel-tools">
          <div class="search-box">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M21 21l-4.35-4.35M10.8 18a7.2 7.2 0 100-14.4 7.2 7.2 0 000 14.4z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
            <input v-model.trim="keyword" placeholder="搜索项目名称..." />
          </div>
        </div>
      </div>

      <div v-if="loading" class="state-block">
        <div class="spinner"></div>
        <p>正在加载项目列表...</p>
      </div>

      <div v-else-if="filteredProjects.length === 0" class="state-block empty">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M4 7.5A2.5 2.5 0 016.5 5h3l1.4 1.5H17.5A2.5 2.5 0 0120 9v8.5a2.5 2.5 0 01-2.5 2.5h-11A2.5 2.5 0 014 17.5v-10z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
          </svg>
        </div>
        <h4>{{ keyword ? '没有匹配到项目' : '还没有项目' }}</h4>
        <p>{{ keyword ? '换个关键词试试，或创建一个新项目。' : '创建你的第一个 API 测试项目吧。' }}</p>
        <button @click="showCreateModal = true" class="primary-btn">立即创建</button>
      </div>

      <div v-else class="project-grid">
        <article v-for="project in filteredProjects" :key="project.id" class="project-card">
          <div class="project-card-head">
            <div class="project-badge">{{ project.name.slice(0, 1).toUpperCase() }}</div>
            <div class="project-title-wrap">
              <h4>{{ project.name }}</h4>
              <span>#{{ project.id }}</span>
            </div>
          </div>

          <p class="project-desc">{{ project.description || '暂无项目描述，建议补充接口范围或业务模块说明。' }}</p>

          <div class="project-meta">
            <span>创建时间</span>
            <strong>{{ formatDate(project.created_at) }}</strong>
          </div>

          <div class="project-actions">
            <router-link :to="`/project/${project.id}`" class="link-btn primary-link">进入项目</router-link>
            <button @click="deleteProjectById(project.id)" class="link-btn danger-link">删除</button>
          </div>
        </article>
      </div>
    </section>

    <div v-if="showCreateModal" class="modal-mask" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-head">
          <div>
            <h3>创建新项目</h3>
            <p>用于归类接口测试用例，建议按系统或业务域命名。</p>
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
            <textarea v-model="newProject.description" rows="4" placeholder="填写接口用途、测试范围或环境说明"></textarea>
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
import { getProjects, createProject, deleteProject } from '@/api/projects'

const projects = ref([])
const loading = ref(false)
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')
const keyword = ref('')

const newProject = ref({
  name: '',
  description: ''
})

const filteredProjects = computed(() => {
  if (!keyword.value) return projects.value
  return projects.value.filter(project =>
    project.name?.toLowerCase().includes(keyword.value.toLowerCase()) ||
    project.description?.toLowerCase().includes(keyword.value.toLowerCase())
  )
})

const latestProject = computed(() => {
  if (!projects.value.length) return null
  return [...projects.value].sort((a, b) => normalizeTimestamp(b.created_at) - normalizeTimestamp(a.created_at))[0]
})

const latestProjectName = computed(() => latestProject.value?.name || '--')
const latestProjectTime = computed(() => latestProject.value ? formatDate(latestProject.value.created_at) : '暂无数据')

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

onMounted(fetchProjects)
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero-card,
.panel-card,
.stat-card,
.modal-card {
  background: rgba(255, 255, 255, 0.84);
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
  background: linear-gradient(135deg, rgba(234, 248, 246, 0.95), rgba(244, 249, 249, 0.95));
}

.eyebrow {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--primary-soft);
  color: var(--primary-dark);
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
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.stat-card {
  border-radius: var(--radius-md);
  padding: 22px;
}

.stat-card span {
  color: var(--text-muted);
  font-size: 13px;
}

.stat-card strong {
  display: block;
  margin-top: 10px;
  color: var(--text-strong);
  font-size: 34px;
  line-height: 1;
}

.stat-card small {
  display: block;
  margin-top: 10px;
  color: var(--text-muted);
}

.stat-card.accent {
  background: linear-gradient(135deg, rgba(18, 179, 165, 0.14), rgba(255, 255, 255, 0.88));
}

.stat-card.soft {
  background: linear-gradient(135deg, rgba(91, 124, 255, 0.08), rgba(255, 255, 255, 0.88));
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
  margin-bottom: 22px;
}

.panel-tools {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box {
  min-width: 300px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  background: var(--bg-card-soft);
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
  height: 48px;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
}

.project-card {
  border: 1px solid var(--border-color);
  border-radius: 22px;
  padding: 22px;
  background: #fff;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.project-card-head {
  display: flex;
  align-items: center;
  gap: 14px;
}

.project-badge {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, rgba(18, 179, 165, 0.18), rgba(18, 179, 165, 0.06));
  color: var(--primary-dark);
  font-size: 18px;
  font-weight: 800;
}

.project-title-wrap h4 {
  margin: 0;
  color: var(--text-strong);
  font-size: 18px;
}

.project-title-wrap span {
  color: var(--text-muted);
  font-size: 13px;
}

.project-desc {
  min-height: 68px;
  margin: 18px 0;
  color: var(--text-main);
  line-height: 1.7;
}

.project-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-radius: 16px;
  background: var(--bg-card-soft);
  color: var(--text-muted);
}

.project-meta strong {
  color: var(--text-main);
  font-size: 13px;
}

.project-actions {
  display: flex;
  gap: 12px;
  margin-top: 18px;
}

.link-btn,
.primary-btn,
.secondary-btn,
.icon-btn {
  border: 0;
  text-decoration: none;
}

.link-btn,
.primary-btn,
.secondary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-radius: 14px;
  padding: 12px 18px;
  font-weight: 700;
}

.primary-btn {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: #fff;
  box-shadow: 0 12px 24px rgba(18, 179, 165, 0.22);
}

.primary-btn svg {
  width: 18px;
  height: 18px;
}

.secondary-btn,
.primary-link {
  background: var(--primary-soft);
  color: var(--primary-dark);
}

.danger-link {
  background: var(--danger-soft);
  color: #d44a4a;
}

.state-block {
  min-height: 280px;
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
  color: var(--primary-dark);
}

.empty-icon svg {
  width: 30px;
  height: 30px;
}

.spinner {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 3px solid rgba(18, 179, 165, 0.2);
  border-top-color: var(--primary);
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.36);
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
  background: #fff;
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
  background: var(--bg-card-soft);
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
  background: var(--bg-card-soft);
  border-radius: 16px;
  padding: 14px 16px;
  outline: none;
  color: var(--text-main);
}

.field-block input:focus,
.field-block textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(18, 179, 165, 0.12);
}

.form-error {
  margin: 0;
  color: #d44a4a;
  background: var(--danger-soft);
  padding: 12px 14px;
  border-radius: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.secondary-btn {
  background: #f4f7f7;
  color: var(--text-main);
  border: 1px solid var(--border-color);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 900px) {
  .stats-grid {
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

  .project-actions,
  .modal-actions {
    flex-direction: column;
  }

  .link-btn,
  .primary-btn,
  .secondary-btn {
    width: 100%;
  }
}
</style>
