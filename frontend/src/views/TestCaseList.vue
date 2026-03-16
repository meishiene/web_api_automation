<template>
  <section class="cases-page">
    <div class="hero-card">
      <div>
        <router-link to="/" class="back-link">← 返回项目列表</router-link>
        <span class="eyebrow">Project</span>
        <h2>{{ projectName }}</h2>
        <p>维护测试用例、执行接口验证，并查看最近一次执行结果。</p>
      </div>
      <button @click="openCreateModal" class="primary-btn">
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        新建用例
      </button>
    </div>

    <div class="stats-grid">
      <article class="stat-card">
        <span>用例总数</span>
        <strong>{{ filteredTestCases.length }}</strong>
        <small>当前项目下的接口测试配置</small>
      </article>
      <article class="stat-card accent">
        <span>GET / POST 数量</span>
        <strong>{{ getCount }} / {{ postCount }}</strong>
        <small>常用方法快速统计</small>
      </article>
      <article class="stat-card soft">
        <span>最近执行</span>
        <strong>{{ lastRunStatus }}</strong>
        <small>{{ lastRunTime }}</small>
      </article>
    </div>

    <section class="panel-card">
      <div class="panel-head">
        <div>
          <h3>测试用例列表</h3>
          <p>按方法、URL 和断言配置管理接口测试。</p>
        </div>
        <div class="panel-tools">
          <button class="secondary-btn" @click="goToUnifiedRuns">统一执行结果</button>
          <button class="secondary-btn" @click="goToWebTestCases">Web 用例管理</button>
          <button class="secondary-btn" @click="goToEnvironmentManager">环境变量治理</button>
          <button class="secondary-btn" @click="goToSchedulingDashboard">Scheduling</button>
          <button class="secondary-btn" @click="goToBatchRuns">查看批次结果</button>
          <button class="secondary-btn" @click="handleExportCases">导出 JSON</button>
          <button class="secondary-btn" @click="handleImportCases">导入 JSON</button>
          <div class="search-box">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M21 21l-4.35-4.35M10.8 18a7.2 7.2 0 100-14.4 7.2 7.2 0 000 14.4z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
            <input v-model.trim="keyword" @keyup.enter="applyFilters" placeholder="关键词（名称/URL）" />
          </div>
          <input class="inline-input" v-model.trim="caseGroupFilter" @keyup.enter="applyFilters" placeholder="分组" />
          <input class="inline-input" v-model.trim="tagFilter" @keyup.enter="applyFilters" placeholder="标签" />
          <button class="secondary-btn" @click="applyFilters">筛选</button>
          <button class="secondary-btn" @click="resetFilters">重置</button>
        </div>
      </div>

      <div v-if="loading" class="state-block">
        <div class="spinner"></div>
        <p>正在加载测试用例...</p>
      </div>

      <div v-else-if="filteredTestCases.length === 0" class="state-block empty">
        <div class="empty-icon">API</div>
        <h4>{{ hasAnyFilter ? '没有匹配到用例' : '还没有测试用例' }}</h4>
        <p>{{ hasAnyFilter ? '试试其他筛选条件，或者新建一个测试用例。' : '先创建一个用例，再进行接口执行。' }}</p>
        <button @click="openCreateModal" class="primary-btn">立即创建</button>
      </div>

      <div v-else class="table-wrap">
        <table class="cases-table">
          <thead>
            <tr>
              <th>名称</th>
              <th>方法</th>
              <th>URL</th>
              <th>期望状态</th>
              <th>分组</th>
              <th>标签</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tc in filteredTestCases" :key="tc.id">
              <td>
                <div class="name-cell">
                  <strong>{{ tc.name }}</strong>
                  <span>#{{ tc.id }}</span>
                </div>
              </td>
              <td>
                <span class="method-pill" :class="`method-${tc.method}`">{{ tc.method }}</span>
              </td>
              <td>
                <div class="url-cell" :title="tc.url">{{ tc.url }}</div>
              </td>
              <td>
                <span class="status-code">{{ tc.expected_status }}</span>
              </td>
              <td>{{ tc.case_group || '--' }}</td>
              <td>{{ (tc.tags && tc.tags.length) ? tc.tags.join(', ') : '--' }}</td>
              <td>{{ formatDate(tc.updated_at || tc.created_at) }}</td>
              <td>
                <div class="row-actions">
                  <button class="table-btn subtle" @click="runTestCase(tc)">运行</button>
                  <button class="table-btn edit" @click="copyCase(tc)">复制</button>
                  <button class="table-btn edit" @click="editTestCase(tc)">编辑</button>
                  <button class="table-btn danger" @click="deleteTestCaseById(tc.id)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="showCreateModal" class="modal-mask" @click.self="closeModal">
      <div class="modal-card modal-wide">
        <div class="modal-head">
          <div>
            <h3>{{ isEditing ? '编辑测试用例' : '创建测试用例' }}</h3>
            <p>支持配置请求参数、请求体和基础断言。</p>
          </div>
          <button @click="closeModal" class="icon-btn">✕</button>
        </div>

        <form @submit.prevent="handleSaveTestCase" class="modal-form grid-form">
          <label class="field-block">
            <span>用例名称</span>
            <input v-model="testCaseForm.name" type="text" placeholder="例如：获取用户详情" />
          </label>

          <label class="field-block">
            <span>请求方法</span>
            <select v-model="testCaseForm.method">
              <option>GET</option>
              <option>POST</option>
              <option>PUT</option>
              <option>PATCH</option>
              <option>DELETE</option>
            </select>
          </label>

          <label class="field-block full-row">
            <span>请求 URL</span>
            <input v-model="testCaseForm.url" type="text" placeholder="https://api.example.com/users/1" />
          </label>

          <label class="field-block">
            <span>分组</span>
            <input v-model="testCaseForm.case_group" type="text" placeholder="例如：smoke" />
          </label>

          <label class="field-block">
            <span>标签（逗号分隔）</span>
            <input v-model="testCaseForm.tags" type="text" placeholder="auth, login" />
          </label>

          <label class="field-block">
            <span>请求头 Headers</span>
            <textarea v-model="testCaseForm.headers" rows="8" placeholder='例如：{"Authorization":"Bearer xxx"}'></textarea>
          </label>

          <label class="field-block">
            <span>请求体 Body</span>
            <textarea v-model="testCaseForm.body" rows="8" placeholder='例如：{"name":"Tom"}'></textarea>
          </label>

          <label class="field-block">
            <span>期望状态码</span>
            <input v-model="testCaseForm.expected_status" type="number" min="100" max="599" />
          </label>

          <label class="field-block full-row">
            <span>期望响应体</span>
            <textarea v-model="testCaseForm.expected_body" rows="8" placeholder='可填 JSON 或纯文本，例如：{"success":true}'></textarea>
          </label>

          <p v-if="formError" class="form-error full-row">{{ formError }}</p>

          <div class="modal-actions full-row">
            <button type="button" class="secondary-btn" @click="closeModal">取消</button>
            <button type="submit" class="primary-btn" :disabled="saving">
              {{ saving ? '保存中...' : (isEditing ? '保存修改' : '创建用例') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showResultModal && testResult" class="modal-mask" @click.self="showResultModal = false">
      <div class="modal-card modal-result">
        <div class="modal-head">
          <div>
            <h3>执行结果</h3>
            <p>展示本次接口执行的返回状态、耗时和响应内容。</p>
          </div>
          <div class="result-head-actions">
            <button class="secondary-btn" @click="openRunDetail" :disabled="!testResult?.id">查看执行详情</button>
            <button @click="showResultModal = false" class="icon-btn">✕</button>
          </div>
        </div>

        <div class="result-summary">
          <span class="result-badge" :class="testResult.status">{{ testResult.status }}</span>
          <div class="result-mini-card">
            <span>响应状态</span>
            <strong>{{ testResult.actual_status ?? '--' }}</strong>
          </div>
          <div class="result-mini-card">
            <span>耗时</span>
            <strong>{{ testResult.duration_ms }} ms</strong>
          </div>
        </div>

        <div class="result-grid">
          <section class="result-panel">
            <h4>响应体</h4>
            <pre>{{ formatJson(testResult.actual_body) || '无响应体' }}</pre>
          </section>

          <section class="result-panel" v-if="testResult.error_message">
            <h4>错误信息</h4>
            <pre class="error-pre">{{ testResult.error_message }}</pre>
          </section>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getTestCases,
  createTestCase,
  copyTestCase as copyTestCaseApi,
  updateTestCase,
  deleteTestCase as deleteTestCaseApi,
  runTestCase as runTestCaseApi,
  exportTestCases,
  importTestCases
} from '@/api/testCases'
import { getProjects } from '@/api/projects'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => parseInt(route.params.projectId, 10))

