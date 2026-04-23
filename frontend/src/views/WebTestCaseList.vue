<template>
  <section class="ui-automation-page">
    <div class="toolbar-card">
      <div class="toolbar-copy">
        <h2>{{ currentCaseLabel }}</h2>
        <p>{{ selectedCase ? (selectedCase.description || '管理页面步骤、执行日志和产物查看。') : '先选择或新建一个 Web 用例。' }}</p>
      </div>

      <div class="toolbar-actions">
        <select v-model="selectedCaseId" class="toolbar-select" @change="handleSelectedCaseChange">
          <option :value="''">选择 Web 用例</option>
          <option v-for="item in cases" :key="item.id" :value="String(item.id)">
            {{ item.name }}
          </option>
        </select>
        <button class="toolbar-btn" @click="copyCurrentCase" :disabled="!selectedCase">复制</button>
        <button class="toolbar-btn" @click="startNewCase">新建</button>
        <button class="toolbar-btn" @click="downloadTemplate">下载模板</button>
        <button class="toolbar-btn" @click="triggerImportExcel" :disabled="importing">{{ importing ? '导入中...' : '导入 Excel' }}</button>
        <button class="toolbar-btn" @click="handleExportExcel">导出 Excel</button>
        <button class="toolbar-btn" @click="saveCase" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
        <button class="toolbar-btn danger" @click="deleteCurrentCase" :disabled="!selectedCase">删除</button>
        <button class="toolbar-btn success" @click="runCurrentCase" :disabled="running || !selectedCase">
          {{ running ? '执行中...' : '开始执行' }}
        </button>
      </div>
    </div>
    <input ref="importInputRef" type="file" accept=".xlsx" class="hidden-file-input" @change="handleImportExcelChange" />

    <div class="project-switch">
      <label class="field-block project-select">
        <span>当前项目</span>
        <select v-model="selectedProjectId" class="toolbar-select project-select-input" @change="handleProjectChange">
          <option v-for="project in projects" :key="project.id" :value="String(project.id)">
            {{ project.name }}
          </option>
        </select>
      </label>
      <div class="project-switch-copy">{{ projectName }}</div>
    </div>

    <div class="page-links">
      <button class="toolbar-btn small" @click="router.push(`/project/${projectId}/reports`)">测试报告</button>
      <button class="toolbar-btn small" @click="router.push(`/project/${projectId}/executions`)">执行中心</button>
      <button class="toolbar-btn small" @click="router.push(`/project/${projectId}/environments`)">环境治理</button>
      <button class="toolbar-btn small" @click="router.push(`/project/${projectId}/integration-governance`)">集成治理</button>
      <button class="toolbar-btn small" @click="router.push(`/project/${projectId}/web-batches`)">批次结果</button>
    </div>

    <section class="panel-card case-selector-card">
      <div class="panel-head">
        <div>
          <h3>用例清单</h3>
          <p class="selector-copy">支持多选后批量执行和批量删除，单击用例可切到编辑态。</p>
        </div>
        <div class="batch-inline">
          <span>已选 {{ selectedCaseIds.length }} 项</span>
          <button class="toolbar-btn small" @click="toggleSelectAllCases">
            {{ isAllCasesSelected ? '取消全选' : '全选用例' }}
          </button>
          <button class="toolbar-btn small" :disabled="!selectedCaseIds.length" @click="clearSelectedCases">清空</button>
          <button class="toolbar-btn small danger" :disabled="!selectedCaseIds.length || batchDeleting" @click="deleteSelectedCases">
            {{ batchDeleting ? '删除中...' : '批量删除' }}
          </button>
          <button class="toolbar-btn small success" :disabled="!selectedCaseIds.length || batchRunning" @click="runSelectedCases">
            {{ batchRunning ? '执行中...' : '批量执行' }}
          </button>
        </div>
      </div>

      <div v-if="!cases.length" class="empty-block">
        <p>当前项目还没有 Web 用例，先新建一个再批量管理。</p>
      </div>

      <div v-else class="case-selector-list">
        <div
          v-for="item in cases"
          :key="item.id"
          class="case-selector-item"
          :class="{ active: String(item.id) === selectedCaseId }"
        >
          <label class="case-selector-check" @click.stop>
            <input type="checkbox" :checked="selectedCaseIds.includes(String(item.id))" @change="toggleCaseSelection(String(item.id))" />
          </label>
          <button class="case-selector-main" @click="openCaseFromList(item)">
            <strong>{{ item.name }}</strong>
            <span>{{ item.description || item.base_url || '未填写描述' }}</span>
          </button>
        </div>
      </div>
    </section>

    <div class="workspace-grid">
      <section class="panel-card">
        <div class="panel-head">
          <h3>测试步骤</h3>
          <button class="mini-btn" @click="addStep">添加步骤</button>
        </div>

        <div v-if="form.steps.length === 0" class="empty-block">
          <p>暂无步骤，可先添加 1 条。</p>
        </div>

        <div v-else class="steps-list">
          <div
            v-for="(step, index) in form.steps"
            :key="`step-${index}`"
            class="timeline-item"
            :class="{ tail: index < form.steps.length - 1 }"
          >
            <div class="timeline-node" :class="stepNodeClass(index)">
              <span>{{ index + 1 }}</span>
            </div>

            <div class="step-card">
              <div class="step-head">
                <div>
                  <div class="step-title">{{ stepLabel(step.action) }}</div>
                  <div class="step-subtitle">{{ stepPreview(step) }}</div>
                </div>
                <div class="step-actions">
                  <button class="icon-link" @click="insertStep(index, 'before')">前插</button>
                  <button class="icon-link" @click="insertStep(index, 'after')">后插</button>
                  <button class="icon-link" @click="moveStepUp(index)" :disabled="index === 0">↑</button>
                  <button class="icon-link" @click="moveStepDown(index)" :disabled="index === form.steps.length - 1">↓</button>
                  <button class="icon-link danger" @click="removeStep(index)">删除</button>
                </div>
              </div>

              <div class="step-editor">
                <label class="field-block narrow">
                  <span>动作</span>
                  <select v-model="step.action">
                    <option value="open">open</option>
                    <option value="click">click</option>
                    <option value="input">input</option>
                    <option value="wait">wait</option>
                    <option value="assert">assert</option>
                    <option value="screenshot">screenshot</option>
                  </select>
                </label>

                <template v-if="step.action === 'open'">
                  <label class="field-block">
                    <span>打开地址</span>
                    <input v-model.trim="step.url" type="text" placeholder="例如：/login 或 https://example.com/login" />
                  </label>
                </template>

                <template v-else-if="step.action === 'screenshot'">
                  <label class="field-block">
                    <span>截图文件名</span>
                    <input v-model.trim="step.filename" type="text" placeholder="例如：login-success.png" />
                  </label>
                </template>

                <template v-else>
                  <label class="field-block narrow">
                    <span>定位方式</span>
                    <select v-model="step.locator_strategy">
                      <option v-for="item in locatorStrategies" :key="item.value" :value="item.value">
                        {{ item.label }}
                      </option>
                    </select>
                  </label>

                  <label class="field-block">
                    <span>定位内容</span>
                    <input v-model.trim="step.locator" type="text" :placeholder="locatorPlaceholder(step.locator_strategy)" />
                    <small v-if="step.locator_strategy === 'role'">`role` 输入格式：`button|登录`</small>
                  </label>

                  <label v-if="step.action === 'input'" class="field-block">
                    <span>输入值</span>
                    <input v-model="step.input_value" type="text" placeholder="请输入要填入的内容" />
                  </label>

                  <label v-if="step.action === 'assert'" class="field-block">
                    <span>期望包含文本</span>
                    <input v-model="step.expected_text" type="text" placeholder="例如：欢迎回来" />
                  </label>

                  <label v-if="step.action === 'wait'" class="field-block narrow">
                    <span>等待时间 (ms)</span>
                    <input v-model.number="step.wait_ms" type="number" min="100" max="60000" />
                  </label>
                </template>
              </div>

              <div v-if="selectedRunDetail?.step_logs?.[index]" class="step-log">
                <span class="log-badge" :class="selectedRunDetail.step_logs[index].status || 'info'">
                  {{ selectedRunDetail.step_logs[index].status || 'info' }}
                </span>
                <span>{{ renderStepLog(selectedRunDetail.step_logs[index]) }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="panel-card logs-card">
        <div class="panel-head">
          <h3>执行日志</h3>
          <select v-model="selectedRunId" class="run-select" @change="handleSelectedRunChange">
            <option :value="''">选择执行记录</option>
            <option v-for="run in caseRuns" :key="run.id" :value="String(run.id)">
              #{{ run.id }} · {{ run.status }} · {{ formatDate(run.created_at) }}
            </option>
          </select>
        </div>

        <div class="log-console">
          <div v-if="selectedRunDetail" class="log-lines">
            <div class="log-line">
              <span class="log-time">{{ formatTime(selectedRunDetail.created_at) }}</span>
              <span class="log-level info">[INFO]</span>
              <span class="log-message">开始执行 Web 用例：{{ selectedRunDetail.web_test_case_name }}</span>
            </div>
            <div
              v-for="(item, index) in selectedRunDetail.step_logs"
              :key="`log-${index}`"
              class="log-line"
            >
              <span class="log-time">{{ formatTime(selectedRunDetail.created_at, index + 1) }}</span>
              <span class="log-level" :class="item.status || 'info'">[{{ (item.status || 'info').toUpperCase() }}]</span>
              <span class="log-message">{{ renderStepLog(item) }}</span>
            </div>
            <div class="log-line">
              <span class="log-time">{{ formatTime(selectedRunDetail.created_at, selectedRunDetail.step_logs.length + 2) }}</span>
              <span class="log-level" :class="selectedRunDetail.status">[{{ selectedRunDetail.status.toUpperCase() }}]</span>
              <span class="log-message">执行完成，耗时 {{ selectedRunDetail.duration_ms || '--' }} ms</span>
            </div>
          </div>
          <div v-else class="empty-console">
            点击“开始执行”或选择历史执行记录后，这里会显示步骤日志。
          </div>
        </div>

        <div class="log-footer">
          <div class="footer-metric">
            <span>已执行步骤</span>
            <strong>{{ executedStepCount }} / {{ form.steps.length }}</strong>
          </div>
          <div class="footer-metric">
            <span>成功</span>
            <strong class="success">{{ successStepCount }}</strong>
          </div>
          <div class="footer-metric">
            <span>失败</span>
            <strong class="danger">{{ failedStepCount }}</strong>
          </div>
        </div>
      </section>
    </div>

    <section class="panel-card config-card">
      <div class="panel-head">
        <h3>测试配置</h3>
      </div>

      <div class="config-grid">
        <label class="field-block">
          <span>用例名称</span>
          <input v-model.trim="form.name" type="text" placeholder="例如：登录流程 smoke" />
        </label>

        <label class="field-block">
          <span>Base URL</span>
          <input v-model.trim="form.base_url" type="text" placeholder="例如：https://example.com" />
        </label>

        <label class="field-block full-row">
          <span>描述</span>
          <textarea v-model.trim="form.description" rows="3" placeholder="描述这个 Web 用例的业务流程"></textarea>
        </label>

        <label class="field-block">
          <span>浏览器类型</span>
          <select v-model="form.browser_name">
            <option value="chromium">Chromium</option>
            <option value="firefox">Firefox</option>
            <option value="webkit">WebKit</option>
          </select>
        </label>

        <label class="field-block">
          <span>窗口大小</span>
          <select v-model="form.viewport_preset">
            <option value="1920x1080">1920x1080</option>
            <option value="1366x768">1366x768</option>
            <option value="1280x720">1280x720</option>
            <option value="375x667">375x667 (Mobile)</option>
            <option value="custom">自定义</option>
          </select>
        </label>

        <label class="field-block">
          <span>超时时间</span>
          <div class="inline-mix">
            <input v-model.number="form.timeout_seconds" type="number" min="1" max="300" />
            <span>秒</span>
          </div>
        </label>
      </div>

      <div class="config-grid compact" v-if="form.viewport_preset === 'custom'">
        <label class="field-block">
          <span>宽度</span>
          <input v-model.number="form.viewport_width" type="number" min="320" max="4096" />
        </label>
        <label class="field-block">
          <span>高度</span>
          <input v-model.number="form.viewport_height" type="number" min="320" max="4096" />
        </label>
      </div>

      <div class="switch-grid">
        <label class="switch-item">
          <input v-model="form.capture_on_failure" type="checkbox" />
          <span>失败时自动截图</span>
        </label>
        <label class="switch-item">
          <input v-model="form.headless" type="checkbox" />
          <span>启用无头模式</span>
        </label>
        <label class="switch-item">
          <input v-model="form.record_video" type="checkbox" />
          <span>录制执行视频</span>
        </label>
      </div>

      <div v-if="selectedRunDetail?.artifacts?.length" class="artifacts-panel">
        <h4>执行产物</h4>
        <div class="artifact-list">
          <a
            v-for="item in selectedRunDetail.artifacts"
            :key="item"
            class="artifact-chip"
            :href="`/${item}`"
            target="_blank"
            rel="noreferrer"
          >
            {{ item }}
          </a>
        </div>
      </div>

      <p v-if="formError" class="form-error">{{ formError }}</p>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProjects } from '@/api/projects'
