<template>
  <section class="api-test-page">
    <div class="api-shell">
      <aside class="api-tree">
        <div class="tree-toolbar">
          <button class="primary-btn full-width" @click="startNewCase">+ 新建接口</button>
          <div class="tree-tools">
            <button class="ghost-btn" @click="openImportModal('json')">导入</button>
            <button class="ghost-btn" @click="handleExportCases">导出</button>
          </div>
        </div>

        <div class="tree-search">
          <input v-model.trim="keyword" @keyup.enter="applyFilters" placeholder="搜索名称或 URL" />
        </div>

        <div class="tree-filters">
          <input v-model.trim="caseGroupFilter" @keyup.enter="applyFilters" placeholder="分组" />
          <input v-model.trim="tagFilter" @keyup.enter="applyFilters" placeholder="标签" />
          <div class="filter-actions">
            <button class="ghost-btn" @click="applyFilters">筛选</button>
            <button class="ghost-btn" @click="resetFilters">重置</button>
          </div>
        </div>

        <div v-if="loading" class="tree-empty">正在加载接口资产...</div>
        <div v-else-if="groupedCaseEntries.length === 0" class="tree-empty">
          {{ hasAnyFilter ? '没有匹配到接口资产' : '当前项目还没有接口用例' }}
        </div>
        <div v-else class="tree-content">
          <section v-for="group in groupedCaseEntries" :key="group.name" class="tree-group">
            <button class="tree-group-head" @click="toggleGroup(group.name)">
              <span class="tree-toggle">{{ expandedGroups[group.name] ? '⌄' : '›' }}</span>
              <span class="tree-folder">📁</span>
              <span class="tree-group-name">{{ group.name }}</span>
            </button>

            <div v-if="expandedGroups[group.name]" class="tree-group-list">
              <button
                v-for="item in group.items"
                :key="item.id"
                class="tree-item"
                :class="{ active: selectedCaseId === item.id }"
                @click="selectCase(item)"
              >
                <span class="method-badge" :class="`method-${item.method}`">{{ item.method }}</span>
                <span class="tree-item-name">{{ item.name }}</span>
              </button>
            </div>
          </section>
        </div>
      </aside>

      <div class="api-main">
        <section class="editor-card">
          <div class="editor-head">
            <h3>{{ selectedCase ? selectedCase.name : '接口测试' }}</h3>
            <div class="editor-actions">
              <button class="ghost-btn" @click="copyCurrentCase" :disabled="!selectedCase">复制</button>
              <button class="ghost-btn" @click="deleteCurrentCase" :disabled="!selectedCase">删除</button>
              <button class="ghost-btn" @click="saveCurrentCase" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
              <button class="success-btn" @click="runCurrentCase" :disabled="running || !selectedCaseId">
                {{ running ? '执行中...' : '执行测试' }}
              </button>
            </div>
          </div>

          <div class="project-switch">
            <label class="field-block narrow">
              <span>当前项目</span>
              <select v-model="selectedProjectId" @change="handleProjectChange">
                <option v-for="project in projects" :key="project.id" :value="String(project.id)">
                  {{ project.name }}
                </option>
              </select>
            </label>
            <div class="project-hint">{{ projectName }}</div>
          </div>

          <div class="page-links">
            <button class="ghost-btn small" @click="router.push(`/project/${projectId}/executions`)">执行中心</button>
            <button class="ghost-btn small" @click="router.push(`/project/${projectId}/reports`)">测试报告</button>
            <button class="ghost-btn small" @click="router.push(`/project/${projectId}/environments`)">环境治理</button>
            <button class="ghost-btn small" @click="router.push(`/project/${projectId}/scheduling`)">任务管理</button>
            <button class="ghost-btn small" @click="router.push(`/project/${projectId}/integration-governance`)">集成治理</button>
            <button class="ghost-btn small" @click="router.push(`/project/${projectId}/batches`)">批次结果</button>
          </div>

          <div class="suite-workbench">
            <div class="suite-main">
              <label class="field-block">
                <span>当前套件</span>
                <select v-model="selectedSuiteId" @change="handleSelectedSuiteChange">
                  <option value="">选择或创建套件</option>
                  <option v-for="suite in suites" :key="suite.id" :value="String(suite.id)">
                    {{ suite.name }}（{{ suite.case_count }}）
                  </option>
                </select>
              </label>
              <label class="field-block narrow">
                <span>执行环境</span>
                <select v-model="suiteEnvironmentId">
                  <option value="">默认环境</option>
                  <option v-for="environment in projectEnvironments" :key="environment.id" :value="String(environment.id)">
                    {{ environment.name }}
                  </option>
                </select>
              </label>
            </div>

            <div class="suite-actions">
              <button class="ghost-btn small" @click="openSuiteModal()">新建套件</button>
              <button class="ghost-btn small" @click="openSuiteModal(selectedSuite)" :disabled="!selectedSuite">编辑套件</button>
              <button class="ghost-btn small" @click="attachCurrentCaseToSuite" :disabled="!selectedSuite || !selectedCase">加入当前用例</button>
              <button class="ghost-btn small" @click="removeCurrentCaseFromSuite" :disabled="!selectedSuite || !selectedCaseInSuite">移出当前用例</button>
              <button class="ghost-btn small" @click="deleteCurrentSuite" :disabled="!selectedSuite">删除套件</button>
              <button class="success-btn small" @click="runCurrentSuite" :disabled="!selectedSuite || suiteRunning">{{ suiteRunning ? '执行中...' : '执行套件' }}</button>
            </div>
          </div>

          <div v-if="selectedSuite" class="suite-case-strip">
            <span class="suite-label">套件用例</span>
            <div class="suite-chip-list">
              <button
                v-for="item in suiteCases"
                :key="item.id"
                class="suite-chip"
                :class="{ active: selectedCaseId === item.test_case_id }"
                @click="selectCaseById(item.test_case_id)"
              >
                <span>{{ item.order_index }}</span>
                <strong>{{ item.test_case_name || `Case #${item.test_case_id}` }}</strong>
              </button>
            </div>
          </div>

          <div class="form-grid">
            <label class="field-block">
              <span>用例名称</span>
              <input v-model="testCaseForm.name" type="text" placeholder="例如：用户登录" />
            </label>

            <label class="field-block narrow">
              <span>请求方法</span>
              <select v-model="testCaseForm.method">
                <option>GET</option>
                <option>POST</option>
                <option>PUT</option>
                <option>DELETE</option>
                <option>PATCH</option>
              </select>
            </label>

            <label class="field-block full-row">
              <span>请求URL</span>
              <input v-model="testCaseForm.url" type="text" placeholder="https://api.example.com/api/user/login" />
            </label>

            <label class="field-block">
              <span>分组</span>
              <input v-model="testCaseForm.case_group" type="text" placeholder="例如：用户模块" />
            </label>

            <label class="field-block">
              <span>标签（逗号分隔）</span>
              <input v-model="testCaseForm.tags" type="text" placeholder="auth, login" />
            </label>

            <label class="field-block">
              <span>期望状态码</span>
              <input v-model="testCaseForm.expected_status" type="number" min="100" max="599" />
            </label>
          </div>
        </section>

        <section class="panel-card">
          <div class="tab-strip">
            <button v-for="tab in mainTabs" :key="tab.value" class="tab-btn" :class="{ active: activeTab === tab.value }" @click="activeTab = tab.value">
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-panel" v-if="activeTab === 'params'">
            <div class="kv-head">
              <span>KEY</span>
              <span>VALUE</span>
              <span>操作</span>
            </div>
            <div class="kv-row">
              <input v-model="paramsDraft.key" placeholder="参数名" />
              <input v-model="paramsDraft.value" placeholder="参数值" />
              <button class="ghost-btn small" @click="clearParamsDraft">删除</button>
            </div>
            <button class="table-link" @click="appendQueryParam">+ 添加参数到 URL</button>
          </div>

          <div class="tab-panel" v-else-if="activeTab === 'headers'">
            <label class="field-block">
              <span>请求头 Headers</span>
              <textarea v-model="testCaseForm.headers" rows="7" placeholder='例如：{"Authorization":"Bearer xxx"}'></textarea>
            </label>
          </div>

          <div class="tab-panel" v-else-if="activeTab === 'body'">
            <label class="field-block">
              <span>请求体 Body</span>
              <textarea v-model="testCaseForm.body" rows="9" placeholder='例如：{"username":"testuser","password":"123456"}'></textarea>
            </label>
          </div>

          <div class="tab-panel" v-else-if="activeTab === 'assertions'">
            <label class="field-block">
              <span>断言规则 Assertion Rules</span>
              <textarea v-model="testCaseForm.assertion_rules" rows="9" placeholder='例如：[{"type":"jsonpath","expression":"$.code","expected":0}]'></textarea>
            </label>
          </div>

          <div class="tab-panel" v-else-if="activeTab === 'extraction'">
            <label class="field-block">
              <span>提取规则 Extraction Rules</span>
              <textarea v-model="testCaseForm.extraction_rules" rows="9" placeholder='例如：[{"name":"token","expression":"$.data.token"}]'></textarea>
            </label>
          </div>

          <div class="tab-panel" v-else>
            <label class="field-block">
              <span>期望响应体 Expected Body</span>
              <textarea v-model="testCaseForm.expected_body" rows="9" placeholder='可填 JSON 或纯文本，例如：{"success":true}'></textarea>
            </label>
          </div>
        </section>

        <section class="panel-card response-card">
          <div class="response-head">
            <h3>响应结果</h3>
            <div class="response-meta" v-if="selectedResult">
              <span class="status-chip" :class="selectedResult.status">{{ selectedResult.status }}</span>
              <span>{{ selectedResult.duration_ms ?? '--' }} ms</span>
            </div>
          </div>

          <div v-if="selectedResult" class="response-body">
            <pre>{{ formatJson(selectedResult.actual_body) || '无响应体' }}</pre>
            <div v-if="selectedResult.error_message" class="error-box">{{ selectedResult.error_message }}</div>
            <button class="table-link" @click="openRunDetail" :disabled="!selectedResult.id">查看执行详情</button>
          </div>
          <div v-else class="response-empty">
            点击“执行测试”按钮查看响应结果
          </div>
        </section>
      </div>
    </div>

    <div v-if="showImportModal" class="modal-mask" @click.self="closeImportModal">
      <div class="modal-card">
        <div class="modal-head">
          <div>
            <h3>导入接口</h3>
            <p>将已有用例集或 OpenAPI 规范导入当前项目。</p>
          </div>
          <button class="close-btn" @click="closeImportModal">✕</button>
        </div>

        <div class="tab-strip import-strip">
          <button v-for="tab in importTabs" :key="tab.value" class="tab-btn" :class="{ active: importMode === tab.value }" @click="importMode = tab.value">
            {{ tab.label }}
          </button>
        </div>

        <div class="tab-panel" v-if="importMode === 'json'">
          <label class="field-block">
            <span>JSON 内容</span>
            <textarea v-model="importJsonText" rows="14" placeholder='导入结构需包含 cases 数组，例如：{"cases":[{"name":"case-a","method":"GET","url":"https://example.com"}]}'></textarea>
          </label>
        </div>

        <div class="tab-panel" v-else>
          <div v-if="importMode === 'openapi'">
            <div class="form-grid">
              <label class="field-block">
                <span>Base URL（可选）</span>
                <input v-model="openApiBaseUrl" type="text" placeholder="https://api.example.com" />
              </label>
              <label class="field-block">
                <span>导入分组（可选）</span>
                <input v-model="openApiCaseGroup" type="text" placeholder="例如：openapi-import" />
              </label>
              <label class="field-block full-row">
                <span>标签（逗号分隔）</span>
                <input v-model="openApiTags" type="text" placeholder="imported, openapi" />
              </label>
            </div>
            <label class="field-block">
              <span>OpenAPI Spec</span>
              <textarea v-model="openApiSpecText" rows="12" placeholder='请粘贴 OpenAPI 3.x JSON 规范，例如：{"openapi":"3.0.3","paths":{...}}'></textarea>
            </label>
          </div>

          <div v-else>
            <div class="form-grid">
              <label class="field-block">
                <span>导入分组（可选）</span>
                <input v-model="postmanCaseGroup" type="text" placeholder="例如：postman-import" />
              </label>
              <label class="field-block">
                <span>标签（逗号分隔）</span>
                <input v-model="postmanTags" type="text" placeholder="imported, postman" />
              </label>
            </div>
            <label class="field-block">
              <span>Postman Collection</span>
              <textarea v-model="postmanCollectionText" rows="12" placeholder='请粘贴 Postman Collection v2.x JSON'></textarea>
            </label>
          </div>
        </div>

        <p v-if="importError" class="form-error">{{ importError }}</p>

        <div class="modal-actions">
          <button class="ghost-btn" @click="closeImportModal">取消</button>
          <button class="primary-btn" :disabled="importing" @click="submitImport">{{ importing ? '导入中...' : '开始导入' }}</button>
        </div>
      </div>
    </div>

    <div v-if="showSuiteModal" class="modal-mask" @click.self="closeSuiteModal">
      <div class="modal-card">
        <div class="modal-head">
          <div>
            <h3>{{ editingSuiteId ? '编辑套件' : '新建套件' }}</h3>
            <p>按业务流或回归批次管理 API 用例集合。</p>
          </div>
          <button class="close-btn" @click="closeSuiteModal">×</button>
        </div>

        <div class="modal-form">
          <label class="field-block">
            <span>套件名称</span>
            <input v-model.trim="suiteForm.name" type="text" placeholder="例如：用户认证回归" />
          </label>
          <label class="field-block">
            <span>套件描述</span>
            <textarea v-model.trim="suiteForm.description" rows="4" placeholder="描述这个套件覆盖的业务范围"></textarea>
          </label>
          <p v-if="suiteFormError" class="form-error">{{ suiteFormError }}</p>
          <div class="modal-actions">
            <button class="ghost-btn" @click="closeSuiteModal">取消</button>
            <button class="primary-btn" @click="submitSuite" :disabled="suiteSaving">{{ suiteSaving ? '保存中...' : editingSuiteId ? '保存修改' : '创建套件' }}</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProjectEnvironments } from '@/api/environments'
