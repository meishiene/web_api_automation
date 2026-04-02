<template>
  <section class="gov-page">
    <div class="toolbar-card">
      <label class="field">
        <span>当前项目</span>
        <select v-model="selectedProjectId" @change="changeProject">
          <option v-for="project in projects" :key="project.id" :value="String(project.id)">{{ project.name }}</option>
        </select>
      </label>
      <div class="toolbar-actions">
        <button class="primary-btn" @click="openConfigModal()">新增配置</button>
        <button class="ghost-btn" @click="refreshAll" :disabled="loading">{{ loading ? '刷新中...' : '刷新' }}</button>
        <button class="primary-btn" @click="retryBacklog" :disabled="loading || retrying">{{ retrying ? '重试中...' : '重试失败积压' }}</button>
      </div>
    </div>

    <div v-if="errorText" class="banner error">{{ errorText }}</div>
    <div v-if="successText" class="banner success">{{ successText }}</div>

    <div class="stats-grid" v-if="health">
      <article class="stat-card"><span>启用配置</span><strong>{{ health.config_counts.enabled }}</strong></article>
      <article class="stat-card"><span>失败事件</span><strong>{{ health.retry_backlog.events }}</strong></article>
      <article class="stat-card"><span>死信投递</span><strong>{{ health.retry_backlog.deliveries }}</strong></article>
      <article class="stat-card"><span>开放缺陷</span><strong>{{ health.defect_open_count }}</strong></article>
    </div>

    <section class="panel-card">
      <div class="tab-strip">
        <button v-for="tab in tabs" :key="tab.value" class="tab-btn" :class="{ active: activeTab === tab.value }" @click="activeTab = tab.value">{{ tab.label }}</button>
      </div>

      <div v-if="activeTab === 'overview'" class="tab-panel">
        <div class="two-col">
          <article class="box">
            <h3>事件状态</h3>
            <ul><li v-for="(count, status) in health?.event_status_counts || {}" :key="status">{{ status }}：{{ count }}</li></ul>
            <h3>投递状态</h3>
            <ul><li v-for="(count, status) in health?.delivery_status_counts || {}" :key="`d-${status}`">{{ status }}：{{ count }}</li></ul>
          </article>
          <article class="box">
            <h3>最近失败</h3>
            <div v-if="!(health?.recent_failures || []).length" class="empty">暂无失败记录</div>
            <div v-else class="stack">
              <article v-for="item in health.recent_failures" :key="`${item.source}-${item.record_id}`" class="row-card">
                <div><strong>{{ item.source }} #{{ item.record_id }}</strong><p>{{ item.message || '--' }}</p></div>
                <span class="pill" :class="item.status">{{ item.status }}</span>
              </article>
            </div>
          </article>
        </div>
      </div>

      <div v-else-if="activeTab === 'configs'" class="tab-panel">
        <div v-if="!configs.length" class="empty">暂无集成配置</div>
        <div v-else class="table-wrap">
          <table class="data-table">
            <thead><tr><th>名称</th><th>类型</th><th>Provider</th><th>状态</th><th>URL</th><th>凭据</th><th>操作</th></tr></thead>
            <tbody>
              <tr v-for="config in configs" :key="config.id">
                <td>{{ config.name }}</td>
                <td>{{ config.integration_type }}</td>
                <td>{{ config.provider }}</td>
                <td>{{ config.is_enabled ? 'enabled' : 'disabled' }}</td>
                <td>{{ config.base_url || '--' }}</td>
                <td><button class="table-link" @click="revealCredential(config)">查看</button></td>
                <td>
                  <div class="link-group">
                    <button class="table-link" @click="openConfigModal(config)">编辑</button>
                    <button class="table-link danger" @click="removeConfig(config)">删除</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else-if="activeTab === 'notifications'" class="tab-panel">
        <div class="box form-box">
          <h3>新增通知订阅</h3>
          <div class="form-grid">
            <input v-model.trim="subForm.name" placeholder="名称" />
            <input v-model.trim="subForm.event_type" placeholder="事件类型" />
            <select v-model="subForm.channel_type"><option value="webhook">webhook</option><option value="email">email</option></select>
            <input v-model.trim="subForm.destination" placeholder="目标地址" />
          </div>
          <button class="primary-btn" @click="createSubscription" :disabled="subSaving">{{ subSaving ? '保存中...' : '创建订阅' }}</button>
        </div>
        <div v-if="!subscriptions.items.length" class="empty">暂无通知订阅</div>
        <div v-else class="stack">
          <article v-for="item in subscriptions.items" :key="item.id" class="row-card">
            <div><strong>{{ item.name }}</strong><p>{{ item.event_type }} · {{ item.channel_type }} · {{ item.destination }}</p></div>
            <button class="table-link" @click="dispatchSub(item)">派发测试事件</button>
          </article>
        </div>
      </div>

      <div v-else-if="activeTab === 'deliveries'" class="tab-panel">
        <div v-if="!deliveries.items.length" class="empty">暂无投递记录</div>
        <div v-else class="table-wrap">
          <table class="data-table">
            <thead><tr><th>ID</th><th>事件</th><th>状态</th><th>错误</th><th>尝试</th><th>操作</th></tr></thead>
            <tbody>
              <tr v-for="item in deliveries.items" :key="item.id">
                <td>#{{ item.id }}</td><td>{{ item.event_type }}</td><td>{{ item.status }}</td><td>{{ item.last_error || '--' }}</td><td>{{ item.attempt_count }}/{{ item.max_attempts }}</td>
                <td><button class="table-link" :disabled="!['retry_pending','dead_letter'].includes(item.status)" @click="retryDelivery(item.id)">重试</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else-if="activeTab === 'defects'" class="tab-panel">
        <div v-if="!defects.items.length" class="empty">暂无缺陷同步记录</div>
        <div v-else class="table-wrap">
          <table class="data-table">
            <thead><tr><th>Issue</th><th>用例</th><th>状态</th><th>分类</th><th>次数</th><th>定位</th></tr></thead>
            <tbody>
              <tr v-for="item in defects.items" :key="item.id">
                <td>{{ item.issue_key }}</td><td>{{ item.case_name }}</td><td>{{ item.issue_status }}</td><td>{{ item.failure_category || '--' }}</td><td>{{ item.occurrence_count }}</td>
                <td><button class="table-link" @click="openDetail(item.detail_api_path)">定位</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else-if="activeTab === 'cicd'" class="tab-panel">
        <label class="field narrow">
          <span>CI 配置</span>
          <select v-model="selectedCicdConfigId" @change="fetchCicdRunsForSelected">
            <option value="">请选择</option>
            <option v-for="config in cicdConfigs" :key="config.id" :value="String(config.id)">{{ config.name }}</option>
          </select>
        </label>
        <div v-if="!selectedCicdConfigId" class="empty">请选择一个 CI/CD 配置</div>
        <div v-else-if="!cicdRuns.items.length" class="empty">暂无 CI/CD 运行记录</div>
        <div v-else class="table-wrap">
          <table class="data-table">
            <thead><tr><th>ID</th><th>事件</th><th>状态</th><th>错误</th><th>更新时间</th></tr></thead>
            <tbody>
              <tr v-for="item in cicdRuns.items" :key="item.id"><td>#{{ item.id }}</td><td>{{ item.event_type }}</td><td>{{ item.status }}</td><td>{{ item.last_error || '--' }}</td><td>{{ formatDate(item.updated_at) }}</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else-if="activeTab === 'identity'" class="tab-panel">
        <label class="field narrow">
          <span>身份配置</span>
          <select v-model="selectedIdentityConfigId" @change="fetchIdentityBindingsForSelected">
            <option value="">请选择</option>
            <option v-for="config in identityConfigs" :key="config.id" :value="String(config.id)">{{ config.name }}</option>
          </select>
        </label>
        <div v-if="!selectedIdentityConfigId" class="empty">请选择一个身份配置</div>
        <div v-else-if="!identityBindings.items.length" class="empty">暂无身份绑定记录</div>
        <div v-else class="table-wrap">
          <table class="data-table">
            <thead><tr><th>用户</th><th>Provider</th><th>Subject</th><th>邮箱</th><th>最近登录</th></tr></thead>
            <tbody>
              <tr v-for="item in identityBindings.items" :key="item.id"><td>#{{ item.user_id }}</td><td>{{ item.provider }}</td><td>{{ item.external_subject }}</td><td>{{ item.external_email || '--' }}</td><td>{{ formatDate(item.last_login_at) }}</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="tab-panel">
        <div v-if="!governanceExecutions.items.length" class="empty">暂无治理执行记录</div>
        <div v-else class="table-wrap">
          <table class="data-table">
            <thead><tr><th>ID</th><th>类型</th><th>状态</th><th>幂等键</th><th>完成时间</th></tr></thead>
            <tbody>
              <tr v-for="item in governanceExecutions.items" :key="item.id"><td>#{{ item.id }}</td><td>{{ item.execution_type }}</td><td>{{ item.status }}</td><td class="mono">{{ item.idempotency_key }}</td><td>{{ formatDate(item.completed_at) }}</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <div v-if="showConfigModal" class="modal-mask" @click.self="closeConfigModal">
      <div class="modal-card">
        <div class="modal-head">
          <h2>{{ editingConfigId ? '编辑集成配置' : '新增集成配置' }}</h2>
          <button class="close-btn" @click="closeConfigModal">×</button>
        </div>
        <div class="modal-form">
          <div class="form-grid">
            <label class="field"><span>名称</span><input v-model.trim="configForm.name" type="text" placeholder="例如：github-actions-main" /></label>
            <label class="field"><span>类型</span><select v-model="configForm.integration_type"><option value="cicd">cicd</option><option value="notification">notification</option><option value="defect">defect</option><option value="identity">identity</option><option value="webhook">webhook</option></select></label>
            <label class="field"><span>Provider</span><input v-model.trim="configForm.provider" type="text" placeholder="例如：github_actions" /></label>
            <label class="field"><span>Base URL</span><input v-model.trim="configForm.base_url" type="text" placeholder="可选" /></label>
            <label class="field"><span>Credential Ref</span><input v-model.trim="configForm.credential_ref" type="text" placeholder="可选" /></label>
            <label class="field"><span>Credential Value</span><input v-model.trim="configForm.credential_value" type="text" placeholder="请填写完整凭据值" /></label>
            <label class="field"><span>启用状态</span><select v-model="configForm.is_enabled"><option :value="true">enabled</option><option :value="false">disabled</option></select></label>
          </div>
          <label class="field"><span>Config JSON</span><textarea v-model.trim="configForm.configText" rows="8" placeholder='例如：{"workflow":"regression.yml"}'></textarea></label>
          <p v-if="configFormError" class="form-error">{{ configFormError }}</p>
          <div class="modal-actions">
            <button class="ghost-btn" @click="closeConfigModal">取消</button>
            <button class="primary-btn" @click="submitConfig" :disabled="configSaving">{{ configSaving ? '保存中...' : editingConfigId ? '保存修改' : '创建配置' }}</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProjects } from '@/api/projects'