import {
  bulkDeleteWebTestCases,
  copyWebTestCase,
  createWebTestCase,
  deleteWebTestCase,
  downloadWebTestCaseTemplate,
  exportWebTestCases,
  getWebTestCase,
  getWebTestCases,
  importWebTestCasesFromExcel,
  updateWebTestCase,
} from '@/api/webTestCases'
import { getWebTestRunDetail, getWebTestRuns, runBatchWebTestCases, runWebTestCase } from '@/api/webTestRuns'
import { setActiveProjectId } from '@/utils/projectContext'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => Number(route.params.projectId))

const projects = ref([])
const selectedProjectId = ref('')
const loadingCases = ref(false)
const saving = ref(false)
const importing = ref(false)
const running = ref(false)
const formError = ref('')
const projectName = ref('Web 项目')
const cases = ref([])
const runs = ref([])
const selectedCaseId = ref('')
const selectedCaseIds = ref([])
const selectedRunId = ref('')
const selectedRunDetail = ref(null)
const batchRunning = ref(false)
const batchDeleting = ref(false)
const importInputRef = ref(null)

const form = ref({
  name: '',
  description: '',
  base_url: '',
  browser_name: 'chromium',
  viewport_preset: '1920x1080',
  viewport_width: 1920,
  viewport_height: 1080,
  timeout_seconds: 30,
  headless: true,
  capture_on_failure: true,
  record_video: false,
  steps: [],
})

