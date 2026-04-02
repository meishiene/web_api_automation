<template>
  <section class="cases-page">
    <div class="toolbar-card">
      <div class="toolbar-left">
        <div class="filter-group">
          <label>所属项目</label>
          <select v-model="selectedProjectId" @change="handleProjectChange">
            <option :value="''">请选择项目</option>
            <option v-for="project in projects" :key="project.id" :value="String(project.id)">
              {{ project.name }}
            </option>
          </select>
        </div>

        <button class="primary-btn" :disabled="!selectedProjectId" @click="openSelectedProjectApi">新建用例</button>
        <button class="ghost-btn" :disabled="!selectedProjectId" @click="openSelectedProjectApi">导出</button>
        <button class="ghost-btn" disabled>筛选（预留）</button>
      </div>

      <div class="toolbar-search">
        <input v-model.trim="keyword" type="text" placeholder="搜索用例名称、路径、描述..." />
      </div>
    </div>

    <div v-if="selectedRows.length" class="batch-bar">
      <span>已选择 {{ selectedRows.length }} 项</span>
      <button class="link-btn" :disabled="selectedRows.length !== 1" @click="openSelectedDetail">查看详情</button>
      <button class="link-btn" disabled>批量执行（预留）</button>
      <button class="link-btn" disabled>批量导出（预留）</button>
    </div>

    <div v-if="loading" class="state-card">正在加载测试用例...</div>
    <div v-else-if="!selectedProjectId" class="state-card">请选择一个项目查看当前项目下的 API / UI 用例</div>
    <div v-else-if="filteredCases.length === 0" class="state-card">当前项目暂无测试用例</div>

    <div v-else class="table-card">
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th class="checkbox-cell">
                <input type="checkbox" :checked="selectedRows.length === filteredCases.length" @change="toggleSelectAll" />
              </th>
              <th>ID</th>
              <th>用例名称</th>
              <th>类型</th>
              <th>优先级</th>
              <th>状态</th>
              <th>负责人</th>
              <th>执行次数</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredCases" :key="`${item.caseType}-${item.id}`">
              <td class="checkbox-cell">
                <input type="checkbox" :checked="selectedRows.includes(item.rowKey)" @change="toggleSelectRow(item.rowKey)" />
              </td>
              <td>{{ item.id }}</td>
              <td class="name-cell">
                <strong>{{ item.name }}</strong>
                <small>{{ item.description || item.url || item.base_url || '暂无补充描述' }}</small>
              </td>
              <td>
                <span class="type-pill" :class="item.caseType">{{ item.caseType === 'api' ? 'API测试' : 'UI测试' }}</span>
              </td>
              <td><span class="tag-pill">{{ item.priority }}</span></td>
              <td><span class="status-pill" :class="item.statusClass">{{ item.statusLabel }}</span></td>
              <td>{{ item.owner }}</td>
              <td>{{ item.execCount }}</td>
              <td>{{ item.updatedLabel }}</td>
              <td>
                <div class="link-group">
                  <button class="link-btn" @click="openRunTarget(item)">执行</button>
                  <button class="link-btn" @click="openDrawer(item)">详情</button>
                  <button class="link-btn" @click="openEditTarget(item)">编辑</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="selectedCase" class="drawer-mask" @click.self="selectedCase = null">
      <div class="drawer-card">
        <div class="drawer-head">
          <h2>用例详情</h2>
          <button class="close-btn" @click="selectedCase = null">×</button>
        </div>

        <div class="drawer-body">
          <div class="detail-grid">
            <div><label>用例名称</label><span>{{ selectedCase.name }}</span></div>
            <div><label>用例类型</label><span>{{ selectedCase.caseType === 'api' ? 'API测试' : 'UI测试' }}</span></div>
            <div><label>项目</label><span>{{ selectedProject?.name || '--' }}</span></div>
            <div><label>状态</label><span>{{ selectedCase.statusLabel }}</span></div>
          </div>

          <div class="detail-section">
            <h3>基础信息</h3>
            <div class="detail-box">
              <template v-if="selectedCase.caseType === 'api'">
                <p><strong>请求方法：</strong>{{ selectedCase.method }}</p>
                <p><strong>请求地址：</strong>{{ selectedCase.url }}</p>
                <p><strong>期望状态：</strong>{{ selectedCase.expected_status || 200 }}</p>
              </template>
              <template v-else>
                <p><strong>Base URL：</strong>{{ selectedCase.base_url || '--' }}</p>
                <p><strong>步骤数：</strong>{{ selectedCase.steps?.length || 0 }}</p>
                <p><strong>描述：</strong>{{ selectedCase.description || '--' }}</p>
              </template>
            </div>
          </div>

          <div class="detail-section">
            <h3>测试描述</h3>
            <div class="detail-box">
              <p v-if="selectedCase.caseType === 'api'">
                当前项目暂无统一测试用例中心的完整字段模型，此处展示 API / UI 资产的基础信息，更多编辑能力请进入对应项目页。
              </p>
              <p v-else>
                UI 测试用例详情已按设计稿预留，当前统一用例中心主要用于跨类型浏览和快速跳转。
              </p>
            </div>
          </div>

          <div class="detail-section">
            <h3>预留区域</h3>
            <div class="detail-box">
              <p>前置条件、步骤编排、执行次数、责任人治理等统一字段将在后续“测试用例中心”能力中接入。</p>
            </div>
          </div>

          <div class="drawer-actions">
            <button class="primary-btn" @click="openRunTarget(selectedCase)">立即前往执行</button>
            <button class="ghost-btn" @click="openEditTarget(selectedCase)">前往编辑页</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getProjects } from '@/api/projects'
