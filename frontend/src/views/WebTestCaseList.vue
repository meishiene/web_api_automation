<template>
  <section class="cases-page">
    <div class="hero-card">
      <div>
        <router-link :to="`/project/${projectId}`" class="back-link">← 返回 API 用例页</router-link>
        <span class="eyebrow">Web Test</span>
        <h2>{{ projectName }}</h2>
        <p>管理 Web 用例步骤，支持单用例执行与结果回溯。</p>
      </div>
      <button @click="openCreateModal" class="primary-btn">新建 Web 用例</button>
    </div>

    <section class="panel-card">
      <div class="panel-head">
        <div>
          <h3>Web 用例列表</h3>
          <p>按项目维护 open / click / input / wait / assert / screenshot 步骤。</p>
        </div>
        <button class="secondary-btn" @click="goToUnifiedRuns">统一执行结果</button>
      </div>

      <div v-if="loadingCases" class="state-block"><p>正在加载 Web 用例...</p></div>
      <div v-else-if="cases.length === 0" class="state-block">
        <p>暂无 Web 用例，先创建一个用于执行验证。</p>
      </div>
      <div v-else class="table-wrap">
        <table class="cases-table">
          <thead>
            <tr>
              <th>名称</th>
              <th>Base URL</th>
              <th>步骤数</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in cases" :key="item.id">
              <td>
                <div class="name-cell">
                  <strong>{{ item.name }}</strong>
                  <span>#{{ item.id }}</span>
                </div>
              </td>
              <td>{{ item.base_url || '--' }}</td>
              <td>{{ item.steps?.length || 0 }}</td>
              <td>{{ formatDate(item.updated_at || item.created_at) }}</td>
              <td>
                <div class="row-actions">
                  <button class="table-btn subtle" @click="runCase(item)">运行</button>
                  <button class="table-btn edit" @click="openEditModal(item)">编辑</button>
                  <button class="table-btn danger" @click="deleteCaseById(item.id)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel-card">
      <div class="panel-head">
        <div>
          <h3>最近 Web 执行记录</h3>
          <p>点击“执行详情”可查看步骤日志与产物路径。</p>
        </div>
      </div>

      <div v-if="loadingRuns" class="state-block"><p>正在加载执行记录...</p></div>
      <div v-else-if="runs.length === 0" class="state-block"><p>暂无执行记录。</p></div>
      <div v-else class="table-wrap">
        <table class="cases-table">
          <thead>
            <tr>
              <th>Run ID</th>
              <th>Case ID</th>
              <th>状态</th>
              <th>耗时(ms)</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="run in runs" :key="run.id">
              <td>#{{ run.id }}</td>
              <td>#{{ run.web_test_case_id }}</td>
              <td><span class="status-pill" :class="run.status">{{ run.status }}</span></td>
              <td>{{ run.duration_ms ?? '--' }}</td>
              <td>{{ formatDate(run.created_at) }}</td>
              <td>
                <router-link class="table-link" :to="`/project/${projectId}/web-runs/${run.id}`">执行详情</router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="showModal" class="modal-mask" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-head">
          <div>
            <h3>{{ editingId ? '编辑 Web 用例' : '新建 Web 用例' }}</h3>
            <p>步骤参数使用 JSON 对象格式，例如：{"selector":"#login"}。</p>
          </div>
          <button @click="closeModal" class="icon-btn">✕</button>
        </div>

        <form @submit.prevent="saveCase" class="modal-form">
          <label class="field-block">
            <span>名称</span>
            <input v-model.trim="form.name" type="text" placeholder="例如：登录流程 smoke" />
          </label>

          <label class="field-block">
            <span>描述</span>
            <input v-model.trim="form.description" type="text" placeholder="可选" />
          </label>

          <label class="field-block">
            <span>Base URL</span>
            <input v-model.trim="form.base_url" type="text" placeholder="例如：https://example.com" />
          </label>

          <div class="steps-head">
            <strong>步骤编排</strong>
            <button type="button" class="secondary-btn" @click="addStep">新增步骤</button>
          </div>

          <div v-if="form.steps.length === 0" class="inline-empty">暂无步骤，可先新增 1 条。</div>
          <div v-for="(step, index) in form.steps" :key="index" class="step-card">
            <div class="step-meta">
              <span>步骤 {{ index + 1 }}</span>
              <button type="button" class="table-btn danger" @click="removeStep(index)">移除</button>
            </div>
            <div class="step-grid">
              <label class="field-block">
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

              <label class="field-block">
                <span>参数（JSON）</span>
                <textarea
                  v-model="step.paramsText"
                  rows="4"
                  placeholder='例如：{"selector":"#submit"}'
                ></textarea>
              </label>
            </div>
          </div>

          <p v-if="formError" class="form-error">{{ formError }}</p>

          <div class="modal-actions">
            <button type="button" class="secondary-btn" @click="closeModal">取消</button>
            <button type="submit" class="primary-btn" :disabled="saving">
              {{ saving ? '保存中...' : (editingId ? '保存修改' : '创建用例') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProjects } from '@/api/projects'
import {
  getWebTestCases,
  getWebTestCase,
  createWebTestCase,
  updateWebTestCase,
  deleteWebTestCase,
} from '@/api/webTestCases'
import { getWebTestRuns, runWebTestCase } from '@/api/webTestRuns'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.projectId)