const locatorStrategies = [
  { value: 'css', label: 'CSS' },
  { value: 'xpath', label: 'XPath' },
  { value: 'text', label: 'Text' },
  { value: 'testid', label: 'TestId' },
  { value: 'role', label: 'Role' },
]

const selectedCase = computed(() => cases.value.find((item) => String(item.id) === selectedCaseId.value) || null)
const currentCaseLabel = computed(() => selectedCase.value?.name || '新建 Web 用例')
const caseRuns = computed(() => runs.value.filter((item) => String(item.web_test_case_id) === selectedCaseId.value))
const isAllCasesSelected = computed(() => cases.value.length > 0 && cases.value.every((item) => selectedCaseIds.value.includes(String(item.id))))
const executedStepCount = computed(() => selectedRunDetail.value?.step_logs?.length || 0)
const successStepCount = computed(() => (selectedRunDetail.value?.step_logs || []).filter((item) => item.status === 'success').length)
const failedStepCount = computed(() => (selectedRunDetail.value?.step_logs || []).filter((item) => ['failed', 'error'].includes(item.status)).length)

const normalizeTimestamp = (value) => {
  if (!value) return 0
  const numeric = Number(value)
  return numeric > 1e12 ? numeric : numeric * 1000
}

const formatDate = (value) => {
  if (!value) return '--'
  return new Date(normalizeTimestamp(value)).toLocaleString('zh-CN')
}

