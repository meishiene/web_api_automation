<template>
  <section class="env-workbench">
    <div class="toolbar-card">
      <div class="toolbar-left">
        <label class="project-switch">
          <span>当前项目</span>
          <select v-model="selectedProjectId" @change="handleProjectChange">
            <option v-for="project in projects" :key="project.id" :value="String(project.id)">{{ project.name }}</option>
          </select>
        </label>
        <div class="toolbar-actions">
          <button class="primary-btn" @click="openEnvironmentModal()">新增环境</button>
          <button class="ghost-btn" @click="refreshAll" :disabled="loading">{{ loading ? '刷新中...' : '刷新' }}</button>
        </div>
      </div>
      <div class="toolbar-stats">
        <div><span>环境数</span><strong>{{ environments.length }}</strong></div>
        <div><span>项目变量</span><strong>{{ projectVariables.length }}</strong></div>
        <div><span>变量组</span><strong>{{ projectGroups.length }}</strong></div>
        <div><span>密钥变量</span><strong>{{ projectSecretCount + environmentSecretCount }}</strong></div>
      </div>
    </div>

    <div v-if="feedback.text" class="feedback-banner" :class="feedback.type">{{ feedback.text }}</div>

    <div class="workspace-grid">
      <aside class="panel-card env-sidebar">
        <div class="panel-head">
          <div>
            <h3>环境列表</h3>
            <p>管理 dev / test / staging / prod 等执行环境。</p>
          </div>
        </div>

        <div v-if="loading && !environments.length" class="mini-state">正在加载环境...</div>
        <div v-else-if="!environments.length" class="mini-state">当前项目还没有环境，先创建一个环境。</div>
        <div v-else class="env-list">
          <button v-for="environment in environments" :key="environment.id" class="env-card" :class="{ active: selectedEnvironmentId === environment.id }" @click="selectEnvironment(environment.id)">
            <div class="env-card-copy">
              <div class="env-card-title">
                <strong>{{ environment.name }}</strong>
                <span class="env-count">{{ environmentVarCount(environment.id) }} 变量</span>
              </div>
              <p>{{ environment.description || '暂无环境描述' }}</p>
              <small>更新时间 {{ formatDate(environment.updated_at || environment.created_at) }}</small>
            </div>
            <div class="env-card-actions">
              <button class="link-btn" @click.stop="openEnvironmentModal(environment)">编辑</button>
              <button class="link-btn danger" @click.stop="removeEnvironment(environment)">删除</button>
            </div>
          </button>
        </div>
      </aside>

      <div class="content-stack">
        <section class="panel-card">
          <div class="panel-head">
            <div>
              <h3>{{ selectedEnvironment ? `${selectedEnvironment.name} 环境概览` : '项目变量概览' }}</h3>
              <p>项目变量为默认值，环境变量与已绑定变量组会在运行时覆盖同名项目变量。</p>
            </div>
            <div class="summary-badges">
              <span class="badge muted">项目：{{ projectName }}</span>
              <span v-if="selectedEnvironment" class="badge info">当前环境：{{ selectedEnvironment.name }}</span>
            </div>
          </div>

          <div class="summary-grid">
            <article class="summary-card"><span>项目变量</span><strong>{{ projectVariables.length }}</strong><small>覆盖当前项目所有环境</small></article>
            <article class="summary-card accent"><span>环境变量</span><strong>{{ environmentVariables.length }}</strong><small>{{ selectedEnvironment ? `${selectedEnvironment.name} 独有配置` : '选择环境后查看' }}</small></article>
            <article class="summary-card"><span>绑定变量组</span><strong>{{ environmentGroupBindings.length }}</strong><small>复用项目级变量分组</small></article>
            <article class="summary-card soft"><span>密钥变量</span><strong>{{ projectSecretCount + environmentSecretCount }}</strong><small>默认脱敏，按权限查看明文</small></article>
          </div>
        </section>

        <section class="panel-card">
          <div class="tab-strip">
            <button class="tab-btn" :class="{ active: activeTab === 'project' }" @click="activeTab = 'project'">项目变量</button>
            <button class="tab-btn" :class="{ active: activeTab === 'environment' }" @click="activeTab = 'environment'">环境变量</button>
            <button class="tab-btn" :class="{ active: activeTab === 'groups' }" @click="activeTab = 'groups'">变量组</button>
          </div>

          <div v-if="activeTab === 'project'" class="tab-panel">
            <div class="editor-card">
              <div class="panel-head compact"><div><h3>新增 / 更新项目变量</h3><p>支持分组与 secret 标记，环境执行时可被环境变量覆盖。</p></div></div>
              <div class="form-grid">
                <label class="field-block"><span>Key</span><input v-model.trim="newProjectVariable.key" type="text" placeholder="例如：base_url" /></label>
                <label class="field-block"><span>Value</span><input v-model="newProjectVariable.value" type="text" placeholder="例如：https://api.example.com" /></label>
                <label class="field-block"><span>变量组</span><input v-model.trim="newProjectVariable.group_name" type="text" placeholder="例如：auth-default" /></label>
                <label class="field-block checkbox-field"><span>安全性</span><label class="check-inline"><input v-model="newProjectVariable.is_secret" type="checkbox" /><span>标记为 secret</span></label></label>
              </div>
              <div class="form-actions"><button class="primary-btn" @click="saveProjectVariable" :disabled="savingProjectVariable">{{ savingProjectVariable ? '保存中...' : '保存项目变量' }}</button></div>
            </div>
            <div v-if="projectVariables.length === 0" class="mini-state">当前项目暂无变量。</div>
            <div v-else class="table-wrap">
              <table class="data-table">
                <thead><tr><th>Key</th><th>Group</th><th>Value</th><th>类型</th><th>更新时间</th><th>操作</th></tr></thead>
                <tbody>
                  <tr v-for="item in projectVariables" :key="`pv-${item.id}`">
                    <td>{{ item.key }}</td><td>{{ item.group_name || '--' }}</td><td class="mono-cell">{{ item.value }}</td>
                    <td><span class="type-pill" :class="{ secret: item.is_secret }">{{ item.is_secret ? 'Secret' : 'Plain' }}</span></td>
                    <td>{{ formatDate(item.updated_at || item.created_at) }}</td>
                    <td><button v-if="item.is_secret" class="link-btn" @click="revealProject(item.key)">查看明文</button><span v-else class="muted-copy">--</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-else-if="activeTab === 'environment'" class="tab-panel">
            <div v-if="!selectedEnvironment" class="mini-state">请先选择一个环境，再维护环境变量。</div>
            <template v-else>
              <div class="editor-card">
                <div class="panel-head compact"><div><h3>新增 / 更新环境变量</h3><p>环境变量优先级高于项目变量，适合配置环境专属地址、密钥与开关。</p></div></div>
                <div class="form-grid three">
                  <label class="field-block"><span>Key</span><input v-model.trim="newEnvironmentVariable.key" type="text" placeholder="例如：token" /></label>
                  <label class="field-block"><span>Value</span><input v-model="newEnvironmentVariable.value" type="text" placeholder="输入变量值" /></label>
                  <label class="field-block checkbox-field"><span>安全性</span><label class="check-inline"><input v-model="newEnvironmentVariable.is_secret" type="checkbox" /><span>标记为 secret</span></label></label>
                </div>
                <div class="form-actions"><button class="primary-btn" @click="saveEnvironmentVariable" :disabled="savingEnvironmentVariable">{{ savingEnvironmentVariable ? '保存中...' : `保存到 ${selectedEnvironment.name}` }}</button></div>
              </div>
              <div v-if="environmentVariables.length === 0" class="mini-state">当前环境暂无变量。</div>
              <div v-else class="table-wrap">
                <table class="data-table">
                  <thead><tr><th>Key</th><th>Value</th><th>类型</th><th>更新时间</th><th>操作</th></tr></thead>
                  <tbody>
                    <tr v-for="item in environmentVariables" :key="`ev-${item.id}`">
                      <td>{{ item.key }}</td><td class="mono-cell">{{ item.value }}</td>
                      <td><span class="type-pill" :class="{ secret: item.is_secret }">{{ item.is_secret ? 'Secret' : 'Plain' }}</span></td>
                      <td>{{ formatDate(item.updated_at || item.created_at) }}</td>
                      <td><button v-if="item.is_secret" class="link-btn" @click="revealEnv(item.key)">查看明文</button><span v-else class="muted-copy">--</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </template>
          </div>

          <div v-else class="tab-panel">
            <div v-if="!selectedEnvironment" class="mini-state">请先选择一个环境，再绑定变量组。</div>
            <template v-else>
              <div class="groups-grid">
                <div class="group-column">
                  <div class="panel-head compact"><div><h3>项目变量组</h3><p>变量组用于将同一类配置统一绑定到多个环境。</p></div></div>
                  <div v-if="projectGroups.length === 0" class="mini-state">当前项目还没有变量组。</div>
                  <div v-else class="group-list">
                    <article v-for="group in projectGroups" :key="group.group_name" class="group-card">
                      <div>
                        <strong>{{ group.group_name }}</strong>
                        <p>{{ group.variable_count }} 个变量 · {{ group.secret_count }} 个 secret</p>
                      </div>
                      <button class="link-btn" @click="groupToBind = group.group_name">选择</button>
                    </article>
                  </div>
                </div>
                <div class="group-column">
                  <div class="panel-head compact"><div><h3>绑定到 {{ selectedEnvironment.name }}</h3><p>已绑定变量组会与项目变量、环境变量共同参与解析。</p></div></div>
                  <div class="bind-form">
                    <select v-model="groupToBind"><option value="">选择一个变量组</option><option v-for="group in projectGroups" :key="group.group_name" :value="group.group_name">{{ group.group_name }}</option></select>
                    <button class="primary-btn" @click="bindGroup" :disabled="bindingGroup">{{ bindingGroup ? '绑定中...' : '绑定到当前环境' }}</button>
                  </div>
                  <div v-if="environmentGroupBindings.length === 0" class="mini-state">当前环境还没有绑定变量组。</div>
                  <div v-else class="binding-list">
                    <article v-for="binding in environmentGroupBindings" :key="binding.id" class="binding-card">
                      <div><strong>{{ binding.group_name }}</strong><p>绑定时间 {{ formatDate(binding.updated_at || binding.created_at) }}</p></div>
                      <button class="link-btn danger" @click="unbindGroup(binding.group_name)">解绑</button>
                    </article>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </section>
      </div>
    </div>

    <div v-if="showEnvironmentModal" class="modal-mask" @click.self="closeEnvironmentModal">
      <div class="modal-card">
        <div class="modal-head"><h2>{{ editingEnvironmentId ? '编辑环境' : '新增环境' }}</h2><button class="close-btn" @click="closeEnvironmentModal">×</button></div>
        <div class="modal-form">
          <label class="field-block"><span>环境名称</span><input v-model.trim="environmentForm.name" type="text" placeholder="例如：staging" /></label>
          <label class="field-block"><span>环境描述</span><textarea v-model.trim="environmentForm.description" rows="3" placeholder="说明当前环境的用途、域名或责任边界"></textarea></label>
          <p v-if="formError" class="form-error">{{ formError }}</p>
          <div class="modal-actions"><button class="ghost-btn" @click="closeEnvironmentModal">取消</button><button class="primary-btn" @click="submitEnvironment" :disabled="savingEnvironment">{{ savingEnvironment ? '保存中...' : editingEnvironmentId ? '保存修改' : '创建环境' }}</button></div>
        </div>
      </div>
    </div>

    <div v-if="secretPreview" class="modal-mask" @click.self="secretPreview = null">
      <div class="modal-card secret-modal">
        <div class="modal-head"><h2>密钥明文</h2><button class="close-btn" @click="secretPreview = null">×</button></div>
        <div class="secret-box">
          <div class="secret-meta"><span>Key：{{ secretPreview.key }}</span><span>Scope：{{ secretPreview.scope }}</span></div>
          <pre>{{ secretPreview.value }}</pre>
        </div>
        <div class="modal-actions"><button class="ghost-btn" @click="secretPreview = null">关闭</button></div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProjects } from '@/api/projects'
