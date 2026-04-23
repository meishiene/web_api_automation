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
            <option value="api">API测试</option>
            <option value="web">UI测试</option>
          </select>
        </div>

        <div class="filter-group">
          <label>趋势粒度:</label>
          <select v-model="filters.granularity">
            <option value="day">按日</option>
            <option value="week">按周</option>
          </select>
        </div>

        <button class="toolbar-btn primary" @click="applyFilters">查询</button>
      </div>

      <div class="toolbar-actions">
        <button class="toolbar-btn" @click="exportReportSnapshot">导出快照</button>
        <button class="toolbar-btn" @click="resetFilters">重置筛选</button>
      </div>
    </div>

    <div class="chart-grid">
      <section class="panel-card">
        <h3>测试执行趋势</h3>
        <div class="trend-chart">
          <div class="trend-lines">
            <div v-for="item in trendRows" :key="item.label" class="trend-row">
              <div class="trend-label">{{ item.label }}</div>
              <div class="trend-track">
                <div class="trend-line total" :style="{ width: `${item.totalWidth}%` }"></div>
                <div class="trend-line pass" :style="{ width: `${item.passWidth}%` }"></div>
                <div class="trend-line fail" :style="{ width: `${item.failWidth}%` }"></div>
              </div>
              <div class="trend-meta">
                <span>总 {{ item.total }}</span>
                <span>过 {{ item.pass }}</span>
                <span>失 {{ item.fail }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="panel-card">
        <h3>通过率分析</h3>
        <div class="summary-circle">
          <div class="circle-core">
            <strong>{{ asPercent(summary.pass_rate) }}</strong>
            <span>通过率</span>
          </div>
        </div>
        <div class="legend-row">
          <div class="legend-item"><span class="dot total"></span>总数 {{ summary.total_count }}</div>
          <div class="legend-item"><span class="dot pass"></span>通过 {{ summary.success_count }}</div>
          <div class="legend-item"><span class="dot fail"></span>失败 {{ summary.failed_count + summary.error_count }}</div>
        </div>
      </section>
    </div>

    <section class="panel-card">
      <div class="panel-head">
        <h3>测试报告列表</h3>
      </div>

      <div v-if="loading" class="state-block">
        <p>正在加载报告...</p>
      </div>
      <div v-else-if="reportRows.length === 0" class="state-block">
        <p>当前筛选条件下暂无报告数据。</p>
      </div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>报告名称</th>
              <th>类型</th>
              <th>执行时间</th>
              <th>总用例</th>
              <th>通过</th>
              <th>失败</th>
              <th>通过率</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in reportRows" :key="row.id">
              <td class="report-name">{{ row.name }}</td>
              <td><span class="tag-pill">{{ row.type }}</span></td>
              <td>{{ row.execTime }}</td>
              <td>{{ row.totalCases }}</td>
              <td class="success-text">{{ row.passCases }}</td>
              <td class="danger-text">{{ row.failCases }}</td>
              <td>
                <div class="rate-cell">
                  <div class="rate-track">
                    <div class="rate-fill" :style="{ width: row.passRate }"></div>
                  </div>
                  <span>{{ row.passRate }}</span>
                </div>
              </td>
              <td>
                <div class="link-group">
                  <button class="table-link" @click="openRowDetail(row)">详情</button>
                  <button class="table-link" @click="openRowDetail(row)">查看</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="selectedReport" class="modal-mask" @click.self="selectedReport = null">
      <div class="modal-card">
        <div class="modal-head">
          <div>
            <h2>测试报告详情</h2>
            <p>{{ selectedReport.name }}</p>
          </div>
          <button class="close-btn" @click="selectedReport = null">✕</button>
        </div>

        <div class="detail-actions">
          <button class="toolbar-btn" @click="router.push(`/project/${projectId}/executions`)">打开执行中心</button>
          <button class="toolbar-btn" @click="openFirstFailureInReport" :disabled="failures.items.length === 0">定位首个失败</button>
        </div>

        <div class="detail-stack">
          <section class="detail-section">
            <h3>基本信息</h3>
            <div class="detail-grid">
              <div><label>测试类型:</label><span>{{ selectedReport.type }}</span></div>
              <div><label>执行时间:</label><span>{{ selectedReport.execTime }}</span></div>
              <div><label>总用例:</label><span>{{ selectedReport.totalCases }}</span></div>
              <div><label>通过率:</label><span class="success-text">{{ selectedReport.passRate }}</span></div>
            </div>
          </section>

          <section class="detail-section">
            <h3>Top 失败项</h3>
            <div v-if="summary.top_failures.length === 0" class="detail-empty">当前没有失败项。</div>
            <div v-else class="detail-list">
              <div v-for="item in summary.top_failures" :key="`${item.run_type}-${item.case_id}-${item.failure_category}`" class="detail-card">
                <div class="detail-card-head">
                  <strong>{{ item.case_name }}</strong>
                  <span class="tag-pill">{{ item.run_type === 'api' ? 'API测试' : 'UI测试' }}</span>
                </div>
                <div class="detail-card-copy">
                  分类：{{ item.failure_category }} / 次数：{{ item.count }}
                </div>
                <div class="detail-card-error">{{ item.last_error_message || '无错误信息' }}</div>
              </div>
            </div>
          </section>

          <section class="detail-section">
            <h3>失败治理记录</h3>
            <div v-if="failures.items.length === 0" class="detail-empty">当前没有失败治理记录。</div>
            <div v-else class="detail-list">
              <div v-for="item in failures.items" :key="`${item.run_type}-${item.run_id}`" class="detail-card">
                <div class="detail-card-head">
                  <strong>#{{ item.run_id }} · {{ item.case_name }}</strong>
                  <button class="table-link" @click="openFailureDetail(item)">追溯详情</button>
                </div>
                <div class="detail-card-copy">
                  {{ item.run_type === 'api' ? 'API测试' : 'UI测试' }} / {{ item.failure_category }} / {{ formatDate(item.created_at) }}
                </div>
                <div class="detail-card-error">{{ item.error_message || '无错误信息' }}</div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProjectReportFailures, getProjectReportSummary, getProjectReportTrends } from '@/api/reporting'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.projectId)

