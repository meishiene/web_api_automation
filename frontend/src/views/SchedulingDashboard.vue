<template>
  <section class="tasks-page">
    <div class="toolbar-card">
      <div class="toolbar-left">
        <label class="project-switch">
          <span>当前项目</span>
          <select v-model="selectedProjectId" @change="handleProjectChange">
            <option v-for="project in projects" :key="project.id" :value="String(project.id)">
              {{ project.name }}
            </option>
          </select>
        </label>
        <button class="primary-btn" @click="openCreateModal">新建任务</button>
        <button class="ghost-btn" @click="refreshAll" :disabled="loading">{{ loading ? '刷新中...' : '刷新' }}</button>
      </div>

      <div class="toolbar-stats">
        <div><i class="dot success"></i><span>运行中</span><strong>{{ enabledTasks.length }}</strong></div>
        <div><i class="dot muted"></i><span>已暂停</span><strong>{{ pausedTasks.length }}</strong></div>
        <div><span>总任务</span><strong>{{ tasks.length }}</strong></div>
      </div>
    </div>

    <div class="table-card">
      <div v-if="loading" class="state-card">正在加载任务...</div>
      <div v-else-if="tasks.length === 0" class="state-card">当前项目还没有定时任务</div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>任务名称</th>
              <th>类型</th>
              <th>执行计划</th>
              <th>状态</th>
              <th>最近结果</th>
              <th>下次执行</th>
              <th>成功率</th>
              <th>负责人</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in tasks" :key="task.id">
              <td>{{ task.id }}</td>
              <td>{{ task.name }}</td>
              <td><span class="type-pill">{{ taskTypeLabel(task) }}</span></td>
              <td>
                <div class="schedule-cell">
                  <span>{{ task.cron_expr }}</span>
                  <small>{{ quickScheduleLabel(task.cron_expr) }}</small>
                </div>
              </td>
              <td>
                <span v-if="task.enabled" class="status-pill running">运行中</span>
                <span v-else class="status-pill paused">已暂停</span>
              </td>
              <td>
                <div class="schedule-cell">
                  <span>{{ taskLastStatus(task)?.label || '--' }}</span>
                  <small>{{ taskLastStatus(task)?.time || '暂无执行记录' }}</small>
                </div>
              </td>
              <td>{{ nextRunHint(task) }}</td>
              <td>
                <div class="rate-cell">
                  <div class="rate-track">
                    <div class="rate-fill" :style="{ width: taskSuccessRateWidth(task) }"></div>
                  </div>
                  <span>{{ taskSuccessRateText(task) }}</span>
                </div>
              </td>
              <td>{{ username }}</td>
              <td>
                <div class="link-group">
                  <button class="link-btn" @click="toggleTask(task)">{{ task.enabled ? '暂停' : '启用' }}</button>
                  <button class="link-btn" @click="triggerTask(task)">立即执行</button>
                  <button class="link-btn" :disabled="!canRetryTask(task)" @click="retryTask(task)">失败重试</button>
                  <button class="link-btn" @click="openEditModal(task)">编辑</button>
                  <button class="link-btn danger" @click="removeTask(task)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="extra-grid">
      <section class="panel-card">
        <div class="panel-head">
          <h3>队列任务</h3>
          <button class="ghost-btn" @click="refreshQueue">刷新队列</button>
        </div>
        <div v-if="queueItems.length === 0" class="mini-state">暂无队列记录</div>
        <div v-else class="mini-table">
          <div class="mini-row head">
            <span>ID</span>
            <span>状态</span>
            <span>类型</span>
            <span>目标</span>
            <span>创建时间</span>
          </div>
          <div v-for="item in queueItems.slice(0, 6)" :key="item.id" class="mini-row">
            <span>#{{ item.id }}</span>
            <span class="status-text" :class="item.status">{{ item.status }}</span>
            <span>{{ item.run_type }}</span>
            <span>{{ item.target_type }}#{{ item.target_id }}</span>
            <span>{{ formatDate(item.created_at) }}</span>
          </div>
        </div>
      </section>

      <section class="panel-card">
        <div class="panel-head">
          <h3>Worker 心跳</h3>
          <button class="ghost-btn" @click="refreshWorkers">刷新 Worker</button>
        </div>
        <div v-if="workerItems.length === 0" class="mini-state">暂无 Worker 心跳</div>
        <div v-else class="mini-table">
          <div class="mini-row head">
            <span>Worker</span>
            <span>状态</span>
            <span>类型</span>
            <span>当前任务</span>
            <span>最近心跳</span>
          </div>
          <div v-for="worker in workerItems" :key="worker.id" class="mini-row">
            <span>{{ worker.worker_id }}</span>
            <span class="status-text" :class="worker.status">{{ worker.status }}</span>
            <span>{{ worker.run_type || '--' }}</span>
            <span>{{ worker.current_queue_item_id || '--' }}</span>
            <span>{{ formatDate(worker.last_heartbeat_at) }}</span>
          </div>
        </div>
      </section>
    </div>

    <div v-if="showModal" class="modal-mask" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-head">
          <h2>{{ modalMode === 'create' ? '新建定时任务' : '编辑定时任务' }}</h2>
          <button class="close-btn" @click="closeModal">×</button>
        </div>

        <form class="modal-form" @submit.prevent="submitTask">
          <label class="field-block">
            <span>任务名称 *</span>
            <input v-model.trim="form.name" type="text" placeholder="请输入任务名称" />
          </label>

          <div class="double-grid">
            <label class="field-block">
              <span>运行类型 *</span>
              <select v-model="form.run_type">
                <option value="api">API测试</option>
                <option value="web">UI测试</option>
              </select>
            </label>
            <label class="field-block">
              <span>时区 *</span>
              <input v-model.trim="form.timezone" type="text" />
            </label>
          </div>

          <div class="double-grid">
            <label class="field-block">
              <span>目标类型 *</span>
              <select v-model="form.target_type">
                <option v-for="option in targetTypeOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
              </select>
            </label>
            <label class="field-block">
              <span>目标</span>
              <select v-model="form.target_id">
                <option value="">请选择目标</option>
                <option v-for="target in availableTargets" :key="`${target.type}-${target.id}`" :value="String(target.id)">
                  {{ target.label }}
                </option>
              </select>
            </label>
          </div>

          <label class="field-block">
            <span>Cron 表达式 *</span>
            <input v-model.trim="form.cron_expr" type="text" placeholder="例如：0 2 * * *" />
            <small>快捷设置：</small>
            <div class="quick-actions">
              <button type="button" class="ghost-btn small" @click="form.cron_expr = '0 * * * *'">每小时</button>
              <button type="button" class="ghost-btn small" @click="form.cron_expr = '0 2 * * *'">每天</button>
              <button type="button" class="ghost-btn small" @click="form.cron_expr = '0 2 * * 1'">每周</button>
              <button type="button" class="ghost-btn small" @click="form.cron_expr = '0 2 1 * *'">每月</button>
            </div>
          </label>

          <div class="template-strip">
            <button type="button" class="ghost-btn small" @click="applyTemplate('smoke')">Smoke 模板</button>
            <button type="button" class="ghost-btn small" @click="applyTemplate('suite-nightly')">夜间回归模板</button>
            <button type="button" class="ghost-btn small" @click="applyTemplate('web-hourly')">Web 巡检模板</button>
          </div>

          <div class="double-grid">
            <label class="field-block">
              <span>优先级</span>
              <input v-model.number="form.priority" type="number" min="1" max="10" />
            </label>
            <label class="field-block checkbox-line">
              <span>任务状态</span>
              <label class="check-inline">
                <input v-model="form.enabled" type="checkbox" />
                <span>启用任务</span>
              </label>
            </label>
          </div>

          <label class="field-block">
            <span>附加 Payload（预留 JSON）</span>
            <textarea v-model.trim="form.payloadText" rows="4" placeholder='例如：{"environment_id": 1}'></textarea>
          </label>

          <label class="field-block">
            <span>执行环境（可选）</span>
            <select v-model="form.environment_id">
              <option value="">默认环境</option>
              <option v-for="environment in projectEnvironments" :key="environment.id" :value="String(environment.id)">
                {{ environment.name }}
              </option>
            </select>
          </label>

          <p v-if="formError" class="form-error">{{ formError }}</p>

          <div class="modal-actions">
            <button type="button" class="ghost-btn" @click="closeModal">取消</button>
            <button type="submit" class="primary-btn" :disabled="saving">
              {{ saving ? '保存中...' : modalMode === 'create' ? '创建任务' : '保存修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProjectEnvironments } from '@/api/environments'
import { getProjects } from '@/api/projects'
import { getQueueItems, getWorkerHeartbeats } from '@/api/queueWorker'
import {
  createScheduleTask,
  deleteScheduleTask,
  getScheduleTasks,
  triggerScheduleTask,
  updateScheduleTask,
} from '@/api/scheduleTasks'
import { getTestCases } from '@/api/testCases'
import { getTestSuites } from '@/api/testSuites'
import { getWebTestCases } from '@/api/webTestCases'
import { setActiveProjectId } from '@/utils/projectContext'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => Number(route.params.projectId))

const projects = ref([])
const selectedProjectId = ref('')
const loading = ref(false)
const saving = ref(false)
const tasks = ref([])
const queueItems = ref([])
const workerItems = ref([])
const apiCases = ref([])
const webCases = ref([])
const apiSuites = ref([])
const projectEnvironments = ref([])
const showModal = ref(false)
const modalMode = ref('create')
const editingTaskId = ref(null)
const formError = ref('')
const projectName = ref(`项目 #${projectId.value}`)
const username = localStorage.getItem('username') || '测试工程师'
const form = ref(defaultForm())

function defaultForm() {
  return {
    name: '',
    run_type: 'api',
    cron_expr: '0 2 * * *',
    timezone: 'Asia/Shanghai',
    enabled: true,
    target_type: 'test_case',
    target_id: '',
    priority: 5,
    environment_id: '',
    payloadText: '',
  }
}

const enabledTasks = computed(() => tasks.value.filter((item) => item.enabled))
const pausedTasks = computed(() => tasks.value.filter((item) => !item.enabled))
const targetTypeOptions = computed(() => {
  if (form.value.run_type === 'web') {
    return [{ value: 'test_case', label: 'web test_case' }]
  }
  return [
    { value: 'test_case', label: 'api test_case' },
    { value: 'test_suite', label: 'api test_suite' },
  ]
})
const availableTargets = computed(() => {
  if (form.value.run_type === 'web') {
    return webCases.value.map((item) => ({ id: item.id, type: 'test_case', label: `${item.name} (#${item.id})` }))
  }
  if (form.value.target_type === 'test_suite') {
    return apiSuites.value.map((item) => ({ id: item.id, type: 'test_suite', label: `${item.name} (#${item.id})` }))
  }
  return apiCases.value.map((item) => ({ id: item.id, type: 'test_case', label: `${item.name} (#${item.id})` }))
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

const quickScheduleLabel = (cronExpr) => {
  if (cronExpr === '0 * * * *') return '每小时执行一次'
  if (cronExpr === '0 2 * * *') return '每天凌晨 2 点'
  if (cronExpr === '0 2 * * 1') return '每周一凌晨 2 点'
  if (cronExpr === '0 2 1 * *') return '每月 1 日凌晨 2 点'
  return '自定义计划'
}

const taskTypeLabel = (task) => {
  if (task.payload?.run_type === 'web') return 'UI测试'
  if (task.payload?.run_type === 'api') return 'API测试'
  return task.target_type
}

const taskSuccessRateText = (task) => {
  const relevant = queueItems.value.filter((item) => {
    if (item.target_type !== task.target_type) return false
    return String(item.target_id || '') === String(task.target_id || '')
  })
  if (!relevant.length) return '--'
  const success = relevant.filter((item) => item.status === 'success').length
  return `${((success / relevant.length) * 100).toFixed(1)}%`
}

const taskSuccessRateWidth = (task) => {
  const text = taskSuccessRateText(task)
  return text === '--' ? '0%' : text
}

const nextRunHint = (task) => {
  return task.enabled ? quickScheduleLabel(task.cron_expr) : '任务已暂停'
}

const parsePayloadText = () => {
  if (!form.value.payloadText) return {}
  try {
    const parsed = JSON.parse(form.value.payloadText)
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      return parsed
    }
    throw new Error('payload 必须是 JSON 对象')
  } catch (err) {
    throw new Error('附加 Payload 必须是合法 JSON 对象')
  }
}

const toRequestPayload = () => {
  const payload = parsePayloadText()
  payload.run_type = form.value.run_type
  payload.priority = Number(form.value.priority) || 5
  if (form.value.environment_id) {
    payload.environment_id = Number(form.value.environment_id)
  }
  return {
    project_id: projectId.value,
    name: form.value.name,
    cron_expr: form.value.cron_expr,
    timezone: form.value.timezone || 'Asia/Shanghai',
    enabled: form.value.enabled,
    target_type: form.value.target_type,
    target_id: form.value.target_id ? Number(form.value.target_id) : null,
    payload,
  }
}

const fetchProjectName = async () => {
  try {
    projects.value = await getProjects()
    selectedProjectId.value = String(projectId.value)
    const current = projects.value.find((item) => item.id === projectId.value)
    if (current) projectName.value = current.name
  } catch (err) {
    console.error('Failed to fetch project name')
  }
}

const handleProjectChange = () => {
  if (!selectedProjectId.value) return
  const nextProjectId = Number(selectedProjectId.value)
  if (!Number.isFinite(nextProjectId) || nextProjectId === projectId.value) return
  setActiveProjectId(nextProjectId)
  router.push(`/project/${nextProjectId}/scheduling`)
}

const refreshTasks = async () => {
  const response = await getScheduleTasks(projectId.value)
  tasks.value = response.items || []
}

const refreshQueue = async () => {
  const response = await getQueueItems(projectId.value)
  queueItems.value = response.items || []
}

const refreshWorkers = async () => {
  const response = await getWorkerHeartbeats(projectId.value)
  workerItems.value = response.items || []
}

const refreshTargets = async () => {
  const [apiCaseResp, suiteResp, webCaseResp, environmentResp] = await Promise.all([
    getTestCases(projectId.value),
    getTestSuites(projectId.value),
    getWebTestCases(projectId.value),
    getProjectEnvironments(projectId.value),
  ])
  apiCases.value = apiCaseResp
  apiSuites.value = suiteResp
  webCases.value = webCaseResp
  projectEnvironments.value = environmentResp
}

const refreshAll = async () => {
  loading.value = true
  try {
    await Promise.all([fetchProjectName(), refreshTasks(), refreshQueue(), refreshWorkers(), refreshTargets()])
  } catch (err) {
    alert(err.response?.data?.detail || '加载任务管理失败')
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  modalMode.value = 'create'
  editingTaskId.value = null
  form.value = defaultForm()
  form.value.target_type = form.value.run_type === 'web' ? 'test_case' : 'test_case'
  formError.value = ''
  showModal.value = true
}

const openEditModal = (task) => {
  modalMode.value = 'edit'
  editingTaskId.value = task.id
  form.value = {
    name: task.name,
    run_type: task.payload?.run_type || 'api',
    cron_expr: task.cron_expr,
    timezone: task.timezone || 'Asia/Shanghai',
    enabled: !!task.enabled,
    target_type: task.target_type,
    target_id: task.target_id ? String(task.target_id) : '',
    priority: task.payload?.priority || 5,
    environment_id: task.payload?.environment_id ? String(task.payload.environment_id) : '',
    payloadText: JSON.stringify(
      Object.fromEntries(
        Object.entries(task.payload || {}).filter(([key]) => !['run_type', 'priority', 'environment_id'].includes(key))
      ),
      null,
      2
    ),
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  saving.value = false
  formError.value = ''
}

const submitTask = async () => {
  if (!form.value.name.trim() || !form.value.cron_expr.trim()) {
    formError.value = '任务名称和 Cron 表达式不能为空'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    const payload = toRequestPayload()
    if (modalMode.value === 'create') {
      await createScheduleTask(payload)
    } else {
      const { project_id, ...updatePayload } = payload
      void project_id
      await updateScheduleTask(editingTaskId.value, updatePayload)
    }
    closeModal()
    await refreshAll()
  } catch (err) {
    formError.value = err.message || err.response?.data?.detail || '保存任务失败'
  } finally {
    saving.value = false
  }
}

const toggleTask = async (task) => {
  try {
    await updateScheduleTask(task.id, {
      name: task.name,
      cron_expr: task.cron_expr,
      timezone: task.timezone,
      enabled: !task.enabled,
      target_type: task.target_type,
      target_id: task.target_id,
      payload: task.payload || {},
    })
    await refreshTasks()
  } catch (err) {
    alert(err.response?.data?.detail || '更新任务状态失败')
  }
}

const triggerTask = async (task) => {
  try {
    await triggerScheduleTask(task.id)
    await Promise.all([refreshQueue(), refreshTasks()])
  } catch (err) {
    alert(err.response?.data?.detail || '触发任务失败')
  }
}

const taskLastStatus = (task) => {
  const relevant = queueItems.value
    .filter((item) => item.target_type === task.target_type && String(item.target_id || '') === String(task.target_id || ''))
    .sort((a, b) => Number(b.created_at || 0) - Number(a.created_at || 0))
  const latest = relevant[0]
  if (!latest) return null
  return {
    label: latest.status,
    time: formatDate(latest.created_at),
  }
}

const canRetryTask = (task) => {
  const latest = taskLastStatus(task)
  return latest && ['failed', 'error'].includes(latest.label)
}

const retryTask = async (task) => {
  if (!canRetryTask(task)) return
  await triggerTask(task)
}

const applyTemplate = (templateKey) => {
  if (templateKey === 'smoke') {
    form.value.run_type = 'api'
    form.value.target_type = 'test_case'
    form.value.cron_expr = '0 9 * * *'
    form.value.priority = 7
    return
  }
  if (templateKey === 'suite-nightly') {
    form.value.run_type = 'api'
    form.value.target_type = 'test_suite'
    form.value.cron_expr = '0 2 * * *'
    form.value.priority = 8
    return
  }
  form.value.run_type = 'web'
  form.value.target_type = 'test_case'
  form.value.cron_expr = '0 * * * *'
  form.value.priority = 5
}

const removeTask = async (task) => {
  if (!confirm(`确定删除任务「${task.name}」吗？`)) return
  try {
    await deleteScheduleTask(task.id)
    await refreshTasks()
  } catch (err) {
    alert(err.response?.data?.detail || '删除任务失败')
  }
}

watch(() => form.value.run_type, (value) => {
  if (value === 'web') {
    form.value.target_type = 'test_case'
    return
  }
  if (form.value.target_type !== 'test_case' && form.value.target_type !== 'test_suite') {
    form.value.target_type = 'test_case'
  }
})

watch(projectId, async () => {
  await refreshAll()
})

onMounted(async () => {
  setActiveProjectId(projectId.value)
  await refreshAll()
})
</script>

<style scoped>
.tasks-page { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.toolbar-card,
.table-card,
.panel-card,
.modal-card,
.state-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); box-shadow: var(--surface-shadow); }
.toolbar-card { padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.toolbar-left,
.toolbar-stats { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.project-switch { display: flex; flex-direction: column; gap: 6px; min-width: 220px; font-size: 13px; color: var(--text-muted); }
.project-switch select { height: 32px; padding: 0 12px; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: var(--bg-card); color: var(--text-main); outline: none; }
.toolbar-stats div { display: inline-flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-main); }
.toolbar-stats strong { font-size: 16px; color: var(--text-strong); }
.dot { width: 8px; height: 8px; border-radius: 999px; display: inline-block; }
.dot.success { background: var(--success); }
.dot.muted { background: var(--text-muted); }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table thead tr { background: var(--bg-muted); border-bottom: 1px solid var(--border-color); }
.data-table th { padding: 12px 16px; text-align: left; font-size: 13px; font-weight: 500; color: var(--text-main); }
.data-table td { padding: 14px 16px; border-bottom: 1px solid var(--border-color); font-size: 13px; color: var(--text-main); vertical-align: top; }
.type-pill,
.status-pill { display: inline-flex; align-items: center; justify-content: center; padding: 4px 10px; border-radius: 999px; font-size: 12px; }
.type-pill { background: var(--bg-muted); color: var(--text-main); }
.status-pill.running { background: #e8f5e9; color: #27ae60; }
.status-pill.paused { background: #f5f5f5; color: #909399; }
.schedule-cell { display: flex; flex-direction: column; gap: 4px; }
.schedule-cell small { color: var(--text-muted); }
.template-strip { display: flex; gap: 8px; flex-wrap: wrap; }
.rate-cell { display: flex; align-items: center; gap: 10px; min-width: 140px; }
.rate-track { flex: 1; height: 6px; border-radius: 999px; background: var(--border-color); overflow: hidden; }
.rate-fill { height: 100%; border-radius: 999px; background: var(--success); }
.link-group { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.link-btn,
.primary-btn,
.ghost-btn { min-height: 32px; padding: 0 14px; border-radius: var(--radius); font-size: 13px; }
.link-btn { border: 0; background: transparent; color: var(--primary); padding: 0; min-height: auto; }
.link-btn.danger { color: var(--danger); }
.primary-btn { border: 1px solid var(--primary); background: var(--primary); color: #fff; }
.ghost-btn { border: 1px solid var(--border-color-strong); background: transparent; color: var(--text-main); }
.ghost-btn.small { min-height: 28px; padding: 0 10px; }
.extra-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.panel-card { padding: 20px; }
.panel-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
.panel-head h3 { margin: 0; font-size: 16px; color: var(--text-strong); }
.mini-table { display: flex; flex-direction: column; gap: 10px; }
.mini-row { display: grid; grid-template-columns: 72px 90px 72px 1fr 150px; gap: 10px; font-size: 12px; color: var(--text-main); }
.mini-row.head { color: var(--text-muted); font-weight: 500; }
.mini-state,
.state-card { min-height: 140px; display: grid; place-items: center; color: var(--text-muted); text-align: center; }
.status-text.success,
.status-text.online { color: var(--success); }
.status-text.failed,
.status-text.error,
.status-text.offline { color: var(--danger); }
.status-text.queued,
.status-text.running,
.status-text.busy { color: var(--primary); }
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.32); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 999; }
.modal-card { width: min(760px, 100%); padding: 24px; }
.modal-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; }
.modal-head h2 { margin: 0; font-size: 18px; color: var(--text-strong); }
.close-btn { border: 0; background: transparent; color: var(--text-muted); font-size: 20px; }
.modal-form { display: flex; flex-direction: column; gap: 16px; }
.field-block { display: flex; flex-direction: column; gap: 8px; }
.field-block span { font-size: 13px; color: var(--text-main); }
.field-block input,
.field-block select,
.field-block textarea {
  width: 100%;
  border: 1px solid var(--border-color-strong);
  border-radius: var(--radius);
  background: var(--bg-card);
  color: var(--text-main);
  outline: none;
}
.field-block input,
.field-block select { height: 36px; padding: 0 12px; }
.field-block textarea { min-height: 96px; padding: 10px 12px; resize: vertical; }
.field-block small { font-size: 12px; color: var(--text-muted); }
.double-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.checkbox-line { justify-content: flex-end; }
.check-inline { display: inline-flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-main); }
.quick-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.form-error { margin: 0; color: var(--danger); font-size: 13px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; }

@media (max-width: 1180px) {
  .extra-grid { grid-template-columns: 1fr; }
}

@media (max-width: 900px) {
  .tasks-page { padding: 16px; }
  .toolbar-card,
  .toolbar-left,
  .toolbar-stats,
  .panel-head { flex-direction: column; align-items: flex-start; }
  .double-grid { grid-template-columns: 1fr; }
}
</style>