import { bindEnvironmentVariableGroup, createProjectEnvironment, deleteProjectEnvironment, getEnvironmentVariableGroups, getEnvironmentVariables, getProjectEnvironments, getProjectVariableGroups, getProjectVariables, revealEnvironmentSecret, revealProjectSecret, unbindEnvironmentVariableGroup, updateProjectEnvironment, upsertEnvironmentVariable, upsertProjectVariable } from '@/api/environments'
import { setActiveProjectId } from '@/utils/projectContext'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => Number(route.params.projectId))
const projects = ref([])
const selectedProjectId = ref('')
const projectName = ref(`项目 #${projectId.value}`)
const loading = ref(false)
const activeTab = ref('project')
const environments = ref([])
const selectedEnvironmentId = ref(null)
const projectVariables = ref([])
const projectGroups = ref([])
const environmentVariables = ref([])
const environmentGroupBindings = ref([])
const environmentVariableCountMap = ref({})
const groupToBind = ref('')
const formError = ref('')
const feedback = ref({ type: 'success', text: '' })
const secretPreview = ref(null)
const showEnvironmentModal = ref(false)
const editingEnvironmentId = ref(null)
const savingEnvironment = ref(false)
const savingProjectVariable = ref(false)
const savingEnvironmentVariable = ref(false)
const bindingGroup = ref(false)
const environmentForm = ref({ name: '', description: '' })
const newProjectVariable = ref({ key: '', value: '', is_secret: false, group_name: '' })
const newEnvironmentVariable = ref({ key: '', value: '', is_secret: false })