const testCases = ref([])
const loading = ref(false)
const showCreateModal = ref(false)
const showResultModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const formError = ref('')
const testResult = ref(null)
const keyword = ref('')
const caseGroupFilter = ref('')
const tagFilter = ref('')

const defaultForm = () => ({
  name: '',
  method: 'GET',
  url: '',
  headers: '{}',
  body: '{}',
  expected_status: 200,
  expected_body: '{}',
  case_group: '',
  tags: ''
})

const testCaseForm = ref(defaultForm())
const projectName = ref('项目')
const lastRunAt = ref(null)

const filteredTestCases = computed(() => testCases.value)
const hasAnyFilter = computed(() => !!(keyword.value || caseGroupFilter.value || tagFilter.value))

const getCount = computed(() => filteredTestCases.value.filter(tc => tc.method === 'GET').length)
const postCount = computed(() => filteredTestCases.value.filter(tc => tc.method === 'POST').length)
const lastRunStatus = computed(() => testResult.value?.status || '--')
const lastRunTime = computed(() => lastRunAt.value ? formatDate(lastRunAt.value) : '暂无执行记录')

const normalizeTimestamp = (value) => {
  if (!value) return 0
  const numeric = Number(value)
  return numeric > 1e12 ? numeric : numeric * 1000
}