import { createIntegration, createNotificationSubscription, deleteIntegration, dispatchNotification, getCicdRuns, getDefectSyncRecords, getIdentityBindings, getIntegrationGovernanceExecutions, getIntegrationGovernanceHealth, getIntegrations, getNotificationDeliveries, getNotificationSubscriptions, retryIntegrationGovernanceBacklog, retryNotificationDelivery, revealIntegrationCredential, updateIntegration } from '@/api/integrations'
import { setActiveProjectId } from '@/utils/projectContext'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => Number(route.params.projectId))
const projects = ref([])
const selectedProjectId = ref('')
const loading = ref(false)
const retrying = ref(false)
const subSaving = ref(false)
const configSaving = ref(false)
const health = ref(null)
const configs = ref([])
const subscriptions = ref({ total: 0, items: [] })
const deliveries = ref({ total: 0, items: [] })
const defects = ref({ total: 0, items: [] })
const cicdRuns = ref({ total: 0, items: [] })
const identityBindings = ref({ total: 0, items: [] })
const governanceExecutions = ref({ total: 0, items: [] })
const selectedCicdConfigId = ref('')
const selectedIdentityConfigId = ref('')
const activeTab = ref('overview')
const errorText = ref('')
const successText = ref('')
const showConfigModal = ref(false)
const editingConfigId = ref(null)
const configFormError = ref('')
const configForm = ref(defaultConfigForm())
const subForm = ref({ name: '', event_type: 'test_run.finished', channel_type: 'webhook', destination: 'mock://success', is_enabled: true, max_attempts: 3 })
const tabs = [
  { value: 'overview', label: '概览' }, { value: 'configs', label: '集成配置' }, { value: 'notifications', label: '通知订阅' }, { value: 'deliveries', label: '投递记录' },
  { value: 'defects', label: '缺陷记录' }, { value: 'cicd', label: 'CI/CD 运行' }, { value: 'identity', label: '身份绑定' }, { value: 'governance', label: '治理执行' },
]