const formatTime = (value, offset = 0) => {
  if (!value) return '--:--:--'
  const date = new Date(normalizeTimestamp(value) + offset * 1000)
  return date.toLocaleTimeString('zh-CN', { hour12: false })
}

const resetForm = () => {
  form.value = {
    name: '',
    description: '',
    base_url: '',
    browser_name: 'chromium',
    viewport_preset: '1920x1080',
    viewport_width: 1920,
    viewport_height: 1080,
    timeout_seconds: 30,
    headless: true,
    capture_on_failure: true,
    record_video: false,
    steps: [],
  }
  formError.value = ''
}

const syncSelectedCaseIds = () => {
  const validIds = new Set(cases.value.map((item) => String(item.id)))
  selectedCaseIds.value = selectedCaseIds.value.filter((id) => validIds.has(id))
}

const clearSelectedCases = () => {
  selectedCaseIds.value = []
}

const toggleCaseSelection = (caseId) => {
  if (selectedCaseIds.value.includes(caseId)) {
    selectedCaseIds.value = selectedCaseIds.value.filter((id) => id !== caseId)
    return
  }
  selectedCaseIds.value = [...selectedCaseIds.value, caseId]
}

const toggleSelectAllCases = () => {
  if (isAllCasesSelected.value) {
    clearSelectedCases()
    return
  }
  selectedCaseIds.value = cases.value.map((item) => String(item.id))
}

const openCaseFromList = (item) => {
  selectedCaseId.value = String(item.id)
}

const inferLocatorStrategy = (params = {}) => {
  const raw = String(params.locator_type || params.strategy || '').trim().toLowerCase()
  if (raw && locatorStrategies.some((item) => item.value === raw)) return raw
  const locator = String(params.locator || params.selector || '').trim()
  if (locator.startsWith('//') || locator.startsWith('xpath=')) return 'xpath'
  return 'css'
}

const createStepDraft = (action = 'open', params = {}) => ({
  action,
  url: params.url || '',
  locator_strategy: inferLocatorStrategy(params),
  locator: params.locator || params.selector || '',
  input_value: params.value || '',
  expected_text: params.contains || '',
  wait_ms: Number(params.timeout_ms || 500),
  filename: params.filename || '',
})

const detectViewportPreset = (width, height) => {
  const candidate = `${width || 1920}x${height || 1080}`
  if (['1920x1080', '1366x768', '1280x720', '375x667'].includes(candidate)) {
    return candidate
  }
  return 'custom'
}

const syncFormFromCase = (detail) => {
  form.value = {
    name: detail.name || '',
    description: detail.description || '',
    base_url: detail.base_url || '',
    browser_name: detail.browser_name || 'chromium',
    viewport_preset: detectViewportPreset(detail.viewport_width, detail.viewport_height),
    viewport_width: detail.viewport_width || 1920,
    viewport_height: detail.viewport_height || 1080,
    timeout_seconds: Math.round((detail.timeout_ms || 30000) / 1000),
    headless: detail.headless ?? true,
    capture_on_failure: detail.capture_on_failure ?? true,
    record_video: detail.record_video ?? false,
    steps: (detail.steps || []).map((step) => createStepDraft(step.action || 'open', step.params || {})),
  }
}

const fetchProjectName = async () => {
  try {
    const list = await getProjects()
    const project = list.find((item) => item.id === projectId)
    if (project) {
      projectName.value = `${project.name} · UI自动化`
    }
  } catch (err) {
    console.error('Failed to fetch project name')
  }
}

const syncProjectOptions = async () => {
  try {
    projects.value = await getProjects()
    selectedProjectId.value = String(projectId.value)
    const project = projects.value.find((item) => item.id === projectId.value)
    if (project) {
      projectName.value = `${project.name} · UI自动化`
    }
  } catch (err) {
    console.error('Failed to fetch project options')
  }
}

const handleProjectChange = () => {
  if (!selectedProjectId.value) return
  const nextProjectId = Number(selectedProjectId.value)
  if (!Number.isFinite(nextProjectId) || nextProjectId === projectId.value) return
  setActiveProjectId(nextProjectId)
  router.push(`/project/${nextProjectId}/web-test-cases`)
}