const loadingCases = ref(false)
const loadingRuns = ref(false)
const saving = ref(false)
const showModal = ref(false)
const editingId = ref(null)
const formError = ref('')

const projectName = ref('Web 项目')
const cases = ref([])
const runs = ref([])
const form = ref({
  name: '',
  description: '',
  base_url: '',
  steps: [],
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

const resetForm = () => {
  form.value = {
    name: '',
    description: '',
    base_url: '',
    steps: [],
  }
  editingId.value = null
  formError.value = ''
}

const fetchProjectName = async () => {
  try {
    const list = await getProjects()
    const project = list.find(item => item.id === projectId)
    if (project) {
      projectName.value = `${project.name} · Web 用例`
    }
  } catch (err) {
    console.error('Failed to fetch project name')
  }
}

const fetchCases = async () => {
  loadingCases.value = true
  try {
    cases.value = await getWebTestCases(projectId)
  } catch (err) {
    alert('获取 Web 用例失败')
  } finally {
    loadingCases.value = false
  }
}

const fetchRuns = async () => {
  loadingRuns.value = true
  try {
    runs.value = await getWebTestRuns(projectId)
  } catch (err) {
    alert('获取 Web 执行记录失败')
  } finally {
    loadingRuns.value = false
  }
}

const openCreateModal = () => {
  resetForm()
  showModal.value = true
}

const openEditModal = async (item) => {
  showModal.value = true
  resetForm()
  editingId.value = item.id
  try {
    const detail = await getWebTestCase(item.id)
    form.value.name = detail.name || ''
    form.value.description = detail.description || ''
    form.value.base_url = detail.base_url || ''
    form.value.steps = (detail.steps || []).map(step => ({
      action: step.action || 'open',
      paramsText: JSON.stringify(step.params || {}, null, 2),
    }))
  } catch (err) {
    alert('加载 Web 用例详情失败')
    closeModal()
  }
}

const closeModal = () => {
  showModal.value = false
  resetForm()
}

const addStep = () => {
  form.value.steps.push({
    action: 'open',
    paramsText: '{}',
  })
}

const removeStep = (index) => {
  form.value.steps.splice(index, 1)
}

const buildPayload = () => {
  if (!form.value.name) {
    throw new Error('用例名称不能为空')
  }

  const steps = form.value.steps.map((step, index) => {
    let parsed = {}
    try {
      parsed = step.paramsText?.trim() ? JSON.parse(step.paramsText) : {}
    } catch (err) {
      throw new Error(`第 ${index + 1} 步参数 JSON 无法解析`)
    }
    if (parsed === null || Array.isArray(parsed) || typeof parsed !== 'object') {
      throw new Error(`第 ${index + 1} 步参数必须为 JSON 对象`)
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
    steps,
  }
}

const saveCase = async () => {
  formError.value = ''
  try {
    const payload = buildPayload()
    saving.value = true
    if (editingId.value) {
      await updateWebTestCase(editingId.value, payload)
    } else {
      await createWebTestCase({
        project_id: projectId,
        ...payload,
      })
    }
    closeModal()
    await fetchCases()
  } catch (err) {
    formError.value = err.response?.data?.detail || err.message || '保存失败'
  } finally {
    saving.value = false
  }
}

const deleteCaseById = async (id) => {
  if (!confirm('确定删除该 Web 用例吗？')) return
  try {
    await deleteWebTestCase(id)
    await fetchCases()
  } catch (err) {
    alert('删除失败')
  }
}

const runCase = async (item) => {
  try {
    const result = await runWebTestCase(item.id)
    await fetchRuns()
    if (result?.id) {
      const shouldOpen = confirm(`执行已触发，状态：${result.status}。是否查看执行详情？`)
      if (shouldOpen) {
        router.push(`/project/${projectId}/web-runs/${result.id}`)
      }
    }
  } catch (err) {
    alert(err.response?.data?.detail || '执行失败')
  }
}

const goToUnifiedRuns = () => {
  router.push(`/project/${projectId}/executions`)
}

onMounted(async () => {
  await fetchProjectName()
  await Promise.all([fetchCases(), fetchRuns()])
})
</script>

<style scoped>
.cases-page { display: flex; flex-direction: column; gap: 20px; }
.hero-card, .panel-card, .modal-card { background: rgba(255,255,255,0.84); border: 1px solid var(--border-color); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); }
.hero-card { padding: 28px 30px; display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; background: linear-gradient(135deg, rgba(234,248,246,0.95), rgba(244,249,249,0.95)); }
.panel-card { padding: 24px; }
.back-link { display: inline-block; margin-bottom: 10px; color: var(--text-muted); text-decoration: none; }
.eyebrow { display: inline-block; padding: 6px 10px; border-radius: 999px; background: var(--primary-soft); color: var(--primary-dark); font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
.panel-head h3 { margin: 0 0 8px; color: var(--text-strong); }
.panel-head p { margin: 0 0 18px; color: var(--text-muted); }
.table-wrap { overflow: auto; border: 1px solid var(--border-color); border-radius: 20px; background: #fff; }
.cases-table { width: 100%; min-width: 860px; border-collapse: collapse; }
.cases-table th, .cases-table td { padding: 16px 18px; border-bottom: 1px solid #edf2f1; text-align: left; }
.cases-table thead th { background: #f8fbfb; color: var(--text-muted); font-size: 13px; }
.name-cell { display: flex; flex-direction: column; gap: 4px; }
.name-cell strong { color: var(--text-strong); }
.name-cell span { color: var(--text-muted); font-size: 12px; }
.row-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.status-pill { display: inline-flex; padding: 6px 10px; border-radius: 999px; font-weight: 700; text-transform: capitalize; }
.status-pill.success { background: #e4fbf3; color: #0f8f6b; }
.status-pill.failed, .status-pill.error { background: #ffe7e7; color: #d44a4a; }
.status-pill.running { background: #eef2ff; color: #4c63d2; }
.state-block { min-height: 220px; display: grid; place-items: center; border: 1px dashed var(--border-strong); border-radius: 16px; color: var(--text-muted); }
.table-link { color: var(--primary-dark); text-decoration: none; font-weight: 700; }
.primary-btn, .secondary-btn, .table-btn { border: 0; border-radius: 14px; padding: 11px 16px; font-weight: 700; }
.primary-btn { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: #fff; box-shadow: 0 12px 24px rgba(18,179,165,0.22); }
.secondary-btn { background: #f4f7f7; color: var(--text-main); border: 1px solid var(--border-color); }
.table-btn.subtle { background: var(--primary-soft); color: var(--primary-dark); }
.table-btn.edit { background: #eef2ff; color: #4c63d2; }
.table-btn.danger { background: var(--danger-soft); color: #d44a4a; }
.modal-mask { position: fixed; inset: 0; background: rgba(15,23,42,0.36); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 999; }
.modal-card { width: min(920px, 100%); max-height: 92vh; overflow: auto; padding: 24px; background: #fff; }
.modal-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 18px; }
.icon-btn { width: 38px; height: 38px; border-radius: 12px; border: 0; background: var(--bg-card-soft); color: var(--text-main); }
.modal-form { display: flex; flex-direction: column; gap: 14px; }
.field-block { display: flex; flex-direction: column; gap: 8px; }
.field-block span { color: var(--text-main); font-weight: 600; }
.field-block input, .field-block textarea, .field-block select { width: 100%; border: 1px solid var(--border-color); background: var(--bg-card-soft); border-radius: 14px; padding: 12px 14px; outline: none; color: var(--text-main); }
.field-block textarea { resize: vertical; font-family: 'JetBrains Mono', 'Consolas', monospace; }
.steps-head { display: flex; align-items: center; justify-content: space-between; margin-top: 6px; }
.inline-empty { border: 1px dashed var(--border-strong); border-radius: 14px; padding: 12px; color: var(--text-muted); }
.step-card { border: 1px solid var(--border-color); border-radius: 14px; padding: 12px; background: #fff; display: flex; flex-direction: column; gap: 10px; }
.step-meta { display: flex; align-items: center; justify-content: space-between; }
.step-grid { display: grid; grid-template-columns: 220px 1fr; gap: 12px; align-items: start; }
.form-error { margin: 0; color: #d44a4a; background: var(--danger-soft); padding: 12px 14px; border-radius: 14px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 8px; }
@media (max-width: 900px) {
  .hero-card { flex-direction: column; align-items: flex-start; }
  .step-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .panel-card, .hero-card, .modal-card { padding: 18px; border-radius: 20px; }
  .row-actions, .modal-actions { flex-direction: column; width: 100%; }
  .primary-btn, .secondary-btn, .table-btn { width: 100%; }
}
</style>
