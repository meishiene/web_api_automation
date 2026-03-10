<template>
  <div class="project-list">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-title">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
          </svg>
          <h1>项目管理</h1>
        </div>
        <p class="header-description">创建和管理您的API测试项目</p>
      </div>
      <button @click="showCreateModal = true" class="create-btn">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        新建项目
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载项目...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="projects.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
        </svg>
      </div>
      <h3>还没有项目</h3>
      <p>创建您的第一个API测试项目，开始测试之旅</p>
      <button @click="showCreateModal = true" class="create-first-btn">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        创建第一个项目
      </button>
    </div>

    <!-- 项目网格 -->
    <div v-else class="projects-grid">
      <div
        v-for="project in projects"
        :key="project.id"
        class="project-card"
        @mouseenter="hoveredProject = project.id"
        @mouseleave="hoveredProject = null"
      >
        <div class="project-header">
          <div class="project-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
            </svg>
          </div>
          <div class="project-title">
            <h3>{{ project.name }}</h3>
            <span class="project-id">#{{ project.id }}</span>
          </div>
        </div>

        <div class="project-content">
          <p class="project-description">
            {{ project.description || '暂无项目描述' }}
          </p>
          <div class="project-meta">
            <div class="meta-item">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
              </svg>
              <span>{{ formatDate(project.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="project-actions">
          <router-link :to="`/project/${project.id}`" class="action-btn primary">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
            </svg>
            查看测试用例
          </router-link>
          <button @click="deleteProjectById(project.id)" class="action-btn danger">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 新建项目模态框 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>创建新项目</h2>
          <button @click="showCreateModal = false" class="close-btn">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>

        <form @submit.prevent="handleCreateProject" class="modal-form">
          <div class="form-group">
            <label for="project-name">项目名称 *</label>
            <div class="input-wrapper">
              <svg class="input-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
              </svg>
              <input
                id="project-name"
                v-model="newProject.name"
                type="text"
                placeholder="输入项目名称"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label for="project-description">项目描述</label>
            <div class="input-wrapper">
              <textarea
                id="project-description"
                v-model="newProject.description"
                placeholder="描述项目的用途和目标（可选）"
                rows="4"
              ></textarea>
            </div>
          </div>

          <div v-if="createError" class="error-message">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            {{ createError }}
          </div>

          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="cancel-btn">
              取消
            </button>
            <button type="submit" :disabled="creating" class="submit-btn">
              <span v-if="creating" class="loading-spinner"></span>
              <svg v-else viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
              </svg>
              {{ creating ? '创建中...' : '创建项目' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProjects, createProject, deleteProject } from '@/api/projects'

const projects = ref([])
const loading = ref(false)
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')
const hoveredProject = ref(null)

const newProject = ref({
  name: '',
  description: ''
})

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

const handleCreateProject = async () => {
  if (!newProject.value.name.trim()) {
    createError.value = '项目名称不能为空'
    return
  }

  creating.value = true
  createError.value = ''

  try {
    await createProject(newProject.value)
    showCreateModal.value = false
    newProject.value = { name: '', description: '' }
    await fetchProjects()
  } catch (err) {
    createError.value = err.response?.data?.detail || '创建失败'
  } finally {
    creating.value = false
  }
}

const deleteProjectById = async (id) => {
  if (!confirm('确定要删除这个项目吗？')) {
    return
  }

  try {
    await deleteProject(id)
    await fetchProjects()
  } catch (err) {
    alert('删除失败')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.project-list {
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 3rem;
  padding: 2rem 0;
  border-bottom: 1px solid var(--gray-200);
}

.header-content {
  flex: 1;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.header-title svg {
  width: 2.5rem;
  height: 2.5rem;
  color: var(--primary-color);
}

.header-title h1 {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--gray-900);
  margin: 0;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-description {
  color: var(--gray-600);
  font-size: 1.125rem;
  margin: 0;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, var(--success-color), #059669);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow);
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.create-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid var(--gray-200);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.loading-state p {
  color: var(--gray-600);
  font-size: 1.125rem;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, var(--gray-50), var(--gray-100));
  border-radius: var(--border-radius-lg);
  border: 2px dashed var(--gray-300);
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  color: var(--gray-400);
  margin-bottom: 1.5rem;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--gray-800);
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: var(--gray-600);
  font-size: 1rem;
  margin-bottom: 2rem;
  max-width: 400px;
}

.create-first-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow);
}

.create-first-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.create-first-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

/* 项目网格 */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 2rem;
}

.project-card {
  background: white;
  border-radius: var(--border-radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--gray-200);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.project-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-light);
}

.project-card:hover::before {
  opacity: 1;
}

/* 项目头部 */
.project-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.project-icon {
  width: 3rem;
  height: 3rem;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.project-icon svg {
  width: 1.5rem;
  height: 1.5rem;
}

.project-title {
  flex: 1;
  min-width: 0;
}

.project-title h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--gray-900);
  margin: 0 0 0.25rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.project-id {
  font-size: 0.875rem;
  color: var(--gray-500);
  font-weight: 500;
}

/* 项目内容 */
.project-content {
  margin-bottom: 2rem;
}

.project-description {
  color: var(--gray-600);
  line-height: 1.6;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: var(--gray-500);
}

.meta-item svg {
  width: 1rem;
  height: 1rem;
}

/* 项目操作 */
.project-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  font-size: 0.875rem;
  text-decoration: none;
  transition: all 0.2s ease;
  flex: 1;
  border: none;
  cursor: pointer;
}

.action-btn.primary {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: white;
  box-shadow: var(--shadow-sm);
}

.action-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}