const fetchCases = async () => {
  loadingCases.value = true
  try {
    cases.value = await getWebTestCases(projectId.value)
    syncSelectedCaseIds()
    if (selectedCaseId.value && !cases.value.some((item) => String(item.id) === selectedCaseId.value)) {
      selectedCaseId.value = ''
    }
    if (!selectedCaseId.value && cases.value.length) {
      selectedCaseId.value = String(cases.value[0].id)
    }
  } catch (err) {
    alert('获取 Web 用例失败')
  } finally {
    loadingCases.value = false
  }
}

const fetchRuns = async () => {
  try {
    runs.value = await getWebTestRuns(projectId.value)
  } catch (err) {
    console.error('Failed to fetch runs')
  }
}

const loadSelectedCaseDetail = async () => {
  if (!selectedCaseId.value) {
    resetForm()
    return
  }
  try {
    const detail = await getWebTestCase(selectedCaseId.value)
    syncFormFromCase(detail)
  } catch (err) {
    alert('加载 Web 用例详情失败')
  }
}

const loadSelectedRunDetail = async () => {
  if (!selectedRunId.value) {
    selectedRunDetail.value = null
    return
  }
  try {
    selectedRunDetail.value = await getWebTestRunDetail(selectedRunId.value)
  } catch (err) {
    alert('加载 Web 执行详情失败')
  }
}

const handleSelectedCaseChange = async () => {
  selectedRunId.value = ''
  selectedRunDetail.value = null
  await loadSelectedCaseDetail()
  if (caseRuns.value.length) {
    selectedRunId.value = String(caseRuns.value[0].id)
    await loadSelectedRunDetail()
  }
}

const handleSelectedRunChange = async () => {
  await loadSelectedRunDetail()
}

const startNewCase = () => {
  selectedCaseId.value = ''
  selectedRunId.value = ''
  selectedRunDetail.value = null
  resetForm()
  addStep()
}

const triggerImportExcel = () => {
  importInputRef.value?.click()
}

const addStep = () => {
  form.value.steps.push(createStepDraft('open'))
}

const insertStep = (index, position = 'after') => {
  const nextIndex = position === 'before' ? index : index + 1
  form.value.steps.splice(nextIndex, 0, createStepDraft('open'))
}

const removeStep = (index) => {
  form.value.steps.splice(index, 1)
}

const moveStepUp = (index) => {
  if (index === 0) return
  const copy = [...form.value.steps]
  ;[copy[index - 1], copy[index]] = [copy[index], copy[index - 1]]
  form.value.steps = copy
}

const moveStepDown = (index) => {
  if (index >= form.value.steps.length - 1) return
  const copy = [...form.value.steps]
  ;[copy[index], copy[index + 1]] = [copy[index + 1], copy[index]]
  form.value.steps = copy
}

const buildPayload = () => {
  if (!form.value.name.trim()) {
    throw new Error('用例名称不能为空')
  }

  let viewportWidth = form.value.viewport_width
  let viewportHeight = form.value.viewport_height
  if (form.value.viewport_preset !== 'custom') {
    const [width, height] = form.value.viewport_preset.split('x').map((item) => Number(item))
    viewportWidth = width
    viewportHeight = height
  }

  const steps = form.value.steps.map((step, index) => {
    const parsed = {}
    if (step.action === 'open') {
      if (!step.url?.trim()) throw new Error(`第 ${index + 1} 步需要填写打开地址`)
      parsed.url = step.url.trim()
    } else if (step.action === 'screenshot') {
      if (step.filename?.trim()) parsed.filename = step.filename.trim()
    } else {
      const locatorValue = step.locator?.trim()
      if (step.action !== 'wait' && !locatorValue) throw new Error(`第 ${index + 1} 步需要填写定位内容`)
      if (locatorValue) {
        parsed.locator_type = step.locator_strategy
        parsed.locator = locatorValue
      }
      if (step.action === 'input') {
        parsed.value = step.input_value ?? ''
      } else if (step.action === 'assert') {
        if (!step.expected_text?.trim()) throw new Error(`第 ${index + 1} 步需要填写期望文本`)
        parsed.contains = step.expected_text.trim()
      } else if (step.action === 'wait') {
        parsed.timeout_ms = Number(step.wait_ms) || 500
      }
    }
    return {
      action: step.action,
      params: parsed,
    }
  })

  return {
    name: form.value.name,
    description: form.value.description || null,
    base_url: form.value.base_url || null,
    browser_name: form.value.browser_name,
    viewport_width: viewportWidth,
    viewport_height: viewportHeight,
    timeout_ms: (Number(form.value.timeout_seconds) || 30) * 1000,
    headless: !!form.value.headless,
    capture_on_failure: !!form.value.capture_on_failure,
    record_video: !!form.value.record_video,
    steps,
  }
}

const saveCase = async () => {
  saving.value = true
  formError.value = ''
  try {
    const payload = buildPayload()
    if (selectedCaseId.value) {
      await updateWebTestCase(selectedCaseId.value, payload)
    } else {
      const created = await createWebTestCase({ project_id: projectId.value, ...payload })
      selectedCaseId.value = String(created.id)
    }
    await fetchCases()
    await handleSelectedCaseChange()
  } catch (err) {
    formError.value = err.response?.data?.detail || err.message || '保存失败'
  } finally {
    saving.value = false
  }
}