const cicdConfigs = computed(() => configs.value.filter((item) => item.integration_type === 'cicd'))
const identityConfigs = computed(() => configs.value.filter((item) => item.integration_type === 'identity'))
const msg = (err, fallback) => err?.response?.data?.detail || err?.response?.data?.error?.message || err?.message || fallback
const setMsg = (success = '', error = '') => { successText.value = success; errorText.value = error }
const normalizeTimestamp = (value) => { const n = Number(value || 0); return n > 1e12 ? n : n * 1000 }
const formatDate = (value) => !value ? '--' : new Date(normalizeTimestamp(value)).toLocaleString('zh-CN')

function defaultConfigForm() {
  return {
    name: '',
    integration_type: 'cicd',
    provider: '',
    base_url: '',
    credential_ref: '',
    credential_value: '',
    configText: '{}',
    is_enabled: true,
  }
}

const fetchProjectOptions = async () => {
  projects.value = await getProjects()
  selectedProjectId.value = String(projectId.value)
}

const fetchCicdRunsForSelected = async () => {
  cicdRuns.value = !selectedCicdConfigId.value ? { total: 0, items: [] } : await getCicdRuns(selectedCicdConfigId.value, { page: 1, page_size: 20 })
}

const fetchIdentityBindingsForSelected = async () => {
  identityBindings.value = !selectedIdentityConfigId.value ? { total: 0, items: [] } : await getIdentityBindings(selectedIdentityConfigId.value, { page: 1, page_size: 20 })
}