const selectedEnvironment = computed(() => environments.value.find((item) => item.id === selectedEnvironmentId.value) || null)
const projectSecretCount = computed(() => projectVariables.value.filter((item) => item.is_secret).length)
const environmentSecretCount = computed(() => environmentVariables.value.filter((item) => item.is_secret).length)
const errorText = (err, fallback) => err?.response?.data?.detail || err?.response?.data?.error?.message || err?.message || fallback
const setFeedback = (type, text) => { feedback.value = { type, text } }
const clearFeedback = () => { feedback.value = { type: 'success', text: '' } }
const normalizeTimestamp = (value) => { const n = Number(value || 0); return n > 1e12 ? n : n * 1000 }
const formatDate = (value) => !value ? '--' : new Date(normalizeTimestamp(value)).toLocaleString('zh-CN')
const environmentVarCount = (environmentId) => environmentVariableCountMap.value[environmentId] || 0

const syncProjectOptions = async () => {
  projects.value = await getProjects()
  selectedProjectId.value = String(projectId.value)
  const project = projects.value.find((item) => item.id === projectId.value)
  if (project) projectName.value = project.name
}

const handleProjectChange = () => {
  if (!selectedProjectId.value) return
  const nextProjectId = Number(selectedProjectId.value)
  if (!Number.isFinite(nextProjectId) || nextProjectId === projectId.value) return
  setActiveProjectId(nextProjectId)
  router.push(`/project/${nextProjectId}/environments`)
}

