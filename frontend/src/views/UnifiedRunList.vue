<template>
  <section class="reports-page">
    <div class="toolbar-card">
      <div class="toolbar-filters">
        <div class="filter-group">
          <label>时间范围:</label>
          <div class="date-range">
            <input v-model="filters.created_from_local" type="datetime-local" />
            <span>至</span>
            <input v-model="filters.created_to_local" type="datetime-local" />
          </div>
        </div>

        <div class="filter-group">
          <label>测试类型:</label>
          <select v-model="filters.run_type">
            <option value="">全部</option>
            <option value="api">API</option>
            <option value="web">Web</option>
          </select>
        </div>

        <div class="filter-group">
          <label>执行状态:</label>
          <select v-model="filters.status">
            <option value="">全部</option>
            <option value="success">success</option>
            <option value="failed">failed</option>
            <option value="error">error</option>
            <option value="running">running</option>
          </select>
        </div>

        <button class="toolbar-btn primary" @click="applyFilters">查询</button>
      </div>

      <button class="toolbar-btn" @click="showFailedOnly">只看失败</button>
    </div>

    <div class="chart-grid">
      <section class="panel-card">
        <h3>执行趋势</h3>
        <div class="chart-area">
          <div class="chart-bars">
            <div v-for="item in trendBars" :key="item.label" class="bar-item">
              <div class="bar-stack">
                <div class="bar total" :style="{ height: `${item.totalHeight}%` }"></div>
                <div class="bar fail" :style="{ height: `${item.failHeight}%` }"></div>
              </div>
              <span>{{ item.label }}</span>
            </div>
          </div>
        </div>
      </section>

      <section class="panel-card">
        <h3>当前页结果分布</h3>
        <div class="summary-circle">
          <div class="circle-core">
            <strong>{{ total }}</strong>
            <span>总记录</span>
          </div>
        </div>
        <div class="legend-row">
          <div class="legend-item"><span class="dot success"></span>成功 {{ successCount }}</div>
          <div class="legend-item"><span class="dot fail"></span>失败 {{ failedCount }}</div>
          <div class="legend-item"><span class="dot running"></span>运行中 {{ runningCount }}</div>
        </div>
      </section>
    </div>

    <section class="panel-card">
      <div class="panel-head">
        <h3>执行记录列表</h3>
        <div class="panel-actions">
          <button class="toolbar-btn" @click="resetFilters">重置</button>
          <button class="toolbar-btn" @click="openFirstFailed" :disabled="!firstFailedItem">快速定位失败</button>
        </div>
      </div>

      <div v-if="loading" class="state-block">
        <p>正在加载执行记录...</p>
      </div>
      <div v-else-if="runs.length === 0" class="state-block">
        <p>当前筛选条件下暂无执行记录。</p>
      </div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Run ID</th>
              <th>测试名称</th>
              <th>类型</th>
              <th>状态</th>
              <th>耗时</th>
              <th>执行时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in runs" :key="`${item.run_type}-${item.run_id}`">
              <td>#{{ item.run_id }}</td>
              <td>
                <div class="name-cell">
                  <strong>{{ item.case_name }}</strong>
                  <small>#{{ item.case_id }}</small>
                </div>
              </td>
              <td>
                <span class="tag-pill">{{ item.run_type === 'api' ? 'API测试' : 'UI测试' }}</span>
              </td>
              <td>
                <span class="status-pill" :class="item.status">{{ item.status }}</span>
              </td>
              <td>{{ item.duration_ms ?? '--' }}{{ item.duration_ms ? ' ms' : '' }}</td>
              <td>{{ formatDate(item.created_at) }}</td>
              <td>
                <div class="link-group">
                  <button class="table-link" @click="openDetail(item)">详情</button>
                  <button class="table-link" @click="rerunItem(item)">重跑</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <div class="pagination-meta">共 {{ total }} 条记录，每页 {{ pageSize }} 条</div>
        <div class="pagination-actions">
          <button class="toolbar-btn" @click="prevPage" :disabled="page <= 1">上一页</button>
          <button class="page-chip active">{{ page }}</button>
          <button class="toolbar-btn" @click="nextPage" :disabled="page >= totalPages">下一页</button>
        </div>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { runTestCase } from '@/api/testCases'
