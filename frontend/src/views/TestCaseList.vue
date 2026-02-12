<template>
  <div class="test-case-list">
    <div class="page-header">
      <div>
        <button @click="$router.push('/')" class="back-btn">← 返回项目列表</button>
        <h1>{{ projectName }} - 测试用例</h1>
      </div>
      <button @click="showCreateModal = true" class="create-btn">新建测试用例</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="testCases.length === 0" class="empty">
      <p>暂无测试用例</p>
    </div>

    <table v-else class="test-table">
      <thead>
        <tr>
          <th>名称</th>
          <th>方法</th>
          <th>URL</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="tc in testCases" :key="tc.id">
          <td>{{ tc.name }}</td>
          <td>
            <span :class="'method-' + tc.method">{{ tc.method }}</span>
          </td>
          <td class="url">{{ tc.url }}</td>
          <td class="actions">
            <button @click="editTestCase(tc)" class="edit-btn">编辑</button>
            <button @click="runTestCase(tc)" class="run-btn">运行</button>
            <button @click="deleteTestCaseById(tc.id)" class="delete-btn">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 新建/编辑测试用例模态框 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal modal-large">
        <h2>{{ isEditing ? '编辑测试用例' : '新建测试用例' }}</h2>
        <form @submit.prevent="handleSaveTestCase">
          <div class="form-group">
            <label>用例名称</label>
            <input v-model="testCaseForm.name" type="text" placeholder="请输入用例名称" required />
          </div>
          <div class="form-group">
            <label>请求方法</label>
            <select v-model="testCaseForm.method">
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
            </select>
          </div>
          <div class="form-group">
            <label>请求 URL</label>
            <input v-model="testCaseForm.url" type="text" placeholder="https://api.example.com/endpoint" required />
          </div>
          <div class="form-group">
            <label>请求头 (JSON)</label>
            <textarea v-model="testCaseForm.headers" rows="3" placeholder='{"Authorization": "Bearer token"}'></textarea>
          </div>
          <div class="form-group">
            <label>请求体 (JSON)</label>
            <textarea v-model="testCaseForm.body" rows="5" placeholder='{"key": "value"}'></textarea>
          </div>
          <div class="form-group">
            <label>期望状态码</label>
            <input v-model="testCaseForm.expected_status" type="number" placeholder="200" required />
          </div>
          <div class="form-group">
            <label>期望响应体 (JSON)</label>
            <textarea v-model="testCaseForm.expected_body" rows="4" placeholder='{"status": "ok"}'></textarea>
          </div>
          <p v-if="formError" class="error">{{ formError }}</p>
          <div class="modal-actions">
            <button type="button" @click="closeModal">取消</button>
            <button type="submit" :disabled="saving">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 测试结果模态框 -->
    <div v-if="showResultModal" class="modal-overlay" @click.self="showResultModal = false">
      <div class="modal modal-large">
        <h2>测试结果</h2>
        <div class="result-content">
          <div :class="'status-badge ' + (testResult?.status === 'passed' ? 'success' : 'failed')">
            {{ testResult?.status === 'passed' ? '通过' : '失败' }}
          </div>
          <div class="result-section">
            <h3>响应状态码</h3>
            <p>{{ testResult?.actual_status }}</p>
          </div>
          <div class="result-section">
            <h3>响应时间</h3>
            <p>{{ testResult?.duration_ms }} ms</p>
          </div>
          <div class="result-section">
            <h3>响应头</h3>
            <pre>无</pre>
          </div>
          <div class="result-section">
            <h3>响应体</h3>
            <pre>{{ formatJson(testResult?.actual_body) }}</pre>
          </div>
          <div v-if="testResult?.error_message" class="result-section">
            <h3>错误信息</h3>
            <pre class="error-text">{{ testResult.error_message }}</pre>
          </div>
        </div>
        <div class="modal-actions">
          <button type="button" @click="showResultModal = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  getTestCases,
  createTestCase,
  updateTestCase,
  deleteTestCase as deleteTestCaseApi,
  runTestCase as runTestCaseApi,
  getTestResult
} from '@/api/testCases'
import { getProjects } from '@/api/projects'

const route = useRoute()
const projectId = computed(() => parseInt(route.params.projectId))

const testCases = ref([])
const loading = ref(false)
const showCreateModal = ref(false)
const showResultModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const formError = ref('')
const testResult = ref(null)

const testCaseForm = ref({
  name: '',
  method: 'GET',
  url: '',
  headers: '{}',
  body: '{}',
  expected_status: 200,
  expected_body: '{}'
})

const projectName = ref('项目')