const fetchProjectVariables = async () => {
  const [variables, groups] = await Promise.all([getProjectVariables(projectId.value), getProjectVariableGroups(projectId.value)])
  projectVariables.value = variables
  projectGroups.value = groups
}

const fetchEnvironments = async () => {
  environments.value = await getProjectEnvironments(projectId.value)
  if (!environments.value.length) {
    selectedEnvironmentId.value = null
    environmentVariables.value = []
    environmentGroupBindings.value = []
    environmentVariableCountMap.value = {}
    return
  }
  if (!selectedEnvironmentId.value || !environments.value.find((item) => item.id === selectedEnvironmentId.value)) {
    selectedEnvironmentId.value = environments.value[0].id
  }
  const detailEntries = await Promise.all(environments.value.map(async (environment) => {
    try {
      const [variables, bindings] = await Promise.all([getEnvironmentVariables(environment.id), getEnvironmentVariableGroups(environment.id)])
      return [environment.id, { variables, bindings }]
    } catch { return [environment.id, { variables: [], bindings: [] }] }
  }))
  const detailMap = Object.fromEntries(detailEntries)
  environmentVariableCountMap.value = Object.fromEntries(Object.entries(detailMap).map(([id, detail]) => [id, detail.variables.length]))
  const currentDetail = detailMap[selectedEnvironmentId.value] || { variables: [], bindings: [] }
  environmentVariables.value = currentDetail.variables
  environmentGroupBindings.value = currentDetail.bindings
}