import { getUnifiedRuns } from '@/api/unifiedRuns'
import { runWebTestCase } from '@/api/webTestRuns'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.projectId)

const loading = ref(false)
const runs = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filters = ref({
  run_type: '',
  status: '',
  created_from_local: '',
  created_to_local: '',
})

const failedCount = computed(() => runs.value.filter((item) => item.status === 'failed' || item.status === 'error').length)
const successCount = computed(() => runs.value.filter((item) => item.status === 'success').length)
const runningCount = computed(() => runs.value.filter((item) => item.status === 'running').length)
const firstFailedItem = computed(() => runs.value.find((item) => item.status === 'failed' || item.status === 'error') || null)
const totalPages = computed(() => (total.value ? Math.ceil(total.value / pageSize.value) : 1))

const trendBars = computed(() => {
  if (!runs.value.length) return []
  const buckets = runs.value.reduce((acc, item) => {
    const day = new Date(normalizeTimestamp(item.created_at)).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
    if (!acc[day]) {
      acc[day] = { total: 0, fail: 0 }
    }
    acc[day].total += 1
    if (item.status === 'failed' || item.status === 'error') {
      acc[day].fail += 1
    }
    return acc
  }, {})

  const entries = Object.entries(buckets).slice(-7)
  const maxTotal = Math.max(...entries.map(([, value]) => value.total), 1)
  return entries.map(([label, value]) => ({
    label,
    totalHeight: Math.max(10, (value.total / maxTotal) * 100),
    failHeight: value.fail ? Math.max(8, (value.fail / maxTotal) * 100) : 0,
  }))
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

const localDatetimeToUnixSeconds = (value) => {
  if (!value) return undefined
  const ts = Math.floor(new Date(value).getTime() / 1000)
  return Number.isNaN(ts) ? undefined : ts
}

const buildParams = () => ({
  page: page.value,
  page_size: pageSize.value,
  run_type: filters.value.run_type || undefined,
  status: filters.value.status || undefined,
  created_from: localDatetimeToUnixSeconds(filters.value.created_from_local),
  created_to: localDatetimeToUnixSeconds(filters.value.created_to_local),
})

const fetchRuns = async () => {
  loading.value = true
  try {
    const response = await getUnifiedRuns(projectId, buildParams())
    runs.value = response.items || []
    total.value = response.total || 0
    page.value = response.page || 1
    pageSize.value = response.page_size || pageSize.value
  } catch (err) {
    alert(err.response?.data?.detail || '获取统一执行记录失败')
  } finally {
    loading.value = false
  }
}

const applyFilters = async () => {
  page.value = 1
  await fetchRuns()
}

const resetFilters = async () => {
  filters.value = {
    run_type: '',
    status: '',
    created_from_local: '',
    created_to_local: '',
  }
  page.value = 1
  pageSize.value = 20
  await fetchRuns()
}

const showFailedOnly = async () => {
  filters.value.status = 'failed'
  page.value = 1
  await fetchRuns()
}

const openDetail = (item) => {
  if (item.run_type === 'web') {
    router.push(`/project/${projectId}/web-runs/${item.run_id}`)
    return
  }
  router.push(`/project/${projectId}/runs/${item.run_id}`)
}

const rerunItem = async (item) => {
  try {
    if (item.run_type === 'web') {
      const result = await runWebTestCase(item.case_id)
      router.push(`/project/${projectId}/web-runs/${result.id}`)
      return
    }
    const result = await runTestCase(projectId, item.case_id, {})
    router.push(`/project/${projectId}/runs/${result.id}`)
  } catch (err) {
    alert(err.response?.data?.detail || '重跑失败')
  }
}

const openFirstFailed = () => {
  if (!firstFailedItem.value) return
  openDetail(firstFailedItem.value)
}

const prevPage = async () => {
  if (page.value <= 1) return
  page.value -= 1
  await fetchRuns()
}

const nextPage = async () => {
  if (page.value >= totalPages.value) return
  page.value += 1
  await fetchRuns()
}

onMounted(fetchRuns)
</script>

<style scoped>
.reports-page { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.toolbar-card, .panel-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); box-shadow: var(--surface-shadow); }
.toolbar-card { padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.toolbar-filters { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.filter-group { display: flex; align-items: center; gap: 10px; }
.filter-group label { font-size: 13px; color: var(--text-main); }
.filter-group select, .filter-group input { height: 32px; padding: 0 12px; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: var(--bg-card); color: var(--text-main); outline: none; }
.date-range { display: flex; align-items: center; gap: 8px; }
.toolbar-btn { min-height: 32px; padding: 0 14px; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: transparent; color: var(--text-main); font-size: 13px; }
.toolbar-btn.primary { background: var(--primary); border-color: var(--primary); color: #fff; }
.chart-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; }
.panel-card { padding: 20px; }
.panel-card h3 { margin: 0 0 16px; font-size: 16px; font-weight: 500; color: var(--text-strong); }
.chart-area { min-height: 280px; display: flex; align-items: end; justify-content: center; }
.chart-bars { width: 100%; height: 220px; display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 14px; align-items: end; }
.bar-item { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.bar-stack { width: 100%; height: 190px; display: flex; flex-direction: column; justify-content: flex-end; gap: 6px; }
.bar { width: 100%; border-radius: 6px 6px 0 0; }
.bar.total { background: var(--primary); opacity: 0.75; }
.bar.fail { background: var(--danger); }
.bar-item span { font-size: 12px; color: var(--text-muted); }
.summary-circle { min-height: 220px; display: grid; place-items: center; }
.circle-core { width: 160px; height: 160px; border-radius: 50%; border: 12px solid rgba(52, 152, 219, 0.18); display: grid; place-items: center; text-align: center; }
.circle-core strong { display: block; font-size: 28px; color: var(--text-strong); }
.circle-core span { font-size: 12px; color: var(--text-muted); }
.legend-row { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-main); }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.dot.success { background: var(--success); }
.dot.fail { background: var(--danger); }
.dot.running { background: var(--primary); }
.panel-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
.panel-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table thead tr { background: var(--bg-muted); border-bottom: 1px solid var(--border-color); }
.data-table th { padding: 12px 16px; text-align: left; font-size: 13px; font-weight: 500; color: var(--text-main); }
.data-table td { padding: 14px 16px; border-bottom: 1px solid var(--border-color); font-size: 13px; color: var(--text-main); vertical-align: top; }
.name-cell { display: flex; flex-direction: column; gap: 4px; }
.name-cell strong { color: var(--text-strong); }
.name-cell small { color: var(--text-muted); }
.tag-pill, .status-pill { display: inline-flex; align-items: center; justify-content: center; padding: 4px 10px; border-radius: 999px; font-size: 12px; }
.tag-pill { background: var(--bg-muted); color: var(--text-main); }
.status-pill.success { background: rgba(39, 174, 96, 0.12); color: var(--success); }
.status-pill.failed, .status-pill.error { background: rgba(231, 76, 60, 0.12); color: var(--danger); }
.status-pill.running { background: rgba(52, 152, 219, 0.12); color: var(--primary); }
.table-link { border: 0; background: transparent; color: var(--primary); font-size: 13px; padding: 0; }
.state-block { min-height: 220px; display: grid; place-items: center; text-align: center; color: var(--text-muted); }
.pagination { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 16px; flex-wrap: wrap; }
.pagination-meta { font-size: 13px; color: var(--text-main); }
.pagination-actions { display: flex; align-items: center; gap: 8px; }
.page-chip { min-width: 32px; height: 32px; border: 0; border-radius: var(--radius); background: var(--primary); color: #fff; font-size: 13px; }
@media (max-width: 1100px) { .chart-grid { grid-template-columns: 1fr; } }
@media (max-width: 860px) { .reports-page { padding: 16px; } .toolbar-card, .panel-card { padding: 16px; } .toolbar-filters { flex-direction: column; align-items: flex-start; } .filter-group, .date-range { width: 100%; flex-wrap: wrap; } .filter-group select, .filter-group input { width: 100%; } .panel-head, .pagination { flex-direction: column; align-items: flex-start; } }
</style>