import { getProjects } from '@/api/projects'
import {
  copyTestCase as copyTestCaseApi,
  createTestCase,
  deleteTestCase as deleteTestCaseApi,
  exportTestCases,
  importTestCasesByProvider,
  getTestCases,
  importOpenApiTestCases,
  importTestCases,
  runTestCase as runTestCaseApi,
  updateTestCase,
} from '@/api/testCases'
import { createTestSuite, deleteTestSuite, deleteTestSuiteCase, getTestSuiteCases, getTestSuites, runTestSuite, updateTestSuite, upsertTestSuiteCase } from '@/api/testSuites'
import { setActiveProjectId } from '@/utils/projectContext'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => parseInt(route.params.projectId, 10))

const projects = ref([])
const selectedProjectId = ref('')
const testCases = ref([])
const projectEnvironments = ref([])
const suites = ref([])
const suiteCases = ref([])
const selectedSuiteId = ref('')
const suiteEnvironmentId = ref('')
const loading = ref(false)
const saving = ref(false)
const running = ref(false)
const suiteRunning = ref(false)
const importing = ref(false)
const projectName = ref('测试项目名称')
const keyword = ref('')
const caseGroupFilter = ref('')
const tagFilter = ref('')
const selectedCaseId = ref(null)
const activeTab = ref('params')
const expandedGroups = ref({})
const resultMap = ref({})
const formError = ref('')
const importError = ref('')
const lastRunAt = ref(null)
const showImportModal = ref(false)
const showSuiteModal = ref(false)
const importMode = ref('json')
const importJsonText = ref('')
const openApiSpecText = ref('')
const openApiBaseUrl = ref('')
const openApiCaseGroup = ref('openapi-import')
const openApiTags = ref('imported')
const postmanCollectionText = ref('')
const postmanCaseGroup = ref('postman-import')
const postmanTags = ref('imported, postman')
const paramsDraft = ref({ key: '', value: '' })
const suiteSaving = ref(false)
const editingSuiteId = ref(null)
const suiteFormError = ref('')
const suiteForm = ref({ name: '', description: '' })