const formatDate = (value) => {
  if (!value) return '--'
  return new Date(normalizeTimestamp(value)).toLocaleString('zh-CN')
}

const editorValue = (value, fallback = '{}') => {
  if (value === null || value === undefined || value === '') return fallback
  return typeof value === 'string' ? value : JSON.stringify(value, null, 2)
}

const fetchProjectName = async () => {
  try {
    const list = await getProjects()
    const project = list.find(item => item.id === projectId.value)
    if (project) projectName.value = project.name
  } catch (err) {
    console.error('Failed to fetch project name')
  }
}

const fetchTestCases = async () => {
  loading.value = true
  try {
    testCases.value = await getTestCases(projectId.value, {
      keyword: keyword.value || undefined,
      case_group: caseGroupFilter.value || undefined,
      tag: tagFilter.value || undefined,
    })
  } catch (err) {
    alert('获取测试用例失败')
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEditing.value = false
  formError.value = ''
  testCaseForm.value = defaultForm()
  showCreateModal.value = true
}

const handleSaveTestCase = async () => {
  if (!testCaseForm.value.name.trim() || !testCaseForm.value.url.trim()) {
    formError.value = '请先填写用例名称和请求 URL'
    return
  }

  try {
    saving.value = true
    formError.value = ''

    const data = {
      name: testCaseForm.value.name,
      method: testCaseForm.value.method,
      url: testCaseForm.value.url,
      headers: testCaseForm.value.headers || '{}',
      body: testCaseForm.value.body || '{}',
      expected_status: parseInt(testCaseForm.value.expected_status, 10) || 200,
      expected_body: testCaseForm.value.expected_body || '{}',
      case_group: testCaseForm.value.case_group?.trim() || null,
      tags: (testCaseForm.value.tags || '')
        .split(',')
        .map(item => item.trim())
        .filter(Boolean)
    }

    if (isEditing.value) {
      await updateTestCase(projectId.value, testCaseForm.value.id, data)
    } else {
      await createTestCase(projectId.value, data)
    }

    closeModal()
    await fetchTestCases()
  } catch (err) {
    formError.value = err.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

const editTestCase = (tc) => {
  isEditing.value = true
  formError.value = ''
  testCaseForm.value = {
    id: tc.id,
    name: tc.name,
    method: tc.method,
    url: tc.url,
    headers: editorValue(tc.headers),
    body: editorValue(tc.body),
    expected_status: tc.expected_status || 200,
    expected_body: editorValue(tc.expected_body),
    case_group: tc.case_group || '',
    tags: Array.isArray(tc.tags) ? tc.tags.join(', ') : ''
  }
  showCreateModal.value = true
}

const deleteTestCaseById = async (id) => {
  if (!confirm('确定要删除这个测试用例吗？')) return

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
    lastRunAt.value = Date.now()
    showResultModal.value = true
  } catch (err) {
    alert('运行测试失败')
  }
}
const copyCase = async (tc) => {
  const customName = prompt('请输入复制后的用例名称（可留空自动生成）', `${tc.name}-copy`)
  if (customName === null) return

  try {
    await copyTestCaseApi(projectId.value, tc.id, { name: customName.trim() || undefined })
    await fetchTestCases()
  } catch (err) {
    alert(err.response?.data?.detail || '复制失败')
  }
}

const handleExportCases = async () => {
  try {
    const payload = await exportTestCases(projectId.value)
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `test-cases-project-${projectId.value}.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    alert('导出失败')
  }
}

const handleImportCases = async () => {
  const raw = prompt('请粘贴导入 JSON（结构需包含 cases 数组）')
  if (!raw) return

  try {
    const parsed = JSON.parse(raw)
    const result = await importTestCases(projectId.value, {
      cases: parsed.cases || [],
      skip_duplicates: true,
    })
    alert(`导入完成：成功 ${result.imported}，跳过 ${result.skipped}`)
    await fetchTestCases()
  } catch (err) {
    alert(err.response?.data?.detail || '导入失败，请检查 JSON 格式')
  }
}

const applyFilters = () => {
  fetchTestCases()
}

const resetFilters = () => {
  keyword.value = ''
  caseGroupFilter.value = ''
  tagFilter.value = ''
  fetchTestCases()
}

const goToBatchRuns = () => {
  router.push(`/project/${projectId.value}/batches`)
}

const goToUnifiedRuns = () => {
  router.push(`/project/${projectId.value}/executions`)
}

const goToWebTestCases = () => {
  router.push(`/project/${projectId.value}/web-test-cases`)
}

const goToEnvironmentManager = () => {
  router.push(`/project/${projectId.value}/environments`)

const goToSchedulingDashboard = () => {
  router.push(`/project/${projectId.value}/scheduling`)
}
}

const openRunDetail = () => {
  if (!testResult.value?.id) return
  showResultModal.value = false
  router.push(`/project/${projectId.value}/runs/${testResult.value.id}`)
}

const closeModal = () => {
  showCreateModal.value = false
  isEditing.value = false
  formError.value = ''
  testCaseForm.value = defaultForm()
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
.cases-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero-card,
.panel-card,
.stat-card,
.modal-card,
.result-panel,
.result-mini-card {
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

.back-link {
  display: inline-block;
  margin-bottom: 10px;
  color: var(--text-muted);
  text-decoration: none;
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
.modal-head h3,
.result-panel h4 {
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

.inline-input {
  min-width: 120px;
  height: 48px;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 0 12px;
  background: var(--bg-card-soft);
  color: var(--text-main);
}

.search-box {
  min-width: 320px;
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

.table-wrap {
  overflow: auto;
  border: 1px solid var(--border-color);
  border-radius: 22px;
  background: #fff;
}

.cases-table {
  width: 100%;
  min-width: 920px;
  border-collapse: collapse;
}

.cases-table th,
.cases-table td {
  padding: 18px 20px;
  text-align: left;
  border-bottom: 1px solid #edf2f1;
}

.cases-table thead th {
  background: #f8fbfb;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 700;
}

.cases-table tbody tr:hover {
  background: rgba(18, 179, 165, 0.04);
}

.name-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.name-cell strong {
  color: var(--text-strong);
}

.name-cell span {
  color: var(--text-muted);
  font-size: 12px;
}

.method-pill,
.status-code,
.result-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  font-weight: 700;
}

.method-pill {
  min-width: 74px;
  padding: 8px 12px;
  font-size: 12px;
}

.method-GET { background: #e6f2ff; color: #2b6cb0; }
.method-POST { background: #e4fbf3; color: #0f8f6b; }
.method-PUT { background: #fff3df; color: #b7791f; }
.method-PATCH { background: #efe8ff; color: #6b46c1; }
.method-DELETE { background: #ffe7e7; color: #d44a4a; }

.url-cell {
  max-width: 360px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-main);
}

.status-code {
  padding: 8px 12px;
  background: var(--primary-soft);
  color: var(--primary-dark);
}

.row-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.table-btn,
.primary-btn,
.secondary-btn,
.result-head-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.icon-btn {
  border: 0;
}

.table-btn,
.primary-btn,
.secondary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-radius: 14px;
  padding: 11px 16px;
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

.secondary-btn {
  background: #f4f7f7;
  color: var(--text-main);
  border: 1px solid var(--border-color);
}

.table-btn.subtle {
  background: var(--primary-soft);
  color: var(--primary-dark);
}

.table-btn.edit {
  background: #eef2ff;
  color: #4c63d2;
}

.table-btn.danger {
  background: var(--danger-soft);
  color: #d44a4a;
}

.state-block {
  min-height: 300px;
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
  font-weight: 800;
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
  width: min(1120px, 100%);
  border-radius: 24px;
  padding: 24px;
  background: #fff;
}

.modal-wide {
  max-height: 92vh;
  overflow: auto;
}

.modal-result {
  width: min(920px, 100%);
}

.modal-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.result-head-actions {
  display: flex;
  align-items: center;
  gap: 10px;
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

.grid-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.full-row {
  grid-column: 1 / -1;
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
.field-block textarea,
.field-block select {
  width: 100%;
  border: 1px solid var(--border-color);
  background: var(--bg-card-soft);
  border-radius: 16px;
  padding: 14px 16px;
  outline: none;
  color: var(--text-main);
}

.field-block textarea {
  resize: vertical;
  min-height: 140px;
  font-family: 'JetBrains Mono', 'Consolas', monospace;
}

.field-block input:focus,
.field-block textarea:focus,
.field-block select:focus {
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

.result-summary {
  display: flex;
  align-items: stretch;
  gap: 14px;
  margin-bottom: 18px;
}

.result-badge {
  min-width: 120px;
  padding: 14px 18px;
  font-size: 15px;
  text-transform: capitalize;
}

.result-badge.success {
  background: #e4fbf3;
  color: #0f8f6b;
}

.result-badge.failed,
.result-badge.error {
  background: #ffe7e7;
  color: #d44a4a;
}

.result-mini-card {
  border-radius: 18px;
  padding: 14px 16px;
  min-width: 150px;
}

.result-mini-card span {
  display: block;
  color: var(--text-muted);
  font-size: 13px;
}

.result-mini-card strong {
  display: block;
  margin-top: 6px;
  color: var(--text-strong);
  font-size: 22px;
}

.result-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.result-panel {
  border-radius: 20px;
  padding: 18px;
}

.result-panel h4 {
  margin-top: 0;
}

.result-panel pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  background: #f8fbfb;
  border-radius: 16px;
  padding: 16px;
  color: var(--text-main);
  line-height: 1.65;
  overflow: auto;
}

.error-pre {
  color: #b42318;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 980px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .hero-card,
  .panel-head,
  .result-summary {
    flex-direction: column;
    align-items: flex-start;
  }

  .inline-input {
  min-width: 120px;
  height: 48px;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 0 12px;
  background: var(--bg-card-soft);
  color: var(--text-main);
}

.search-box {
    min-width: 0;
    width: 100%;
  }

  .grid-form {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .panel-card,
  .hero-card,
  .modal-card {
    padding: 18px;
    border-radius: 20px;
  }

  .modal-actions,
  .row-actions {
    flex-direction: column;
    width: 100%;
  }

  .table-btn,
  .primary-btn,
  .secondary-btn {
    width: 100%;
  }
}
</style>