const refreshAll = async () => {
  loading.value = true
  clearFeedback()
  try {
    await syncProjectOptions()
    await Promise.all([fetchProjectVariables(), fetchEnvironments()])
  } catch (err) {
    setFeedback('error', errorText(err, '加载环境治理数据失败'))
  } finally {
    loading.value = false
  }
}

const selectEnvironment = async (environmentId) => {
  selectedEnvironmentId.value = environmentId
  await fetchEnvironments()
}

const openEnvironmentModal = (environment = null) => {
  editingEnvironmentId.value = environment?.id || null
  environmentForm.value = { name: environment?.name || '', description: environment?.description || '' }
  formError.value = ''
  showEnvironmentModal.value = true
}

const closeEnvironmentModal = () => {
  showEnvironmentModal.value = false
  editingEnvironmentId.value = null
  savingEnvironment.value = false
  formError.value = ''
}

const submitEnvironment = async () => {
  if (!environmentForm.value.name.trim()) { formError.value = '环境名称不能为空'; return }
  savingEnvironment.value = true
  try {
    const payload = { name: environmentForm.value.name.trim(), description: environmentForm.value.description?.trim() || '' }
    if (editingEnvironmentId.value) {
      await updateProjectEnvironment(editingEnvironmentId.value, payload)
      setFeedback('success', '环境已更新')
    } else {
      await createProjectEnvironment(projectId.value, payload)
      setFeedback('success', '环境已创建')
    }
    closeEnvironmentModal()
    await refreshAll()
  } catch (err) {
    formError.value = errorText(err, '保存环境失败')
  } finally {
    savingEnvironment.value = false
  }
}

const removeEnvironment = async (environment) => {
  if (!confirm(`确定删除环境「${environment.name}」吗？`)) return
  try {
    await deleteProjectEnvironment(environment.id)
    setFeedback('success', '环境已删除')
    await refreshAll()
  } catch (err) {
    setFeedback('error', errorText(err, '删除环境失败'))
  }
}

const saveProjectVariable = async () => {
  if (!newProjectVariable.value.key.trim()) { setFeedback('error', '项目变量 key 不能为空'); return }
  savingProjectVariable.value = true
  try {
    await upsertProjectVariable(projectId.value, { key: newProjectVariable.value.key.trim(), value: newProjectVariable.value.value || '', is_secret: newProjectVariable.value.is_secret, group_name: newProjectVariable.value.group_name?.trim() || null })
    newProjectVariable.value = { key: '', value: '', is_secret: false, group_name: '' }
    setFeedback('success', '项目变量已保存')
    await fetchProjectVariables()
  } catch (err) {
    setFeedback('error', errorText(err, '保存项目变量失败'))
  } finally {
    savingProjectVariable.value = false
  }
}

const saveEnvironmentVariable = async () => {
  if (!selectedEnvironmentId.value) { setFeedback('error', '请先选择环境'); return }
  if (!newEnvironmentVariable.value.key.trim()) { setFeedback('error', '环境变量 key 不能为空'); return }
  savingEnvironmentVariable.value = true
  try {
    await upsertEnvironmentVariable(selectedEnvironmentId.value, { key: newEnvironmentVariable.value.key.trim(), value: newEnvironmentVariable.value.value || '', is_secret: newEnvironmentVariable.value.is_secret })
    newEnvironmentVariable.value = { key: '', value: '', is_secret: false }
    setFeedback('success', '环境变量已保存')
    await fetchEnvironments()
  } catch (err) {
    setFeedback('error', errorText(err, '保存环境变量失败'))
  } finally {
    savingEnvironmentVariable.value = false
  }
}

const bindGroup = async () => {
  if (!selectedEnvironmentId.value || !groupToBind.value) { setFeedback('error', '请选择环境和变量组'); return }
  bindingGroup.value = true
  try {
    await bindEnvironmentVariableGroup(selectedEnvironmentId.value, groupToBind.value)
    groupToBind.value = ''
    setFeedback('success', '变量组已绑定')
    await fetchEnvironments()
  } catch (err) {
    setFeedback('error', errorText(err, '绑定变量组失败'))
  } finally {
    bindingGroup.value = false
  }
}