const mainTabs = [
  { value: 'params', label: 'Params' },
  { value: 'headers', label: 'Headers' },
  { value: 'body', label: 'Body' },
  { value: 'assertions', label: 'Assertions' },
  { value: 'extraction', label: 'Extraction' },
  { value: 'expected', label: 'Expected Body' },
]

const importTabs = [
  { value: 'json', label: 'JSON 导入' },
  { value: 'openapi', label: 'OpenAPI 导入' },
  { value: 'postman', label: 'Postman 导入' },
]

const defaultForm = () => ({
  name: '',
  method: 'GET',
  url: '',
  case_group: '',
  tags: '',
  headers: '',
  body: '',
  expected_status: 200,
  expected_body: '',
  assertion_rules: '',
  extraction_rules: '',
})

const testCaseForm = ref(defaultForm())
const selectedCase = computed(() => testCases.value.find((item) => item.id === selectedCaseId.value) || null)
const selectedResult = computed(() => (selectedCaseId.value ? resultMap.value[selectedCaseId.value] || null : null))
const hasAnyFilter = computed(() => !!(keyword.value || caseGroupFilter.value || tagFilter.value))
const selectedSuite = computed(() => suites.value.find((item) => String(item.id) === selectedSuiteId.value) || null)
const selectedCaseInSuite = computed(() => suiteCases.value.find((item) => item.test_case_id === selectedCaseId.value) || null)