const refreshAll = async () => {
  loading.value = true
  setMsg()
  try {
    await fetchProjectOptions()
    const [healthResp, configResp, subResp, delResp, defectResp, execResp] = await Promise.all([
      getIntegrationGovernanceHealth(projectId.value),
      getIntegrations(projectId.value),
      getNotificationSubscriptions(projectId.value, { page: 1, page_size: 20 }),
      getNotificationDeliveries(projectId.value, { page: 1, page_size: 20 }),
      getDefectSyncRecords(projectId.value, { page: 1, page_size: 20 }),
      getIntegrationGovernanceExecutions(projectId.value, { page: 1, page_size: 20 }),
    ])
    health.value = healthResp
    configs.value = configResp
    subscriptions.value = subResp
    deliveries.value = delResp
    defects.value = defectResp
    governanceExecutions.value = execResp
    if (!selectedCicdConfigId.value && cicdConfigs.value.length) selectedCicdConfigId.value = String(cicdConfigs.value[0].id)
    if (!selectedIdentityConfigId.value && identityConfigs.value.length) selectedIdentityConfigId.value = String(identityConfigs.value[0].id)
    await Promise.all([fetchCicdRunsForSelected(), fetchIdentityBindingsForSelected()])
  } catch (err) {
    setMsg('', msg(err, '加载集成治理数据失败'))
  } finally {
    loading.value = false
  }
}

const changeProject = () => {
  const nextProjectId = Number(selectedProjectId.value)
  if (!Number.isFinite(nextProjectId) || nextProjectId === projectId.value) return
  setActiveProjectId(nextProjectId)
  router.push(`/project/${nextProjectId}/integration-governance`)
}

const retryBacklog = async () => {
  retrying.value = true
  try {
    await retryIntegrationGovernanceBacklog(projectId.value, { max_events: 20, max_deliveries: 20 })
    setMsg('失败积压已触发重试')
    await refreshAll()
  } catch (err) {
    setMsg('', msg(err, '重试失败积压失败'))
  } finally {
    retrying.value = false
  }
}

const openConfigModal = async (config = null) => {
  editingConfigId.value = config?.id || null
  configFormError.value = ''
  configForm.value = {
    name: config?.name || '',
    integration_type: config?.integration_type || 'cicd',
    provider: config?.provider || '',
    base_url: config?.base_url || '',
    credential_ref: config?.credential_ref || '',
    credential_value: '',
    configText: JSON.stringify(config?.config_json || {}, null, 2),
    is_enabled: config?.is_enabled ?? true,
  }
  if (config?.has_credential_value) {
    try {
      const revealed = await revealIntegrationCredential(config.id)
      configForm.value.credential_value = revealed.value
    } catch (err) {
      configFormError.value = '读取凭据失败，请手动重新输入'
    }
  }
  showConfigModal.value = true
}