const fetchProjectName = async () => {
  try {
    const list = await getProjects()
    const project = list.find(p => p.id === projectId.value)
    if (project) {
      projectName.value = project.name
    }
  } catch (err) {
    console.error('Failed to fetch project name')
  }
}

const fetchTestCases = async () => {
  loading.value = true
  try {
    testCases.value = await getTestCases(projectId.value)
  } catch (err) {
    alert('获取测试用例失败')
  } finally {
    loading.value = false
  }
}

const handleSaveTestCase = async () => {
  try {
    const data = {
      name: testCaseForm.value.name,
      method: testCaseForm.value.method,
      url: testCaseForm.value.url,
      headers: testCaseForm.value.headers || '{}',
      body: testCaseForm.value.body || '{}',
      expected_status: parseInt(testCaseForm.value.expected_status) || 200,
      expected_body: testCaseForm.value.expected_body || '{}'
    }

    saving.value = true
    formError.value = ''

    if (isEditing.value) {
      await updateTestCase(projectId.value, testCaseForm.value.id, data)
    } else {
      await createTestCase(projectId.value, data)
    }

    closeModal()
    await fetchTestCases()
  } catch (err) {
    if (err instanceof SyntaxError) {
      formError.value = 'JSON 格式错误，请检查输入'
    } else {
      formError.value = err.response?.data?.detail || '保存失败'
    }
  } finally {
    saving.value = false
  }
}

const editTestCase = (tc) => {
  isEditing.value = true
  testCaseForm.value = {
    id: tc.id,
    name: tc.name,
    method: tc.method,
    url: tc.url,
    headers: JSON.stringify(tc.headers, null, 2),
    body: JSON.stringify(tc.body, null, 2),
    expected_status: tc.expected_status || 200,
    expected_body: JSON.stringify(tc.expected_body || {}, null, 2)
  }
  showCreateModal.value = true
}

const deleteTestCaseById = async (id) => {
  if (!confirm('确定要删除这个测试用例吗？')) {
    return
  }

  try {
    await deleteTestCaseApi(projectId.value, id)
    await fetchTestCases()
  } catch (err) {
    alert('删除失败')
  }
}

const runTestCase = async (tc) => {
  try {
    const result = await runTestCaseApi(projectId.value, tc.id)
    testResult.value = result
    showResultModal.value = true
  } catch (err) {
    alert('运行测试失败')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  isEditing.value = false
  testCaseForm.value = {
    name: '',
    method: 'GET',
    url: '',
    headers: '{}',
    body: '{}',
    expected_status: 200,
    expected_body: '{}'
  }
  formError.value = ''
}

const formatJson = (data) => {
  if (!data) return ''
  if (typeof data === 'string') {
    try {
      return JSON.stringify(JSON.parse(data), null, 2)
    } catch {
      return data
    }
  }
  return JSON.stringify(data, null, 2)
}

onMounted(() => {
  fetchProjectName()
  fetchTestCases()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0.5rem 0 0 0;
}

.back-btn {
  padding: 0.5rem 1rem;
  background: #666;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.back-btn:hover {
  background: #555;
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

.test-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.test-table th,
.test-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.test-table th {
  background: #f5f5f5;
  font-weight: 600;
}

.url {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #666;
}

.method-GET { color: #61affe; font-weight: 600; }
.method-POST { color: #49cc90; font-weight: 600; }
.method-PUT { color: #fca130; font-weight: 600; }
.method-DELETE { color: #f93e3e; font-weight: 600; }

.actions {
  display: flex;
  gap: 0.5rem;
}

.actions button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.edit-btn {
  background: #2196F3;
  color: white;
}

.edit-btn:hover { background: #1976D2; }

.run-btn {
  background: #9C27B0;
  color: white;
}

.run-btn:hover { background: #7B1FA2; }

.delete-btn {
  background: #f44336;
  color: white;
}

.delete-btn:hover { background: #d32f2f; }

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
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-large {
  max-width: 700px;
}

.modal h2 {
  margin: 0 0 1.5rem 0;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  font-family: 'Courier New', monospace;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.modal-actions button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal-actions button[type="button"] {
  background: #ccc;
  color: white;
}

.modal-actions button[type="submit"] {
  background: #4CAF50;
  color: white;
}

.modal-actions button[type="submit"]:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.result-content {
  margin-bottom: 1.5rem;
}

.status-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
  margin-bottom: 1rem;
}

.status-badge.success {
  background: #d4edda;
  color: #155724;
}

.status-badge.failed {
  background: #f8d7da;
  color: #721c24;
}

.result-section {
  margin-bottom: 1.5rem;
}

.result-section h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: #666;
}

.result-section pre {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0;
}

.error-text {
  color: #f44336;
}

.loading,
.empty {
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