.action-btn.danger {
  background: var(--gray-100);
  color: var(--gray-700);
  border: 1px solid var(--gray-300);
}

.action-btn.danger:hover {
  background: var(--error-color);
  color: white;
  border-color: var(--error-color);
}

.action-btn svg {
  width: 1rem;
  height: 1rem;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: white;
  border-radius: var(--border-radius-lg);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--gray-200);
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--gray-900);
  margin: 0;
}

.close-btn {
  width: 2rem;
  height: 2rem;
  background: none;
  border: none;
  color: var(--gray-400);
  cursor: pointer;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--gray-100);
  color: var(--gray-700);
}

.close-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

.modal-form {
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: var(--gray-700);
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.25rem;
  height: 1.25rem;
  color: var(--gray-400);
  z-index: 1;
}

.input-wrapper input,
.input-wrapper textarea {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  border: 2px solid var(--gray-200);
  border-radius: var(--border-radius);
  font-size: 1rem;
  background: var(--gray-50);
  transition: all 0.2s ease;
  outline: none;
  resize: vertical;
}

.input-wrapper input:focus,
.input-wrapper textarea:focus {
  border-color: var(--primary-color);
  background: white;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.input-wrapper textarea {
  min-height: 100px;
  padding-top: 0.875rem;
  padding-left: 1rem;
  line-height: 1.6;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--border-radius);
  color: var(--error-color);
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 1.5rem;
}

.error-message svg {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--gray-200);
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  background: var(--gray-100);
  color: var(--gray-700);
  border: 1px solid var(--gray-300);
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: var(--gray-200);
}

.submit-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.submit-btn .loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.submit-btn svg {
  width: 1rem;
  height: 1rem;
}

/* 动画 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1.5rem;
    align-items: stretch;
  }

  .header-title h1 {
    font-size: 2rem;
  }

  .projects-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .project-card {
    padding: 1.5rem;
  }

  .modal {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }

  .modal-header,
  .modal-form {
    padding: 1.5rem;
  }

  .project-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 1.5rem 0;
    margin-bottom: 2rem;
  }

  .header-title {
    flex-direction: column;
    text-align: center;
    gap: 0.75rem;
  }

  .header-title h1 {
    font-size: 1.75rem;
  }

  .create-btn,
  .create-first-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