import { getTestCases } from '@/api/testCases'
import { getWebTestCases } from '@/api/webTestCases'
import { getActiveProjectId, setActiveProjectId } from '@/utils/projectContext'

const router = useRouter()

const loading = ref(false)
const projects = ref([])
const apiCases = ref([])
const webCases = ref([])
const keyword = ref('')
const selectedProjectId = ref(getActiveProjectId() ? String(getActiveProjectId()) : '')
const selectedRows = ref([])
const selectedCase = ref(null)

const selectedProject = computed(() => projects.value.find((item) => String(item.id) === selectedProjectId.value) || null)

const mergedCases = computed(() => {
  const apiRows = apiCases.value.map((item) => ({
    ...item,
    caseType: 'api',
    rowKey: `api-${item.id}`,
    priority: '中',
    statusLabel: '待执行',
    statusClass: 'pending',
    owner: '当前项目',
    execCount: '--',
    updatedLabel: formatDate(item.updated_at || item.created_at),
  }))
  const webRows = webCases.value.map((item) => ({
    ...item,
    caseType: 'web',
    rowKey: `web-${item.id}`,
    priority: '中',
    statusLabel: '待执行',
    statusClass: 'pending',
    owner: '当前项目',
    execCount: '--',
    updatedLabel: formatDate(item.updated_at || item.created_at),
  }))
  return [...apiRows, ...webRows]
})