const copyCurrentCase = async () => {
  if (!selectedCase.value) return
  try {
    const copied = await copyWebTestCase(selectedCase.value.id, {})
    await fetchCases()
    selectedCaseId.value = String(copied.id)
    await handleSelectedCaseChange()
  } catch (err) {
    alert(err.response?.data?.detail || '复制失败')
  }
}

const deleteCurrentCase = async () => {
  if (!selectedCase.value) return
  if (!confirm('确定删除该 Web 用例吗？')) return
  try {
    await deleteWebTestCase(selectedCase.value.id)
    selectedCaseIds.value = selectedCaseIds.value.filter((id) => id !== selectedCaseId.value)
    selectedCaseId.value = ''
    selectedRunId.value = ''
    selectedRunDetail.value = null
    await fetchCases()
    await handleSelectedCaseChange()
  } catch (err) {
    alert('删除失败')
  }
}

const runCurrentCase = async () => {
  if (!selectedCase.value) {
    formError.value = '请先保存一个 Web 用例再执行'
    return
  }
  running.value = true
  try {
    const run = await runWebTestCase(selectedCase.value.id)
    await fetchRuns()
    selectedRunId.value = String(run.id)
    await loadSelectedRunDetail()
  } catch (err) {
    alert(err.response?.data?.detail || '执行失败')
  } finally {
    running.value = false
  }
}

const runSelectedCases = async () => {
  if (!selectedCaseIds.value.length) return
  batchRunning.value = true
  let response
  try {
    response = await runBatchWebTestCases(projectId.value, {
      test_case_ids: selectedCaseIds.value.map((id) => Number(id)),
    })
  } catch (err) {
    alert(err.response?.data?.detail || '批量执行请求失败')
    batchRunning.value = false
    return
  }

  try {
    clearSelectedCases()
    if (response.status === 'failed' || response.status === 'error') {
      alert(`批量执行完成：成功 ${response.passed_cases}，失败 ${response.failed_cases}，异常 ${response.error_cases}`)
    }
    if (response.id) {
      router.push(`/project/${projectId.value}/web-batches/${response.id}`)
      return
    }
    await fetchRuns()
  } catch (err) {
    console.error('Batch execution follow-up failed', err)
  } finally {
    batchRunning.value = false
  }
}

const deleteSelectedCases = async () => {
  if (!selectedCaseIds.value.length) return
  if (!confirm(`确定批量删除 ${selectedCaseIds.value.length} 个 Web 用例吗？`)) return
  batchDeleting.value = true
  try {
    const deletedCaseIds = [...selectedCaseIds.value]
    await bulkDeleteWebTestCases(projectId.value, {
      test_case_ids: deletedCaseIds.map((id) => Number(id)),
    })
    if (selectedCaseId.value && deletedCaseIds.includes(selectedCaseId.value)) {
      selectedCaseId.value = ''
      selectedRunId.value = ''
      selectedRunDetail.value = null
    }
    clearSelectedCases()
    await Promise.all([fetchCases(), fetchRuns()])
    if (cases.value.length && selectedCaseId.value) {
      await handleSelectedCaseChange()
    }
  } catch (err) {
    alert(err.response?.data?.detail || '批量删除失败')
  } finally {
    batchDeleting.value = false
  }
}

const downloadBlobFile = (blob, fileName) => {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  link.click()
  URL.revokeObjectURL(url)
}

const downloadTemplate = async () => {
  try {
    const blob = await downloadWebTestCaseTemplate(projectId.value)
    downloadBlobFile(blob, `web-test-cases-project-${projectId.value}-template.xlsx`)
  } catch (err) {
    alert(err.response?.data?.detail || '下载模板失败')
  }
}

const handleExportExcel = async () => {
  try {
    const blob = await exportWebTestCases(projectId.value)
    downloadBlobFile(blob, `web-test-cases-project-${projectId.value}-export.xlsx`)
  } catch (err) {
    alert(err.response?.data?.detail || '导出 Excel 失败')
  }
}

const arrayBufferToBase64 = (buffer) => {
  let binary = ''
  const bytes = new Uint8Array(buffer)
  const chunkSize = 0x8000
  for (let index = 0; index < bytes.length; index += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(index, index + chunkSize))
  }
  return btoa(binary)
}

const handleImportExcelChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  importing.value = true
  try {
    const fileContentBase64 = arrayBufferToBase64(await file.arrayBuffer())
    const result = await importWebTestCasesFromExcel(projectId.value, {
      file_name: file.name,
      file_content_base64: fileContentBase64,
    })
    await fetchCases()
    alert(`导入完成：新增 ${result.imported}，更新 ${result.updated}`)
  } catch (err) {
    alert(err.response?.data?.detail || '导入 Excel 失败')
  } finally {
    importing.value = false
    if (importInputRef.value) {
      importInputRef.value.value = ''
    }
  }
}

const stepLabel = (action) => {
  const mapping = {
    open: '打开页面',
    click: '点击元素',
    input: '输入文本',
    wait: '等待条件',
    assert: '断言校验',
    screenshot: '截图',
  }
  return mapping[action] || action
}