const closeConfigModal = () => {
  showConfigModal.value = false
  editingConfigId.value = null
  configSaving.value = false
  configFormError.value = ''
}

const submitConfig = async () => {
  if (!configForm.value.name.trim() || !configForm.value.provider.trim()) {
    configFormError.value = '名称和 Provider 不能为空'
    return
  }
  configSaving.value = true
  configFormError.value = ''
  try {
    const payload = {
      name: configForm.value.name.trim(),
      integration_type: configForm.value.integration_type,
      provider: configForm.value.provider.trim(),
      base_url: configForm.value.base_url?.trim() || null,
      credential_ref: configForm.value.credential_ref?.trim() || null,
      credential_value: configForm.value.credential_value || null,
      config_json: JSON.parse(configForm.value.configText || '{}'),
      is_enabled: !!configForm.value.is_enabled,
    }
    if (editingConfigId.value) {
      await updateIntegration(editingConfigId.value, payload)
      setMsg('集成配置已更新')
    } else {
      await createIntegration(projectId.value, payload)
      setMsg('集成配置已创建')
    }
    closeConfigModal()
    await refreshAll()
  } catch (err) {
    configFormError.value = msg(err, '保存集成配置失败')
  } finally {
    configSaving.value = false
  }
}

const removeConfig = async (config) => {
  if (!confirm(`确定删除集成配置「${config.name}」吗？`)) return
  try {
    await deleteIntegration(config.id)
    setMsg('集成配置已删除')
    await refreshAll()
  } catch (err) {
    setMsg('', msg(err, '删除集成配置失败'))
  }
}

const createSubscription = async () => {
  subSaving.value = true
  try {
    await createNotificationSubscription(projectId.value, { ...subForm.value })
    subForm.value = { name: '', event_type: 'test_run.finished', channel_type: 'webhook', destination: 'mock://success', is_enabled: true, max_attempts: 3 }
    setMsg('通知订阅已创建')
    await refreshAll()
  } catch (err) {
    setMsg('', msg(err, '创建通知订阅失败'))
  } finally {
    subSaving.value = false
  }
}

const dispatchSub = async (subscription) => {
  try {
    await dispatchNotification(subscription.id, { event_type: subscription.event_type, payload: { source: 'manual-dispatch', project_id: projectId.value, ts: Date.now() } })
    setMsg('测试通知已派发')
    await refreshAll()
  } catch (err) {
    setMsg('', msg(err, '派发通知失败'))
  }
}

const retryDelivery = async (deliveryId) => {
  try {
    await retryNotificationDelivery(deliveryId)
    setMsg('投递已重试')
    await refreshAll()
  } catch (err) {
    setMsg('', msg(err, '重试投递失败'))
  }
}

const revealCredential = async (config) => {
  try {
    const value = await revealIntegrationCredential(config.id)
    alert(`${config.name} 凭据：${value.value}`)
  } catch (err) {
    setMsg('', msg(err, '查看凭据失败'))
  }
}

const openDetail = (detailApiPath) => {
  if (!detailApiPath) return
  router.push(detailApiPath)
}

watch(projectId, async () => {
  selectedCicdConfigId.value = ''
  selectedIdentityConfigId.value = ''
  await refreshAll()
})

onMounted(async () => {
  setActiveProjectId(projectId.value)
  await refreshAll()
})
</script>