const filteredCases = computed(() => {
  if (!keyword.value) return mergedCases.value
  const query = keyword.value.toLowerCase()
  return mergedCases.value.filter((item) => {
    return [
      item.name,
      item.description,
      item.url,
      item.base_url,
    ]
      .filter(Boolean)
      .some((text) => String(text).toLowerCase().includes(query))
  })
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

const fetchProjects = async () => {
  projects.value = await getProjects()
  if (!selectedProjectId.value && projects.value.length) {
    selectedProjectId.value = String(projects.value[0].id)
    setActiveProjectId(projects.value[0].id)
  }
}

const fetchCases = async () => {
  if (!selectedProjectId.value) {
    apiCases.value = []
    webCases.value = []
    return
  }
  loading.value = true
  try {
    const projectId = Number(selectedProjectId.value)
    const [apiResp, webResp] = await Promise.all([
      getTestCases(projectId),
      getWebTestCases(projectId),
    ])
    apiCases.value = apiResp
    webCases.value = webResp
    selectedRows.value = []
  } catch (err) {
    alert(err.response?.data?.detail || '加载测试用例失败')
  } finally {
    loading.value = false
  }
}

const refreshAll = async () => {
  await fetchProjects()
  await fetchCases()
}

const handleProjectChange = async () => {
  if (selectedProjectId.value) {
    setActiveProjectId(selectedProjectId.value)
  }
  await fetchCases()
}

const toggleSelectAll = () => {
  if (selectedRows.value.length === filteredCases.value.length) {
    selectedRows.value = []
    return
  }
  selectedRows.value = filteredCases.value.map((item) => item.rowKey)
}

const toggleSelectRow = (rowKey) => {
  if (selectedRows.value.includes(rowKey)) {
    selectedRows.value = selectedRows.value.filter((item) => item !== rowKey)
    return
  }
  selectedRows.value = [...selectedRows.value, rowKey]
}

const openDrawer = (item) => {
  selectedCase.value = item
}

const openSelectedDetail = () => {
  if (selectedRows.value.length !== 1) return
  const row = filteredCases.value.find((item) => item.rowKey === selectedRows.value[0])
  if (row) openDrawer(row)
}

const openSelectedProjectApi = () => {
  if (!selectedProjectId.value) return
  router.push(`/project/${selectedProjectId.value}`)
}

const openRunTarget = (item) => {
  if (item.caseType === 'api') {
    router.push(`/project/${selectedProjectId.value}`)
    return
  }
  router.push(`/project/${selectedProjectId.value}/web-test-cases`)
}

const openEditTarget = (item) => {
  if (item.caseType === 'api') {
    router.push(`/project/${selectedProjectId.value}`)
    return
  }
  router.push(`/project/${selectedProjectId.value}/web-test-cases`)
}

onMounted(refreshAll)
</script>

<style scoped>
.cases-page { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.toolbar-card,
.table-card,
.drawer-card,
.state-card,
.batch-bar { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); box-shadow: var(--surface-shadow); }
.toolbar-card { padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.toolbar-left { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.filter-group { display: flex; align-items: center; gap: 8px; }
.filter-group label { font-size: 13px; color: var(--text-main); }
.filter-group select,
.toolbar-search input { height: 32px; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: var(--bg-card); color: var(--text-main); outline: none; }
.filter-group select { min-width: 180px; padding: 0 12px; }
.toolbar-search input { width: 300px; padding: 0 12px; }
.batch-bar { padding: 12px 16px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; font-size: 13px; color: var(--text-main); }
.state-card { min-height: 160px; display: grid; place-items: center; text-align: center; color: var(--text-muted); }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table thead tr { background: var(--bg-muted); border-bottom: 1px solid var(--border-color); }
.data-table th { padding: 12px 16px; text-align: left; font-size: 13px; font-weight: 500; color: var(--text-main); }
.data-table td { padding: 14px 16px; border-bottom: 1px solid var(--border-color); font-size: 13px; color: var(--text-main); vertical-align: top; }
.checkbox-cell { width: 48px; text-align: center !important; }
.name-cell { display: flex; flex-direction: column; gap: 4px; }
.name-cell strong { color: var(--text-strong); }
.name-cell small { color: var(--text-muted); }
.type-pill,
.tag-pill,
.status-pill { display: inline-flex; align-items: center; justify-content: center; padding: 4px 10px; border-radius: 999px; font-size: 12px; }
.type-pill.api { background: #e3f2fd; color: #3498db; }
.type-pill.web { background: #f0e6ff; color: #9b59b6; }
.tag-pill { background: #fff8e1; color: #f39c12; }
.status-pill.pending { background: #e3f2fd; color: #3498db; }
.link-group { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.link-btn,
.primary-btn,
.ghost-btn { min-height: 32px; padding: 0 14px; border-radius: var(--radius); font-size: 13px; }
.link-btn { border: 0; background: transparent; color: var(--primary); padding: 0; min-height: auto; }
.primary-btn { border: 1px solid var(--primary); background: var(--primary); color: #fff; }
.ghost-btn { border: 1px solid var(--border-color-strong); background: transparent; color: var(--text-main); }
.drawer-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.32); display: flex; justify-content: flex-end; z-index: 999; }
.drawer-card { width: min(640px, 100%); height: 100%; overflow-y: auto; }
.drawer-head { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px; border-bottom: 1px solid var(--border-color); }
.drawer-head h2 { margin: 0; font-size: 18px; color: var(--text-strong); }
.close-btn { border: 0; background: transparent; color: var(--text-muted); font-size: 20px; }
.drawer-body { padding: 24px; display: flex; flex-direction: column; gap: 20px; }
.detail-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.detail-grid div { display: flex; flex-direction: column; gap: 6px; }
.detail-grid label,
.detail-section h3 { font-size: 13px; color: var(--text-muted); }
.detail-grid span { font-size: 14px; color: var(--text-strong); }
.detail-section { display: flex; flex-direction: column; gap: 10px; }
.detail-box { padding: 14px; border-radius: var(--radius); background: var(--bg-muted); color: var(--text-main); line-height: 1.7; }
.detail-box p { margin: 0 0 8px; }
.drawer-actions { display: flex; gap: 12px; }

@media (max-width: 960px) {
  .cases-page { padding: 16px; }
  .toolbar-card,
  .toolbar-left { flex-direction: column; align-items: flex-start; }
  .toolbar-search input { width: 100%; }
  .detail-grid { grid-template-columns: 1fr; }
}
</style>