const unbindGroup = async (groupName) => {
  if (!selectedEnvironmentId.value) return
  try {
    await unbindEnvironmentVariableGroup(selectedEnvironmentId.value, groupName)
    setFeedback('success', '变量组已解绑')
    await fetchEnvironments()
  } catch (err) {
    setFeedback('error', errorText(err, '解绑变量组失败'))
  }
}

const revealProject = async (key) => {
  try { secretPreview.value = await revealProjectSecret(projectId.value, key) } catch (err) { setFeedback('error', errorText(err, '查看项目密钥失败')) }
}
const revealEnv = async (key) => {
  if (!selectedEnvironmentId.value) return
  try { secretPreview.value = await revealEnvironmentSecret(selectedEnvironmentId.value, key) } catch (err) { setFeedback('error', errorText(err, '查看环境密钥失败')) }
}

watch(projectId, async () => {
  selectedEnvironmentId.value = null
  await refreshAll()
})

onMounted(async () => {
  setActiveProjectId(projectId.value)
  await refreshAll()
})
</script>

<style scoped>
.env-workbench { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.toolbar-card, .panel-card, .editor-card, .modal-card, .feedback-banner { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); box-shadow: var(--surface-shadow); }
.toolbar-card { padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.toolbar-left, .toolbar-actions, .toolbar-stats, .summary-badges, .form-actions, .modal-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.project-switch { display: flex; flex-direction: column; gap: 6px; min-width: 220px; }
.project-switch span, .field-block span { font-size: 13px; color: var(--text-muted); }
.project-switch select, .bind-form select, .field-block input, .field-block textarea, .field-block select { width: 100%; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: var(--bg-card); color: var(--text-main); outline: none; }
.project-switch select, .bind-form select, .field-block input, .field-block select { height: 36px; padding: 0 12px; }
.field-block textarea { min-height: 96px; padding: 10px 12px; resize: vertical; }
.toolbar-stats div { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-main); }
.toolbar-stats strong { font-size: 16px; color: var(--text-strong); }
.feedback-banner { padding: 12px 16px; font-size: 13px; }
.feedback-banner.success { border-color: rgba(39,174,96,.35); background: rgba(39,174,96,.08); color: #1d7f48; }
.feedback-banner.error { border-color: rgba(231,76,60,.35); background: rgba(231,76,60,.08); color: #b42318; }
.workspace-grid { display: grid; grid-template-columns: 320px 1fr; gap: 16px; }
.panel-card { padding: 20px; }
.panel-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 16px; }
.panel-head h3 { margin: 0 0 6px; font-size: 16px; font-weight: 500; color: var(--text-strong); }
.panel-head p { margin: 0; font-size: 13px; color: var(--text-muted); }
.panel-head.compact { margin-bottom: 12px; }
.env-list, .group-list, .binding-list, .content-stack { display: flex; flex-direction: column; gap: 12px; }
.env-card, .group-card, .binding-card { width: 100%; border: 1px solid var(--border-color); border-radius: var(--radius); background: var(--bg-muted); padding: 14px; text-align: left; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.env-card { align-items: flex-start; flex-direction: column; }
.env-card.active { border-color: var(--primary); background: rgba(52,152,219,.08); }
.env-card-title { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.env-card-title strong, .group-card strong, .binding-card strong { color: var(--text-strong); font-size: 14px; }
.env-card-copy p, .group-card p, .binding-card p { margin: 8px 0 6px; font-size: 13px; color: var(--text-main); }
.env-card-copy small { font-size: 12px; color: var(--text-muted); }
.env-count, .badge { font-size: 12px; }
.env-card-actions { display: flex; align-items: center; gap: 12px; }
.badge { display: inline-flex; align-items: center; justify-content: center; padding: 4px 10px; border-radius: 999px; }
.badge.muted { background: var(--bg-muted); color: var(--text-main); }
.badge.info { background: rgba(52,152,219,.12); color: var(--primary); }
.summary-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.summary-card { border: 1px solid var(--border-color); border-radius: var(--radius); background: var(--bg-card); padding: 16px; }
.summary-card.accent { background: rgba(52,152,219,.06); }
.summary-card.soft { background: rgba(39,174,96,.06); }
.summary-card span { font-size: 13px; color: var(--text-muted); }
.summary-card strong { display: block; margin-top: 8px; font-size: 24px; color: var(--text-strong); }
.summary-card small { display: block; margin-top: 8px; font-size: 12px; color: var(--text-muted); }
.tab-strip { display: flex; align-items: center; gap: 24px; border-bottom: 1px solid var(--border-color); margin: -20px -20px 0; padding: 0 20px; }
.tab-btn { min-height: 38px; border: 0; background: transparent; color: var(--text-main); font-size: 13px; position: relative; }
.tab-btn.active { color: var(--primary); }
.tab-btn.active::after { content: ''; position: absolute; left: 0; right: 0; bottom: -1px; height: 2px; background: var(--primary); }
.tab-panel { padding-top: 18px; }
.editor-card { border: 1px solid var(--border-color); padding: 16px; }
.form-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.form-grid.three { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.checkbox-field { justify-content: flex-end; }
.check-inline { display: inline-flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-main); }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table thead tr { background: var(--bg-muted); border-bottom: 1px solid var(--border-color); }
.data-table th { padding: 12px 16px; text-align: left; font-size: 13px; font-weight: 500; color: var(--text-main); }
.data-table td { padding: 14px 16px; border-bottom: 1px solid var(--border-color); font-size: 13px; color: var(--text-main); vertical-align: top; }
.mono-cell { font-family: Consolas, 'JetBrains Mono', monospace; word-break: break-all; }
.type-pill { display: inline-flex; align-items: center; justify-content: center; padding: 4px 10px; border-radius: 999px; background: var(--bg-muted); color: var(--text-main); font-size: 12px; }
.type-pill.secret { background: rgba(231,76,60,.12); color: var(--danger); }
.muted-copy { color: var(--text-muted); }
.groups-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.bind-form { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
.mini-state { min-height: 140px; display: grid; place-items: center; text-align: center; color: var(--text-muted); border: 1px dashed var(--border-color); border-radius: var(--radius); }
.primary-btn, .ghost-btn, .link-btn { min-height: 32px; padding: 0 14px; border-radius: var(--radius); font-size: 13px; }
.primary-btn { border: 1px solid var(--primary); background: var(--primary); color: #fff; }
.ghost-btn { border: 1px solid var(--border-color-strong); background: transparent; color: var(--text-main); }
.link-btn { border: 0; background: transparent; color: var(--primary); padding: 0; min-height: auto; }
.link-btn.danger { color: var(--danger); }
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,.32); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 999; }
.modal-card { width: min(720px, 100%); padding: 24px; }
.secret-modal { width: min(560px, 100%); }
.modal-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 18px; }
.modal-head h2 { margin: 0; font-size: 18px; font-weight: 500; color: var(--text-strong); }
.close-btn { border: 0; background: transparent; color: var(--text-muted); font-size: 20px; }
.modal-form { display: flex; flex-direction: column; gap: 16px; }
.form-error { margin: 0; font-size: 13px; color: var(--danger); }
.secret-box { border: 1px solid var(--border-color); border-radius: var(--radius); background: var(--bg-muted); padding: 16px; }
.secret-meta { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; font-size: 12px; color: var(--text-muted); }
.secret-box pre { margin: 0; white-space: pre-wrap; word-break: break-all; font-family: Consolas, 'JetBrains Mono', monospace; font-size: 13px; color: var(--text-strong); }
@media (max-width: 1180px) { .workspace-grid, .groups-grid { grid-template-columns: 1fr; } .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .form-grid, .form-grid.three { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 860px) { .env-workbench { padding: 16px; } .toolbar-card, .toolbar-left, .toolbar-stats, .panel-head, .summary-badges, .bind-form, .modal-actions { flex-direction: column; align-items: flex-start; } .summary-grid, .form-grid, .form-grid.three { grid-template-columns: 1fr; } }
</style>
