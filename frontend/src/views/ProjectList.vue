<template>
  <div class="project-list">
    <div class="page-header">
      <h1>项目列表</h1>
      <button @click="showCreateModal = true" class="create-btn">新建项目</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="projects.length === 0" class="empty">
      <p>暂无项目</p>
    </div>

    <div v-else class="projects-grid">
      <div v-for="project in projects" :key="project.id" class="project-card">
        <h3>{{ project.name }}</h3>
        <p class="description">{{ project.description || '暂无描述' }}</p>
        <div class="project-info">
          <span>创建时间: {{ formatDate(project.created_at) }}</span>
        </div>
        <div class="project-actions">
          <router-link :to="`/project/${project.id}`" class="view-btn">查看测试用例</router-link>
          <button @click="deleteProjectById(project.id)" class="delete-btn">删除</button>
        </div>
      </div>
    </div>

    <!-- 新建项目模态框 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <h2>新建项目</h2>
        <form @submit.prevent="handleCreateProject">
          <div class="form-group">
            <label>项目名称</label>
            <input
              v-model="newProject.name"
              type="text"
              placeholder="请输入项目名称"
              required
            />
          </div>
          <div class="form-group">
            <label>项目描述</label>
            <textarea
              v-model="newProject.description"
              placeholder="请输入项目描述"
              rows="3"
            ></textarea>
          </div>
          <p v-if="createError" class="error">{{ createError }}</p>
          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false">取消</button>
            <button type="submit" :disabled="creating">
              {{ creating ? '创建中...' : '创建' }}
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
  margin: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.create-btn {
  padding: 0.75rem 1.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.create-btn:hover {
  background: #45a049;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.project-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.project-card h3 {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
}

.description {
  color: #666;
  margin-bottom: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.project-info {
  font-size: 0.875rem;
  color: #888;
  margin-bottom: 1rem;
}

.project-actions {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  padding: 0.5rem 1rem;
  background: #2196F3;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  flex: 1;
  text-align: center;
}

.view-btn:hover {
  background: #1976D2;
}

.delete-btn {
  padding: 0.5rem 1rem;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.delete-btn:hover {
  background: #d32f2f;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}

.modal h2 {
  margin: 0 0 1.5rem 0;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
}

textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  resize: vertical;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.modal-actions button[type="button"] {
  padding: 0.75rem 1.5rem;
  background: #ccc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal-actions button[type="submit"] {
  padding: 0.75rem 1.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal-actions button[type="submit"]:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading, .empty {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error {
  color: #f44336;
  margin: 0.5rem 0;
  font-size: 0.875rem;
}
</style>