const groupedCaseEntries = computed(() => {
  const groups = new Map()
  for (const item of testCases.value) {
    const groupName = item.case_group || '未分组'
    if (!groups.has(groupName)) groups.set(groupName, [])
    groups.get(groupName).push(item)
  }
  return [...groups.entries()]
    .map(([name, items]) => ({
      name,
      items: [...items].sort((a, b) => {
        if (a.method === b.method) return a.name.localeCompare(b.name)
        return a.method.localeCompare(b.method)
      }),
    }))
    .sort((a, b) => a.name.localeCompare(b.name))
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

const editorValue = (value, fallback = '{}') => {
  if (value === null || value === undefined || value === '') return fallback
  return typeof value === 'string' ? value : JSON.stringify(value, null, 2)
}

const syncFormFromCase = (testCase) => {
  if (!testCase) {
    testCaseForm.value = defaultForm()
    activeTab.value = 'params'
    formError.value = ''
    return
  }
  testCaseForm.value = {
    id: testCase.id,
    name: testCase.name,
    method: testCase.method,
    url: testCase.url,
    case_group: testCase.case_group || '',
    tags: Array.isArray(testCase.tags) ? testCase.tags.join(', ') : '',
    headers: editorValue(testCase.headers, ''),
    body: editorValue(testCase.body, ''),
    expected_status: testCase.expected_status || 200,
    expected_body: editorValue(testCase.expected_body, ''),
    assertion_rules: editorValue(testCase.assertion_rules, ''),
    extraction_rules: editorValue(testCase.extraction_rules, ''),
  }
  formError.value = ''
}

const refreshExpandedGroups = () => {
  const nextState = {}
  for (const group of groupedCaseEntries.value) {
    nextState[group.name] = expandedGroups.value[group.name] ?? true
  }
  expandedGroups.value = nextState
}

const selectCase = (testCase) => {
  selectedCaseId.value = testCase.id
  syncFormFromCase(testCase)
}

const startNewCase = () => {
  selectedCaseId.value = null
  syncFormFromCase(null)
}

const fetchProjectName = async () => {
  try {
    projects.value = await getProjects()
    selectedProjectId.value = String(projectId.value)
    const project = projects.value.find((item) => item.id === projectId.value)
    if (project) projectName.value = project.name
  } catch (err) {
    console.error('Failed to fetch project name')
  }
}

const handleProjectChange = () => {
  if (!selectedProjectId.value) return
  const nextProjectId = Number(selectedProjectId.value)
  if (!Number.isFinite(nextProjectId) || nextProjectId === projectId.value) return
  setActiveProjectId(nextProjectId)
  router.push(`/project/${nextProjectId}`)
}

const fetchProjectEnvironments = async () => {
  try {
    projectEnvironments.value = await getProjectEnvironments(projectId.value)
  } catch (err) {
    projectEnvironments.value = []
  }
}

const fetchSuites = async () => {
  try {
    suites.value = await getTestSuites(projectId.value)
    if (selectedSuiteId.value && !suites.value.find((item) => String(item.id) === selectedSuiteId.value)) {
      selectedSuiteId.value = ''
      suiteCases.value = []
    }
  } catch (err) {
    suites.value = []
    suiteCases.value = []
  }
}

const fetchSuiteCases = async () => {
  if (!selectedSuiteId.value) {
    suiteCases.value = []
    return
  }
  try {
    suiteCases.value = await getTestSuiteCases(selectedSuiteId.value)
  } catch (err) {
    suiteCases.value = []
  }
}

const handleSelectedSuiteChange = async () => {
  await fetchSuiteCases()
}

const fetchTestCases = async () => {
  loading.value = true
  try {
    testCases.value = await getTestCases(projectId.value, {
      keyword: keyword.value || undefined,
      case_group: caseGroupFilter.value || undefined,
      tag: tagFilter.value || undefined,
    })
    refreshExpandedGroups()
    if (selectedCaseId.value) {
      const matched = testCases.value.find((item) => item.id === selectedCaseId.value)
      if (matched) {
        syncFormFromCase(matched)
      } else if (testCases.value.length) {
        selectCase(testCases.value[0])
      }
    } else if (testCases.value.length) {
      selectCase(testCases.value[0])
    }
  } catch (err) {
    alert('获取测试用例失败')
  } finally {
    loading.value = false
  }
}

const buildPayload = () => ({
  name: testCaseForm.value.name,
  method: testCaseForm.value.method,
  url: testCaseForm.value.url,
  case_group: testCaseForm.value.case_group?.trim() || null,
  tags: (testCaseForm.value.tags || '').split(',').map((item) => item.trim()).filter(Boolean),
  headers: testCaseForm.value.headers?.trim() || null,
  body: testCaseForm.value.body?.trim() || null,
  expected_status: parseInt(testCaseForm.value.expected_status, 10) || 200,
  expected_body: testCaseForm.value.expected_body?.trim() || null,
  assertion_rules: testCaseForm.value.assertion_rules?.trim() || null,
  extraction_rules: testCaseForm.value.extraction_rules?.trim() || null,
})

const buildExecutionPayload = () => ({
  method: testCaseForm.value.method?.trim() || null,
  url: testCaseForm.value.url?.trim() || null,
  headers: testCaseForm.value.headers?.trim() || null,
  body: testCaseForm.value.body?.trim() || null,
  expected_status: parseInt(testCaseForm.value.expected_status, 10) || 200,
  expected_body: testCaseForm.value.expected_body?.trim() || null,
  assertion_rules: testCaseForm.value.assertion_rules?.trim() || null,
  extraction_rules: testCaseForm.value.extraction_rules?.trim() || null,
})

const saveCurrentCase = async () => {
  if (!testCaseForm.value.name.trim() || !testCaseForm.value.url.trim()) {
    formError.value = '请先填写用例名称和请求 URL'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    const payload = buildPayload()
    let response
    if (selectedCaseId.value) {
      response = await updateTestCase(projectId.value, selectedCaseId.value, payload)
    } else {
      response = await createTestCase(projectId.value, payload)
      selectedCaseId.value = response.id
    }
    await fetchTestCases()
    if (response?.id) {
      const matched = testCases.value.find((item) => item.id === response.id)
      if (matched) selectCase(matched)
    }
  } catch (err) {
    formError.value = err.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

const runCurrentCase = async () => {
  if (!selectedCaseId.value) {
    formError.value = '请先保存接口用例，再执行测试'
    return
  }
  if (!testCaseForm.value.method?.trim() || !testCaseForm.value.url?.trim()) {
    formError.value = '请先补全请求方法和 URL，再执行测试'
    return
  }
  running.value = true
  formError.value = ''
  try {
    const result = await runTestCaseApi(projectId.value, selectedCaseId.value, buildExecutionPayload())
    resultMap.value = { ...resultMap.value, [selectedCaseId.value]: result }
    lastRunAt.value = Date.now()
  } catch (err) {
    alert(err.response?.data?.detail || '运行测试失败')
  } finally {
    running.value = false
  }
}

const openSuiteModal = (suite = null) => {
  editingSuiteId.value = suite?.id || null
  suiteForm.value = {
    name: suite?.name || '',
    description: suite?.description || '',
  }
  suiteFormError.value = ''
  showSuiteModal.value = true
}

const closeSuiteModal = () => {
  showSuiteModal.value = false
  editingSuiteId.value = null
  suiteSaving.value = false
  suiteFormError.value = ''
}

const submitSuite = async () => {
  if (!suiteForm.value.name.trim()) {
    suiteFormError.value = '套件名称不能为空'
    return
  }
  suiteSaving.value = true
  suiteFormError.value = ''
  try {
    if (editingSuiteId.value) {
      await updateTestSuite(editingSuiteId.value, { ...suiteForm.value })
    } else {
      const created = await createTestSuite(projectId.value, { ...suiteForm.value })
      selectedSuiteId.value = String(created.id)
    }
    closeSuiteModal()
    await fetchSuites()
    await fetchSuiteCases()
  } catch (err) {
    suiteFormError.value = err.response?.data?.detail || '保存套件失败'
  } finally {
    suiteSaving.value = false
  }
}

const deleteCurrentSuite = async () => {
  if (!selectedSuite.value) return
  if (!confirm(`确定删除套件「${selectedSuite.value.name}」吗？`)) return
  try {
    await deleteTestSuite(selectedSuite.value.id)
    selectedSuiteId.value = ''
    suiteCases.value = []
    await fetchSuites()
  } catch (err) {
    alert(err.response?.data?.detail || '删除套件失败')
  }
}

const attachCurrentCaseToSuite = async () => {
  if (!selectedSuite.value || !selectedCase.value) return
  try {
    await upsertTestSuiteCase(selectedSuite.value.id, selectedCase.value.id, {
      order_index: suiteCases.value.length,
    })
    await Promise.all([fetchSuites(), fetchSuiteCases()])
  } catch (err) {
    alert(err.response?.data?.detail || '加入套件失败')
  }
}

const removeCurrentCaseFromSuite = async () => {
  if (!selectedSuite.value || !selectedCaseInSuite.value) return
  try {
    await deleteTestSuiteCase(selectedSuite.value.id, selectedCaseInSuite.value.test_case_id)
    await Promise.all([fetchSuites(), fetchSuiteCases()])
  } catch (err) {
    alert(err.response?.data?.detail || '移出套件失败')
  }
}

const runCurrentSuite = async () => {
  if (!selectedSuite.value) return
  suiteRunning.value = true
  try {
    const response = await runTestSuite(selectedSuite.value.id, {
      environment_id: suiteEnvironmentId.value ? Number(suiteEnvironmentId.value) : undefined,
      retry_count: 0,
      retry_on: ['error'],
    })
    router.push(`/project/${projectId.value}/batches/${response.id}`)
  } catch (err) {
    alert(err.response?.data?.detail || '执行套件失败')
  } finally {
    suiteRunning.value = false
  }
}

const selectCaseById = (caseId) => {
  const matched = testCases.value.find((item) => item.id === caseId)
  if (matched) {
    selectCase(matched)
  }
}

const copyCurrentCase = async () => {
  if (!selectedCaseId.value) return
  try {
    const copied = await copyTestCaseApi(projectId.value, selectedCaseId.value, {})
    await fetchTestCases()
    const matched = testCases.value.find((item) => item.id === copied.id)
    if (matched) selectCase(matched)
  } catch (err) {
    alert(err.response?.data?.detail || '复制失败')
  }
}

const deleteCurrentCase = async () => {
  if (!selectedCaseId.value) return
  if (!confirm('确定要删除这个测试用例吗？')) return
  try {
    await deleteTestCaseApi(projectId.value, selectedCaseId.value)
    delete resultMap.value[selectedCaseId.value]
    selectedCaseId.value = null
    await fetchTestCases()
  } catch (err) {
    alert('删除失败')
  }
}

const handleExportCases = async () => {
  try {
    const payload = await exportTestCases(projectId.value)
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `test-cases-project-${projectId.value}.json`
    anchor.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    alert('导出失败')
  }
}

const openImportModal = (mode) => {
  importMode.value = mode
  importError.value = ''
  showImportModal.value = true
}

const closeImportModal = () => {
  showImportModal.value = false
  importError.value = ''
}

const submitImport = async () => {
  importing.value = true
  importError.value = ''
  try {
    let result
    if (importMode.value === 'json') {
      const parsed = JSON.parse(importJsonText.value || '{}')
      result = await importTestCases(projectId.value, { cases: parsed.cases || [], skip_duplicates: true })
    } else if (importMode.value === 'openapi') {
      const spec = JSON.parse(openApiSpecText.value || '{}')
      result = await importOpenApiTestCases(projectId.value, {
        spec,
        base_url: openApiBaseUrl.value || undefined,
        case_group: openApiCaseGroup.value || undefined,
        tags: (openApiTags.value || '').split(',').map((item) => item.trim()).filter(Boolean),
        skip_duplicates: true,
      })
    } else {
      const collection = JSON.parse(postmanCollectionText.value || '{}')
      result = await importTestCasesByProvider(projectId.value, {
        provider: 'postman',
        payload: {
          collection,
          case_group: postmanCaseGroup.value || undefined,
          tags: (postmanTags.value || '').split(',').map((item) => item.trim()).filter(Boolean),
          skip_duplicates: true,
        },
      })
    }
    await Promise.all([fetchTestCases(), fetchSuites()])
    closeImportModal()
    alert(`导入完成：成功 ${result.imported}，跳过 ${result.skipped}`)
  } catch (err) {
    importError.value = err.response?.data?.detail || '导入失败，请检查输入内容'
  } finally {
    importing.value = false
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

const toggleGroup = (groupName) => {
  expandedGroups.value = { ...expandedGroups.value, [groupName]: !expandedGroups.value[groupName] }
}

const clearParamsDraft = () => {
  paramsDraft.value = { key: '', value: '' }
}

const appendQueryParam = () => {
  if (!paramsDraft.value.key.trim()) return
  try {
    const url = new URL(testCaseForm.value.url || 'https://placeholder.local')
    url.searchParams.set(paramsDraft.value.key.trim(), paramsDraft.value.value)
    const nextUrl = testCaseForm.value.url.startsWith('http') ? url.toString() : `${url.pathname}${url.search}`
    testCaseForm.value.url = nextUrl
    clearParamsDraft()
  } catch {
    formError.value = '当前 URL 不是合法的绝对地址，无法追加 Params'
  }
}

const openRunDetail = () => {
  if (!selectedResult.value?.id) return
  router.push(`/project/${projectId.value}/runs/${selectedResult.value.id}`)
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

watch(projectId, async () => {
  selectedCaseId.value = null
  selectedSuiteId.value = ''
  suiteCases.value = []
  resultMap.value = {}
  await fetchProjectName()
  await Promise.all([fetchTestCases(), fetchSuites(), fetchProjectEnvironments()])
})

onMounted(async () => {
  setActiveProjectId(projectId.value)
  await fetchProjectName()
  await Promise.all([fetchTestCases(), fetchSuites(), fetchProjectEnvironments()])
})
</script>

<style scoped>
.api-test-page { padding: 0; height: 100%; }
.api-shell { display: grid; grid-template-columns: 280px 1fr; min-height: calc(100vh - 100px); }
.api-tree { background: var(--bg-card); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; }
.tree-toolbar { padding: 14px; border-bottom: 1px solid var(--border-color); }
.full-width { width: 100%; justify-content: center; }
.tree-tools { display: flex; gap: 8px; margin-top: 10px; }
.tree-search, .tree-filters { padding: 14px; border-bottom: 1px solid var(--border-color); }
.tree-search input, .tree-filters input { width: 100%; height: 36px; padding: 0 12px; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: var(--bg-card); color: var(--text-main); outline: none; }
.tree-filters { display: grid; gap: 8px; }
.filter-actions { display: flex; gap: 8px; }
.tree-content { padding: 12px; overflow: auto; }
.tree-group { margin-bottom: 10px; }
.tree-group-head { width: 100%; border: 0; background: transparent; display: flex; align-items: center; gap: 8px; padding: 8px 6px; color: var(--text-strong); font-size: 13px; text-align: left; }
.tree-toggle { color: var(--text-muted); width: 14px; text-align: center; }
.tree-folder { font-size: 14px; }
.tree-group-list { padding-left: 18px; }
.tree-item { width: 100%; border: 0; background: transparent; display: flex; align-items: center; gap: 8px; padding: 8px 8px; border-radius: var(--radius); text-align: left; color: var(--text-main); }
.tree-item.active { background: rgba(52, 152, 219, 0.10); color: var(--primary); }
.tree-item-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.method-badge { min-width: 44px; height: 22px; border-radius: 999px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; }
.method-GET { background: #e8f5e9; color: #27ae60; }
.method-POST { background: #e3f2fd; color: #3498db; }
.method-PUT { background: #fff8e1; color: #f39c12; }
.method-DELETE { background: #ffebee; color: #e74c3c; }
.method-PATCH { background: #f0e6ff; color: #9b59b6; }
.tree-empty { padding: 30px 16px; color: var(--text-muted); text-align: center; }
.api-main { background: var(--bg-page); padding: 24px; display: flex; flex-direction: column; gap: 14px; overflow: auto; }
.editor-card, .panel-card, .modal-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); box-shadow: var(--surface-shadow); }
.editor-card, .panel-card { padding: 18px; }
.editor-head, .response-head, .modal-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 16px; }
.editor-head h3, .response-head h3, .modal-head h3 { margin: 0 0 6px; font-size: 16px; font-weight: 500; color: var(--text-strong); }
.editor-head p, .response-head p, .modal-head p { margin: 0; font-size: 13px; color: var(--text-muted); }
.editor-actions, .response-meta, .modal-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.project-switch { display: flex; align-items: end; justify-content: space-between; gap: 12px; margin-bottom: 16px; }
.project-hint { font-size: 12px; color: var(--text-muted); }
.page-links { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
.suite-workbench { display: flex; align-items: end; justify-content: space-between; gap: 12px; margin-bottom: 16px; padding: 14px; border: 1px solid var(--border-color); border-radius: var(--radius); background: var(--bg-muted); }
.suite-main, .suite-actions { display: flex; align-items: end; gap: 12px; flex-wrap: wrap; }
.suite-case-strip { margin-bottom: 16px; padding: 12px 14px; border: 1px solid var(--border-color); border-radius: var(--radius); background: var(--bg-card); }
.suite-label { display: block; margin-bottom: 10px; font-size: 12px; color: var(--text-muted); }
.suite-chip-list { display: flex; flex-wrap: wrap; gap: 8px; }
.suite-chip { border: 1px solid var(--border-color-strong); border-radius: 999px; background: transparent; padding: 8px 12px; display: inline-flex; align-items: center; gap: 8px; color: var(--text-main); font-size: 12px; }
.suite-chip.active { border-color: var(--primary); background: rgba(52, 152, 219, 0.08); color: var(--primary); }
.suite-chip span { min-width: 18px; height: 18px; border-radius: 999px; background: var(--bg-muted); display: inline-flex; align-items: center; justify-content: center; font-size: 11px; }
.form-grid { display: grid; grid-template-columns: 1fr 180px; gap: 14px; }
.full-row { grid-column: 1 / -1; }
.field-block { display: flex; flex-direction: column; gap: 8px; }
.field-block span { font-size: 13px; color: var(--text-main); }
.field-block input, .field-block select, .field-block textarea { width: 100%; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: var(--bg-card); color: var(--text-main); padding: 10px 12px; outline: none; }
.field-block textarea { resize: vertical; font-family: Consolas, 'JetBrains Mono', monospace; }
.tab-strip { display: flex; align-items: center; gap: 24px; border-bottom: 1px solid var(--border-color); margin: -18px -18px 0; padding: 0 18px; }
.tab-btn { min-height: 38px; border: 0; background: transparent; color: var(--text-main); font-size: 13px; position: relative; }
.tab-btn.active { color: var(--primary); }
.tab-btn.active::after { content: ''; position: absolute; left: 0; right: 0; bottom: -1px; height: 2px; background: var(--primary); }
.tab-panel { padding-top: 18px; }
.kv-head, .kv-row { display: grid; grid-template-columns: 1fr 1fr 90px; gap: 10px; align-items: center; }
.kv-head { margin-bottom: 8px; font-size: 12px; color: var(--text-muted); }
.kv-row input { width: 100%; height: 32px; padding: 0 10px; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: var(--bg-card); color: var(--text-main); }
.response-card { min-height: 220px; }
.response-meta { font-size: 13px; color: var(--text-main); }
.status-chip { display: inline-flex; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }
.status-chip.success { background: #e8f5e9; color: #27ae60; }
.status-chip.failed, .status-chip.error { background: #ffebee; color: #e74c3c; }
.status-chip.running { background: #e3f2fd; color: #3498db; }
.response-body pre { margin: 0 0 12px; padding: 14px; background: var(--bg-muted); border-radius: var(--radius); font-size: 12px; line-height: 1.6; overflow: auto; color: var(--text-strong); }
.error-box { margin-bottom: 10px; padding: 12px 14px; border-radius: var(--radius); background: #ffebee; color: #e74c3c; font-size: 13px; }
.response-empty { min-height: 120px; display: grid; place-items: center; color: var(--text-muted); font-size: 13px; }
.primary-btn, .ghost-btn, .success-btn { min-height: 32px; padding: 0 14px; border-radius: var(--radius); font-size: 13px; }
.primary-btn { border: 0; background: var(--primary); color: #fff; }
.success-btn { border: 0; background: var(--success); color: #fff; }
.ghost-btn { border: 1px solid var(--border-color-strong); background: transparent; color: var(--text-main); }
.ghost-btn.small { min-height: 28px; padding: 0 8px; font-size: 12px; }
.table-link { border: 0; background: transparent; color: var(--primary); font-size: 13px; padding: 0; }
.form-error { margin: 12px 0 0; color: var(--danger); font-size: 13px; }
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 999; }
.modal-card { width: min(820px, 100%); padding: 20px; }
.import-strip { margin-top: -8px; }
.close-btn { border: 0; background: transparent; color: var(--text-muted); font-size: 18px; }
@media (max-width: 980px) {
  .api-shell { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .editor-head, .response-head, .modal-head, .project-switch, .suite-workbench, .suite-main, .suite-actions { flex-direction: column; align-items: flex-start; }
}
@media (max-width: 640px) {
  .api-main { padding: 16px; }
  .kv-head, .kv-row { grid-template-columns: 1fr; }
  .editor-actions, .modal-actions, .filter-actions { width: 100%; }
  .ghost-btn, .primary-btn, .success-btn { width: 100%; }
}
</style>