<style scoped>
.gov-page { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.toolbar-card,.panel-card,.stat-card,.box,.banner { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); box-shadow: var(--surface-shadow); }
.toolbar-card { padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.field { display: flex; flex-direction: column; gap: 6px; min-width: 220px; }
.field span { font-size: 13px; color: var(--text-muted); }
.field select,.field input,.form-grid input,.form-grid select { height: 36px; padding: 0 12px; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: var(--bg-card); color: var(--text-main); outline: none; }
.toolbar-actions,.toolbar-stats,.link-group { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.toolbar-stats div { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-main); }
.toolbar-stats strong { font-size: 16px; color: var(--text-strong); }
.banner { padding: 12px 16px; font-size: 13px; }
.banner.success { border-color: rgba(39,174,96,.35); background: rgba(39,174,96,.08); color: #1d7f48; }
.banner.error { border-color: rgba(231,76,60,.35); background: rgba(231,76,60,.08); color: #b42318; }
.stats-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.stat-card { padding: 16px; }
.stat-card span { font-size: 13px; color: var(--text-muted); }
.stat-card strong { display: block; margin-top: 8px; font-size: 24px; color: var(--text-strong); }
.panel-card { padding: 20px; }
.tab-strip { display: flex; align-items: center; gap: 24px; border-bottom: 1px solid var(--border-color); margin: -20px -20px 0; padding: 0 20px; overflow-x: auto; }
.tab-btn { min-height: 38px; border: 0; background: transparent; color: var(--text-main); font-size: 13px; position: relative; flex-shrink: 0; }
.tab-btn.active { color: var(--primary); }
.tab-btn.active::after { content: ''; position: absolute; left: 0; right: 0; bottom: -1px; height: 2px; background: var(--primary); }
.tab-panel { padding-top: 18px; }
.two-col { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.box { padding: 16px; }
.box h3 { margin: 0 0 12px; font-size: 16px; color: var(--text-strong); }
.box h4 { margin: 0 0 8px; font-size: 14px; color: var(--text-strong); }
.box ul { margin: 0; padding-left: 18px; color: var(--text-main); }
.stack { display: flex; flex-direction: column; gap: 12px; }
.row-card { border: 1px solid var(--border-color); border-radius: var(--radius); background: var(--bg-muted); padding: 14px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.row-card strong { color: var(--text-strong); }
.row-card p { margin: 6px 0 0; font-size: 12px; color: var(--text-muted); }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table thead tr { background: var(--bg-muted); border-bottom: 1px solid var(--border-color); }
.data-table th,.data-table td { padding: 12px 16px; border-bottom: 1px solid var(--border-color); text-align: left; font-size: 13px; color: var(--text-main); vertical-align: top; }
.pill,.status-pill,.tag-pill { display: inline-flex; align-items: center; justify-content: center; padding: 4px 10px; border-radius: 999px; font-size: 12px; }
.tag-pill { background: var(--bg-muted); color: var(--text-main); }
.pill.failed,.pill.dead_letter,.status-pill.failed,.status-pill.dead_letter { background: rgba(231,76,60,.12); color: var(--danger); }
.pill.retry_pending,.status-pill.retry_pending { background: rgba(243,156,18,.12); color: var(--warning); }
.pill.processed,.pill.sent,.pill.completed,.status-pill.processed,.status-pill.sent,.status-pill.completed { background: rgba(39,174,96,.12); color: var(--success); }
.pill.disabled { background: rgba(148,163,184,.16); color: var(--text-muted); }
.table-link,.primary-btn,.ghost-btn { min-height: 32px; padding: 0 14px; border-radius: var(--radius); font-size: 13px; }
.table-link { border: 0; background: transparent; color: var(--primary); padding: 0; min-height: auto; }
.table-link:disabled { color: var(--text-muted); }
.primary-btn { border: 1px solid var(--primary); background: var(--primary); color: #fff; }
.ghost-btn { border: 1px solid var(--border-color-strong); background: transparent; color: var(--text-main); }
.form-box { display: flex; flex-direction: column; gap: 12px; }
.form-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.empty { min-height: 140px; display: grid; place-items: center; text-align: center; color: var(--text-muted); border: 1px dashed var(--border-color); border-radius: var(--radius); }
.mono { font-family: Consolas, 'JetBrains Mono', monospace; word-break: break-all; }
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,.32); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 999; }
.modal-card { width: min(860px, 100%); padding: 24px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); box-shadow: var(--surface-shadow); }
.modal-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 18px; }
.modal-head h2 { margin: 0; font-size: 18px; color: var(--text-strong); }
.close-btn { border: 0; background: transparent; color: var(--text-muted); font-size: 20px; }
.modal-form { display: flex; flex-direction: column; gap: 16px; }
.form-error { margin: 0; font-size: 13px; color: var(--danger); }
@media (max-width: 1180px) { .stats-grid,.form-grid,.two-col { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 860px) { .gov-page { padding: 16px; } .toolbar-card,.toolbar-actions,.toolbar-stats,.row-card { flex-direction: column; align-items: flex-start; } .stats-grid,.form-grid,.two-col { grid-template-columns: 1fr; } }
</style>