const loading = ref(false)
const selectedReport = ref(null)
const filters = ref({
  run_type: '',
  created_from_local: '',
  created_to_local: '',
  top_n: 5,
  granularity: 'day',
})
const governanceFilters = ref({
  failure_category: '',
})

const summary = ref({
  project_id: projectId,
  total_count: 0,
  completed_count: 0,
  success_count: 0,
  failed_count: 0,
  error_count: 0,
  running_count: 0,
  pass_rate: 0,
  fail_rate: 0,
  top_failures: [],
})

const trends = ref({
  project_id: projectId,
  granularity: 'day',
  items: [],
})

const failures = ref({
  total: 0,
  page: 1,
  page_size: 10,
  items: [],
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

const asPercent = (value) => `${((Number(value) || 0) * 100).toFixed(1)}%`

const localDatetimeToUnixSeconds = (value) => {
  if (!value) return undefined
  const ts = Math.floor(new Date(value).getTime() / 1000)
  return Number.isNaN(ts) ? undefined : ts
}

const buildParams = () => ({
  run_type: filters.value.run_type || undefined,
  created_from: localDatetimeToUnixSeconds(filters.value.created_from_local),
  created_to: localDatetimeToUnixSeconds(filters.value.created_to_local),
  top_n: filters.value.top_n,
})

const buildTrendParams = () => ({
  run_type: filters.value.run_type || undefined,
  created_from: localDatetimeToUnixSeconds(filters.value.created_from_local),
  created_to: localDatetimeToUnixSeconds(filters.value.created_to_local),
  granularity: filters.value.granularity,
})

const buildFailureParams = () => ({
  run_type: filters.value.run_type || undefined,
  failure_category: governanceFilters.value.failure_category || undefined,
  created_from: localDatetimeToUnixSeconds(filters.value.created_from_local),
  created_to: localDatetimeToUnixSeconds(filters.value.created_to_local),
  page: 1,
  page_size: 10,
})

const trendRows = computed(() => {
  const items = trends.value.items || []
  if (!items.length) return []
  const maxTotal = Math.max(...items.map((item) => item.total_count), 1)
  return items.map((item) => ({
    label: item.bucket_label,
    total: item.total_count,
    pass: item.success_count,
    fail: item.failed_count + item.error_count,
    totalWidth: Math.max(8, (item.total_count / maxTotal) * 100),
    passWidth: item.total_count ? Math.max(6, (item.success_count / maxTotal) * 100) : 0,
    failWidth: item.total_count ? Math.max(6, ((item.failed_count + item.error_count) / maxTotal) * 100) : 0,
  }))
})

const reportRows = computed(() => {
  const buckets = trends.value.items || []
  return buckets.map((item, index) => ({
    id: `${item.bucket_start}-${index}`,
    name: `${filters.value.granularity === 'week' ? '周报' : '日报'} · ${item.bucket_label}`,
    type: filters.value.run_type === 'web' ? 'UI测试' : filters.value.run_type === 'api' ? 'API测试' : '混合测试',
    execTime: item.bucket_label,
    totalCases: item.total_count,
    passCases: item.success_count,
    failCases: item.failed_count + item.error_count,
    passRate: asPercent(item.pass_rate),
  }))
})

const fetchAll = async () => {
  loading.value = true
  try {
    const [summaryResp, trendResp, failuresResp] = await Promise.all([
      getProjectReportSummary(projectId, buildParams()),
      getProjectReportTrends(projectId, buildTrendParams()),
      getProjectReportFailures(projectId, buildFailureParams()),
    ])
    summary.value = summaryResp
    trends.value = trendResp
    failures.value = failuresResp
  } catch (err) {
    alert(err.response?.data?.detail || '获取报告数据失败')
  } finally {
    loading.value = false
  }
}

const applyFilters = async () => {
  await fetchAll()
}

const resetFilters = async () => {
  filters.value = {
    run_type: '',
    created_from_local: '',
    created_to_local: '',
    top_n: 5,
    granularity: 'day',
  }
  governanceFilters.value.failure_category = ''
  selectedReport.value = null
  await fetchAll()
}

const openFailureDetail = (item) => {
  if (item.run_type === 'web') {
    router.push(`/project/${projectId}/web-runs/${item.run_id}`)
    return
  }
  router.push(`/project/${projectId}/runs/${item.run_id}`)
}

const openFirstFailureInReport = () => {
  if (!failures.items.length) return
  openFailureDetail(failures.items[0])
}

const openRowDetail = (row) => {
  selectedReport.value = row
}

const exportReportSnapshot = () => {
  const payload = {
    filters: filters.value,
    summary: summary.value,
    trends: trends.value,
    failures: failures.value,
  }
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `report-summary-project-${projectId}.json`
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(fetchAll)
</script>

<style scoped>
.reports-page { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.toolbar-card, .panel-card, .modal-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); box-shadow: var(--surface-shadow); }
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
.trend-chart { min-height: 280px; display: flex; align-items: center; }
.trend-lines { width: 100%; display: flex; flex-direction: column; gap: 14px; }
.trend-row { display: grid; grid-template-columns: 70px 1fr 170px; gap: 12px; align-items: center; }
.trend-label { font-size: 12px; color: var(--text-main); }
.trend-track { height: 36px; border-radius: var(--radius); background: var(--bg-muted); position: relative; overflow: hidden; }
.trend-line { position: absolute; left: 0; border-radius: 0 var(--radius) var(--radius) 0; }
.trend-line.total { top: 6px; height: 8px; background: rgba(52, 152, 219, 0.35); }
.trend-line.pass { top: 14px; height: 8px; background: var(--success); }
.trend-line.fail { top: 22px; height: 8px; background: var(--danger); }
.trend-meta { display: flex; align-items: center; gap: 10px; font-size: 12px; color: var(--text-muted); }
.summary-circle { min-height: 220px; display: grid; place-items: center; }
.circle-core { width: 160px; height: 160px; border-radius: 50%; border: 12px solid rgba(39, 174, 96, 0.18); display: grid; place-items: center; text-align: center; }
.circle-core strong { display: block; font-size: 26px; color: var(--text-strong); }
.circle-core span { font-size: 12px; color: var(--text-muted); }
.legend-row { display: flex; justify-content: center; gap: 18px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-main); }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.dot.total { background: var(--primary); }
.dot.pass { background: var(--success); }
.dot.fail { background: var(--danger); }
.panel-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table thead tr { background: var(--bg-muted); border-bottom: 1px solid var(--border-color); }
.data-table th { padding: 12px 16px; text-align: left; font-size: 13px; font-weight: 500; color: var(--text-main); }
.data-table td { padding: 14px 16px; border-bottom: 1px solid var(--border-color); font-size: 13px; color: var(--text-main); vertical-align: top; }
.report-name { color: var(--text-strong); font-weight: 500; }
.tag-pill { display: inline-flex; align-items: center; justify-content: center; padding: 4px 10px; border-radius: 999px; font-size: 12px; background: var(--bg-muted); color: var(--text-main); }
.success-text { color: var(--success); }
.danger-text { color: var(--danger); }
.rate-cell { display: flex; align-items: center; gap: 10px; }
.rate-track { flex: 1; height: 6px; border-radius: 999px; background: var(--border-color); overflow: hidden; }
.rate-fill { height: 100%; border-radius: 999px; background: var(--success); }
.link-group { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.table-link { border: 0; background: transparent; color: var(--primary); font-size: 13px; padding: 0; }
.state-block { min-height: 220px; display: grid; place-items: center; text-align: center; color: var(--text-muted); }
.modal-mask { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.3); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 999; }
.modal-card { width: min(920px, 100%); max-height: 86vh; overflow-y: auto; padding: 24px; }
.modal-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 18px; }
.modal-head h2 { margin: 0 0 6px; font-size: 18px; font-weight: 500; color: var(--text-strong); }
.modal-head p { margin: 0; font-size: 13px; color: var(--text-muted); }
.close-btn { border: 0; background: transparent; color: var(--text-muted); font-size: 18px; }
.detail-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.detail-stack { display: flex; flex-direction: column; gap: 20px; }
.detail-section h3 { margin: 0 0 14px; font-size: 16px; font-weight: 500; color: var(--text-strong); }
.detail-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 20px; }
.detail-grid div { display: flex; gap: 10px; font-size: 13px; }
.detail-grid label { width: 84px; color: var(--text-muted); }
.detail-grid span { color: var(--text-main); }
.detail-list { display: flex; flex-direction: column; gap: 12px; }
.detail-card { border: 1px solid var(--border-color); border-radius: var(--radius); padding: 14px; background: var(--bg-muted); }
.detail-card-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 8px; }
.detail-card-head strong { color: var(--text-strong); font-size: 14px; }
.detail-card-copy { font-size: 13px; color: var(--text-muted); margin-bottom: 8px; }
.detail-card-error { font-size: 12px; color: var(--text-main); line-height: 1.6; }
.detail-empty { min-height: 100px; display: grid; place-items: center; text-align: center; color: var(--text-muted); border: 1px dashed var(--border-color); border-radius: var(--radius); }
@media (max-width: 1100px) { .chart-grid { grid-template-columns: 1fr; } }
@media (max-width: 860px) { .reports-page { padding: 16px; } .toolbar-card, .panel-card, .modal-card { padding: 16px; } .toolbar-filters { flex-direction: column; align-items: flex-start; } .filter-group, .date-range { width: 100%; flex-wrap: wrap; } .filter-group select, .filter-group input { width: 100%; } .trend-row, .detail-grid { grid-template-columns: 1fr; } .trend-meta { flex-wrap: wrap; } .detail-grid div { flex-direction: column; } .detail-grid label { width: auto; } }
</style>