const stepPreview = (paramsText) => {
  if (!paramsText) return '暂无参数'
  if (paramsText.action === 'open') return paramsText.url || '待填写打开地址'
  if (paramsText.action === 'screenshot') return paramsText.filename || '使用默认截图文件名'
  const locator = paramsText.locator ? `${paramsText.locator_strategy}: ${paramsText.locator}` : '待填写定位内容'
  if (paramsText.action === 'input') return `${locator} · value: ${paramsText.input_value || ''}`
  if (paramsText.action === 'assert') return `${locator} · contains: ${paramsText.expected_text || ''}`
  if (paramsText.action === 'wait') return `${paramsText.locator ? locator : 'fixed wait'} · timeout: ${paramsText.wait_ms || 500}ms`
  return locator
}

const locatorPlaceholder = (strategy) => {
  if (strategy === 'xpath') return '//button[@id="submit"]'
  if (strategy === 'text') return '登录'
  if (strategy === 'testid') return 'submit-button'
  if (strategy === 'role') return 'button|登录'
  return '#submit'
}

const renderStepLog = (item) => {
  if (!item) return '无日志'
  const action = item.action ? `动作 ${item.action}` : '步骤执行'
  return `${action}${item.message ? ` · ${item.message}` : ''}`
}

const stepNodeClass = (index) => {
  const status = selectedRunDetail.value?.step_logs?.[index]?.status
  if (status === 'success') return 'success'
  if (status === 'failed' || status === 'error') return 'danger'
  if (status === 'running') return 'running'
  return 'pending'
}

watch(selectedCaseId, async (value, oldValue) => {
  if (value === oldValue) return
  await handleSelectedCaseChange()
})

watch(projectId, async () => {
  selectedCaseId.value = ''
  selectedCaseIds.value = []
  selectedRunId.value = ''
  selectedRunDetail.value = null
  await syncProjectOptions()
  await Promise.all([fetchCases(), fetchRuns()])
  if (cases.value.length && selectedCaseId.value) {
    await handleSelectedCaseChange()
  } else if (!cases.value.length) {
    addStep()
  }
})

onMounted(async () => {
  setActiveProjectId(projectId.value)
  await syncProjectOptions()
  await Promise.all([fetchCases(), fetchRuns()])
  if (cases.value.length && selectedCaseId.value) {
    await handleSelectedCaseChange()
  } else if (!cases.value.length) {
    addStep()
  }
})
</script>

