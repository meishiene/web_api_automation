<template>
  <section class="report-page">
    <div class="hero-card">
      <div>
        <router-link :to="`/project/${projectId}`" class="back-link">← 返回 API 用例页</router-link>
        <span class="eyebrow">Report Center</span>
        <h2>项目执行摘要</h2>
        <p>汇总项目执行结果，展示通过率、失败率和 Top 失败项。</p>
      </div>
      <button class="secondary-btn" @click="fetchAll" :disabled="loading">
        {{ loading ? '刷新中...' : '刷新数据' }}
      </button>
    </div>

    <section class="panel-card">
      <div class="filter-bar">
        <label>
          <span>类型</span>
          <select v-model="filters.run_type">
            <option value="">全部</option>
            <option value="api">API</option>
            <option value="web">Web</option>
          </select>
        </label>
        <label>
          <span>开始时间</span>
          <input v-model="filters.created_from_local" type="datetime-local" />
        </label>
        <label>
          <span>结束时间</span>
          <input v-model="filters.created_to_local" type="datetime-local" />
        </label>
        <label>
          <span>Top N</span>
          <select v-model.number="filters.top_n">
            <option :value="3">3</option>
            <option :value="5">5</option>
            <option :value="10">10</option>
          </select>
        </label>
        <label>
          <span>趋势粒度</span>
          <select v-model="filters.granularity">
            <option value="day">日</option>
            <option value="week">周</option>
          </select>
        </label>
        <div class="filter-actions">
          <button class="secondary-btn" @click="applyFilters">筛选</button>
          <button class="secondary-btn" @click="resetFilters">重置</button>
        </div>
      </div>
    </section>

    <div class="stats-grid">
      <article class="stat-card">
        <span>总执行数</span>
        <strong>{{ summary.total_count }}</strong>
      </article>
      <article class="stat-card accent">
        <span>通过率</span>
        <strong>{{ asPercent(summary.pass_rate) }}</strong>
        <small>success / completed</small>
      </article>
      <article class="stat-card soft">
        <span>失败率</span>
        <strong>{{ asPercent(summary.fail_rate) }}</strong>
        <small>(failed + error) / completed</small>
      </article>
      <article class="stat-card">
        <span>进行中</span>
        <strong>{{ summary.running_count }}</strong>
      </article>
    </div>

    <section class="panel-card">
      <div class="panel-head">
        <h3>状态分布</h3>
      </div>
      <div class="status-grid">
        <article class="mini">
          <span>completed</span>
          <strong>{{ summary.completed_count }}</strong>
        </article>
        <article class="mini">
          <span>success</span>
          <strong>{{ summary.success_count }}</strong>
        </article>
        <article class="mini">
          <span>failed</span>
          <strong>{{ summary.failed_count }}</strong>
        </article>
        <article class="mini">
          <span>error</span>
          <strong>{{ summary.error_count }}</strong>
        </article>
      </div>
    </section>

    <section class="panel-card">
      <div class="panel-head">
        <h3>Top 失败项</h3>
      </div>
      <div v-if="loading" class="state-block">正在加载报告...</div>
      <div v-else-if="summary.top_failures.length === 0" class="state-block">暂无失败项</div>
      <div v-else class="table-wrap">
        <table class="report-table">
          <thead>
            <tr>
              <th>用例</th>
              <th>类型</th>
              <th>分类</th>
              <th>次数</th>
              <th>最后错误</th>
              <th>最后出现</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in summary.top_failures" :key="`${item.run_type}-${item.case_id}-${item.failure_category}`">
              <td>
                <div class="case-cell">
                  <strong>{{ item.case_name }}</strong>
                  <small>#{{ item.case_id }}</small>
                </div>
              </td>
              <td><span class="type-pill" :class="item.run_type">{{ item.run_type }}</span></td>
              <td><span class="cat-pill">{{ item.failure_category }}</span></td>
              <td>{{ item.count }}</td>
              <td class="error-cell">{{ item.last_error_message || '--' }}</td>
              <td>{{ formatDate(item.last_seen_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel-card">
      <div class="panel-head">
        <h3>失败治理视图</h3>
      </div>
      <div class="governance-filter">
        <label>
          <span>失败分类</span>
          <select v-model="governanceFilters.failure_category" @change="fetchFailuresOnly">
            <option value="">全部</option>
            <option value="assertion_failure">assertion_failure</option>
            <option value="timeout">timeout</option>
            <option value="network_error">network_error</option>
            <option value="execution_error">execution_error</option>
            <option value="test_failure">test_failure</option>
          </select>
        </label>
      </div>
      <div v-if="loading" class="state-block">正在加载失败治理数据...</div>
      <div v-else-if="failures.items.length === 0" class="state-block">当前筛选条件暂无失败记录</div>
      <div v-else class="table-wrap">
        <table class="report-table">
          <thead>
            <tr>
              <th>类型</th>
              <th>Run ID</th>
              <th>用例</th>
              <th>分类</th>
              <th>错误信息</th>
              <th>创建时间</th>
              <th>追溯</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in failures.items" :key="`${item.run_type}-${item.run_id}`">
              <td><span class="type-pill" :class="item.run_type">{{ item.run_type }}</span></td>
              <td>#{{ item.run_id }}</td>
              <td>
                <div class="case-cell">
                  <strong>{{ item.case_name }}</strong>
                  <small>#{{ item.case_id }}</small>
                </div>
              </td>
              <td><span class="cat-pill">{{ item.failure_category }}</span></td>
              <td class="error-cell">{{ item.error_message || '--' }}</td>
              <td>{{ formatDate(item.created_at) }}</td>
              <td>
                <button class="table-link" @click="openFailureDetail(item)">查看详情</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel-card">
      <div class="panel-head">
        <h3>趋势概览（{{ filters.granularity === 'day' ? '按日' : '按周' }}）</h3>
      </div>
      <div v-if="loading" class="state-block">正在加载趋势...</div>
      <div v-else-if="trends.items.length === 0" class="state-block">当前筛选条件暂无趋势数据</div>
      <div v-else class="trend-list">
        <article v-for="item in trends.items" :key="`${trends.granularity}-${item.bucket_start}`" class="trend-row">
          <div class="trend-label">{{ item.bucket_label }}</div>
          <div class="trend-bar-track">
            <div class="trend-bar-fill" :style="{ width: `${trendBarWidth(item.total_count)}%` }"></div>
          </div>
          <div class="trend-meta">
            <strong>{{ item.total_count }}</strong>
            <span>通过率 {{ asPercent(item.pass_rate) }}</span>
            <span>失败率 {{ asPercent(item.fail_rate) }}</span>
          </div>
        </article>
      </div>
    </section>
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
const filters = ref({
  run_type: '',
  created_from_local: '',
  created_to_local: '',
  top_n: 5,
  granularity: 'day',
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
const governanceFilters = ref({
  failure_category: '',
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
  await fetchAll()
}

const trendMax = computed(() => {
  const values = trends.value.items.map(item => item.total_count)
  return values.length ? Math.max(...values) : 1
})

const trendBarWidth = (value) => {
  if (!trendMax.value) return 0
  return Math.max(6, (value / trendMax.value) * 100)
}

const fetchFailuresOnly = async () => {
  loading.value = true
  try {
    failures.value = await getProjectReportFailures(projectId, buildFailureParams())
  } catch (err) {
    alert(err.response?.data?.detail || '获取失败治理视图失败')
  } finally {
    loading.value = false
  }
}

const openFailureDetail = (item) => {
  if (item.run_type === 'web') {
    router.push(`/project/${projectId}/web-runs/${item.run_id}`)
    return
  }
  router.push(`/project/${projectId}/runs/${item.run_id}`)
}

onMounted(fetchAll)
</script>

<style scoped>
.report-page { display: flex; flex-direction: column; gap: 20px; }
.hero-card, .panel-card, .stat-card { background: rgba(255,255,255,0.84); border: 1px solid var(--border-color); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); }
.hero-card { padding: 24px 28px; display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.panel-card { padding: 22px; }
.back-link { color: var(--text-muted); text-decoration: none; }
.eyebrow { display: inline-block; margin-top: 10px; padding: 6px 10px; border-radius: 999px; background: var(--primary-soft); color: var(--primary-dark); font-size: 12px; font-weight: 700; }
.filter-bar { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; }
.filter-bar label { display: flex; flex-direction: column; gap: 6px; }
.filter-bar span { color: var(--text-muted); font-size: 12px; }
.filter-bar input, .filter-bar select { height: 38px; border: 1px solid var(--border-color); border-radius: 10px; padding: 0 10px; background: var(--bg-card-soft); color: var(--text-main); }
.filter-actions { display: flex; align-items: end; gap: 8px; }
.stats-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.stat-card { padding: 18px; border-radius: var(--radius-md); }
.stat-card span { color: var(--text-muted); font-size: 13px; }
.stat-card strong { display: block; margin-top: 10px; font-size: 30px; color: var(--text-strong); line-height: 1; }
.stat-card small { display: block; margin-top: 8px; color: var(--text-muted); }
.stat-card.accent { background: linear-gradient(135deg, rgba(18,179,165,0.14), rgba(255,255,255,0.88)); }
.stat-card.soft { background: linear-gradient(135deg, rgba(91,124,255,0.08), rgba(255,255,255,0.88)); }
.panel-head h3 { margin: 0 0 12px; color: var(--text-strong); }
.status-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.mini { border: 1px solid var(--border-color); border-radius: 14px; background: var(--bg-card-soft); padding: 14px; }
.mini span { color: var(--text-muted); font-size: 12px; text-transform: uppercase; }
.mini strong { display: block; margin-top: 8px; color: var(--text-strong); font-size: 24px; }
.table-wrap { overflow: auto; border: 1px solid var(--border-color); border-radius: 16px; }
.report-table { width: 100%; min-width: 900px; border-collapse: collapse; }
.report-table th, .report-table td { padding: 14px 16px; border-bottom: 1px solid #edf2f1; text-align: left; }
.report-table thead th { background: #f8fbfb; color: var(--text-muted); font-size: 13px; }
.case-cell { display: flex; flex-direction: column; gap: 4px; }
.case-cell small { color: var(--text-muted); }
.type-pill { display: inline-flex; padding: 6px 10px; border-radius: 999px; font-weight: 700; text-transform: capitalize; }
.type-pill.api { background: #e6f2ff; color: #2b6cb0; }
.type-pill.web { background: #efe8ff; color: #6b46c1; }
.cat-pill { display: inline-flex; padding: 6px 10px; border-radius: 999px; background: #ffe7e7; color: #d44a4a; font-weight: 700; }
.error-cell { max-width: 360px; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; color: var(--text-main); }
.governance-filter { margin-bottom: 12px; }
.governance-filter label { display: flex; flex-direction: column; gap: 6px; max-width: 260px; }
.governance-filter span { color: var(--text-muted); font-size: 12px; }
.governance-filter select { height: 38px; border: 1px solid var(--border-color); border-radius: 10px; padding: 0 10px; background: var(--bg-card-soft); color: var(--text-main); }
.secondary-btn { background: #f4f7f7; color: var(--text-main); border: 1px solid var(--border-color); border-radius: 12px; padding: 8px 10px; font-weight: 700; }
.table-link { border: 0; background: none; color: var(--primary-dark); font-weight: 700; cursor: pointer; }
.state-block { min-height: 220px; display: grid; place-items: center; border: 1px dashed var(--border-strong); border-radius: 16px; color: var(--text-muted); }
.trend-list { display: flex; flex-direction: column; gap: 10px; }
.trend-row { display: grid; grid-template-columns: 110px 1fr 260px; gap: 12px; align-items: center; }
.trend-label { color: var(--text-main); font-weight: 700; }
.trend-bar-track { height: 14px; border-radius: 999px; background: #eef5f4; overflow: hidden; border: 1px solid #dce8e5; }
.trend-bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #12b3a5, #0d9488); }
.trend-meta { display: flex; align-items: center; gap: 12px; color: var(--text-muted); font-size: 13px; }
.trend-meta strong { color: var(--text-strong); min-width: 24px; }
@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .status-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .filter-bar { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 900px) {
  .hero-card { flex-direction: column; align-items: flex-start; }
  .filter-bar { grid-template-columns: 1fr; }
  .filter-actions { align-items: stretch; }
  .stats-grid, .status-grid { grid-template-columns: 1fr; }
  .trend-row { grid-template-columns: 1fr; gap: 8px; }
  .trend-meta { flex-wrap: wrap; }
}
</style>