<style scoped>
.ui-automation-page { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.toolbar-card, .panel-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); box-shadow: var(--surface-shadow); }
.toolbar-card { padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.toolbar-copy h2 { margin: 0 0 6px; font-size: 18px; font-weight: 500; color: var(--text-strong); }
.toolbar-copy p { margin: 0; font-size: 13px; color: var(--text-muted); }
.toolbar-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.hidden-file-input { display: none; }
.project-switch { display: flex; align-items: end; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.project-select { min-width: 360px; max-width: 520px; flex: 1 1 360px; }
.project-select-input { min-width: 360px; width: 100%; }
.project-switch-copy { font-size: 12px; color: var(--text-muted); flex: 1 1 240px; min-width: 220px; word-break: break-word; }
.page-links { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.case-selector-card { display: flex; flex-direction: column; gap: 14px; }
.selector-copy { margin: 6px 0 0; font-size: 12px; color: var(--text-muted); }
.batch-inline { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 12px; color: var(--text-muted); }
.case-selector-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
.case-selector-item { display: flex; align-items: stretch; gap: 10px; padding: 12px; border: 1px solid var(--border-color); border-radius: var(--radius); background: var(--bg-muted); }
.case-selector-item.active { border-color: var(--primary); background: rgba(52, 152, 219, 0.08); }
.case-selector-check { display: inline-flex; align-items: center; justify-content: center; width: 18px; }
.case-selector-main { flex: 1; border: 0; background: transparent; display: flex; flex-direction: column; align-items: flex-start; gap: 4px; text-align: left; color: var(--text-main); }
.case-selector-main strong { font-size: 14px; color: var(--text-strong); }
.case-selector-main span { font-size: 12px; color: var(--text-muted); line-height: 1.5; }
.toolbar-select {
  min-width: 240px;
  height: 36px;
  line-height: 20px;
  padding: 0 36px 0 12px;
  border: 1px solid var(--border-color-strong);
  border-radius: var(--radius);
  background: var(--bg-card);
  color: var(--text-main);
  outline: none;
  appearance: auto;
  -webkit-appearance: menulist;
  box-sizing: border-box;
  vertical-align: middle;
}
.toolbar-btn { min-height: 36px; padding: 0 16px; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: transparent; color: var(--text-main); font-size: 13px; }
.toolbar-btn.small { min-height: 30px; padding: 0 12px; }
.toolbar-btn.success { background: var(--success); border-color: var(--success); color: #fff; }
.toolbar-btn.danger { color: var(--danger); }
.workspace-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.panel-card { padding: 20px; }
.panel-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 16px; }
.panel-head h3 { margin: 0; font-size: 16px; font-weight: 500; color: var(--text-strong); }
.mini-btn { min-height: 28px; padding: 0 12px; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: var(--primary); color: #fff; font-size: 12px; }
.steps-list { display: flex; flex-direction: column; gap: 14px; }
.timeline-item { position: relative; padding-left: 44px; }
.timeline-item.tail::after { content: ''; position: absolute; left: 16px; top: 30px; bottom: -14px; width: 2px; background: var(--border-color); }
.timeline-node { position: absolute; left: 0; top: 0; width: 32px; height: 32px; border-radius: 50%; display: grid; place-items: center; font-size: 12px; font-weight: 600; color: #fff; background: #cbd5e1; }
.timeline-node.success { background: var(--success); }
.timeline-node.danger { background: var(--danger); }
.timeline-node.running { background: var(--primary); }
.timeline-node.pending { background: #cbd5e1; color: #475569; }
.step-card { background: var(--bg-muted); border-radius: var(--radius); padding: 12px; }
.step-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
.step-title { font-size: 14px; font-weight: 500; color: var(--text-strong); margin-bottom: 4px; }
.step-subtitle { font-size: 12px; color: var(--text-muted); line-height: 1.5; }
.step-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.icon-link { border: 0; background: transparent; color: var(--primary); font-size: 12px; padding: 0; }
.icon-link.danger { color: var(--danger); }
.step-editor { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.field-block { display: flex; flex-direction: column; gap: 8px; }
.field-block span { font-size: 13px; color: var(--text-main); }
.field-block input, .field-block textarea, .field-block select { width: 100%; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: var(--bg-card); color: var(--text-main); padding:5px 12px; outline: none; }
.field-block textarea { resize: vertical; font-family: "Consolas", "JetBrains Mono", monospace; }
.field-block small { font-size: 11px; color: var(--text-muted); }
.field-block.narrow { width: auto; }
.step-log { margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-color); display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-main); }
.log-badge { display: inline-flex; padding: 2px 8px; border-radius: 999px; font-size: 11px; }
.log-badge.success { background: rgba(39, 174, 96, 0.12); color: var(--success); }
.log-badge.failed, .log-badge.error { background: rgba(231, 76, 60, 0.12); color: var(--danger); }
.log-badge.running { background: rgba(52, 152, 219, 0.12); color: var(--primary); }
.log-badge.info { background: rgba(148, 163, 184, 0.16); color: var(--text-muted); }
.logs-card { display: flex; flex-direction: column; }
.run-select { min-width: 280px; height: 32px; padding: 0 12px; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: var(--bg-card); color: var(--text-main); outline: none; }
.log-console { flex: 1; min-height: 460px; background: #1e1e1e; border-radius: var(--radius); padding: 14px; font-family: "Consolas", "JetBrains Mono", monospace; overflow-y: auto; }
.log-lines { display: flex; flex-direction: column; gap: 6px; }
.log-line { display: flex; gap: 10px; font-size: 12px; line-height: 1.6; }
.log-time { width: 78px; color: #888; flex: none; }
.log-level { width: 64px; flex: none; }
.log-level.info { color: #3498db; }
.log-level.success { color: #27ae60; }
.log-level.failed, .log-level.error { color: #e74c3c; }
.log-level.running { color: #f39c12; }
.log-message { color: #d4d4d4; flex: 1; }
.empty-console { min-height: 200px; display: grid; place-items: center; text-align: center; color: #9ca3af; font-size: 13px; }
.log-footer { margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.footer-metric { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-main); }
.footer-metric strong { color: var(--text-strong); font-size: 14px; }
.footer-metric strong.success { color: var(--success); }
.footer-metric strong.danger { color: var(--danger); }
.config-card { display: flex; flex-direction: column; gap: 16px; }
.config-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.full-row { grid-column: 1 / -1; }
.inline-mix { display: flex; align-items: center; gap: 8px; }
.inline-mix span { font-size: 12px; color: var(--text-muted); }
.switch-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.switch-item { display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--text-main); }
.switch-item input { width: 16px; height: 16px; }
.artifacts-panel { margin-top: 8px; }
.artifacts-panel h4 { margin: 0 0 10px; font-size: 14px; font-weight: 500; color: var(--text-strong); }
.artifact-list { display: flex; flex-wrap: wrap; gap: 8px; }
.artifact-chip { display: inline-flex; align-items: center; padding: 6px 10px; border-radius: 999px; background: rgba(52, 152, 219, 0.1); color: var(--primary); text-decoration: none; font-size: 12px; }
.form-error { margin: 0; font-size: 13px; color: var(--danger); }
.empty-block { min-height: 180px; display: grid; place-items: center; text-align: center; color: var(--text-muted); border: 1px dashed var(--border-color); border-radius: var(--radius); }
@media (max-width: 1100px) { .workspace-grid { grid-template-columns: 1fr; } .config-grid, .switch-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 720px) { .ui-automation-page { padding: 16px; } .toolbar-card, .panel-card { padding: 16px; } .toolbar-card, .panel-head, .toolbar-actions, .project-switch, .batch-inline { flex-direction: column; align-items: flex-start; } .toolbar-select, .run-select, .project-select { width: 100%; min-width: 0; } .step-editor, .config-grid, .switch-grid { grid-template-columns: 1fr; } .field-block.narrow { width: 100%; } .case-selector-list { grid-template-columns: 1fr; } }
</style>
