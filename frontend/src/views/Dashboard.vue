<template>
  <section class="dashboard-page">
    <div v-if="activeProject" class="page-caption">
      <div>
        <h2>{{ activeProject.name }}</h2>
        <p>{{ activeProject.description || '当前项目执行概览与最近测试动态' }}</p>
      </div>
      <div class="caption-actions">
        <button class="ghost-btn" @click="router.push('/projects')">项目管理</button>
        <button class="primary-btn" @click="router.push(`/project/${activeProject.id}`)">进入 API 测试</button>
      </div>
    </div>

    <div v-if="!projects.length && !loading" class="empty-card">
      <h3>还没有项目</h3>
      <p>先创建项目，再开始配置 API、UI、任务和报告。</p>
      <button class="primary-btn" @click="router.push('/projects')">去创建项目</button>
    </div>

    <template v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-head">
            <span class="stat-label">总执行次数</span>
            <span class="stat-icon">◈</span>
          </div>
          <div class="stat-value">{{ summary.total_count }}</div>
          <div class="stat-foot">当前项目最近统计窗口内的执行总量</div>
        </div>

        <div class="stat-card">
          <div class="stat-head">
            <span class="stat-label">成功次数</span>
            <span class="stat-icon success">●</span>
          </div>
          <div class="stat-value">{{ summary.success_count }}</div>
          <div class="stat-foot">通过率 {{ percent(summary.pass_rate) }}</div>
        </div>

        <div class="stat-card">
          <div class="stat-head">
            <span class="stat-label">失败次数</span>
            <span class="stat-icon danger">✕</span>
          </div>
          <div class="stat-value">{{ failedCount }}</div>
          <div class="stat-foot">失败 + 异常总计</div>
        </div>

        <div class="stat-card">
          <div class="stat-head">
            <span class="stat-label">运行中</span>
            <span class="stat-icon info">◔</span>
          </div>
          <div class="stat-value">{{ summary.running_count }}</div>
          <div class="stat-foot">当前仍在执行或排队中的记录</div>
        </div>
      </div>

      <div class="chart-grid">
        <section class="panel-card">
          <h3>执行趋势</h3>
          <div v-if="trendRows.length" class="line-chart-wrap">
            <svg viewBox="0 0 620 280" class="trend-svg" preserveAspectRatio="none">
              <g>
                <line v-for="tick in yTicks" :key="`y-${tick.value}`" x1="52" x2="590" :y1="tick.y" :y2="tick.y" class="grid-line" />
                <polyline :points="trendPolyline('total')" class="trend-line total" />
                <polyline :points="trendPolyline('pass')" class="trend-line pass" />
                <polyline :points="trendPolyline('fail')" class="trend-line fail" />
                <g v-for="point in trendPoints" :key="point.label">
                  <circle :cx="point.x" :cy="point.totalY" r="4" class="point total" />
                  <circle :cx="point.x" :cy="point.passY" r="4" class="point pass" />
                  <circle :cx="point.x" :cy="point.failY" r="4" class="point fail" />
                  <text :x="point.x" y="264" text-anchor="middle" class="axis-label">{{ point.label }}</text>
                </g>
              </g>
            </svg>
            <div class="chart-legend">
              <span><i class="dot total"></i>总数</span>
              <span><i class="dot pass"></i>通过</span>
              <span><i class="dot fail"></i>失败</span>
            </div>
          </div>
          <div v-else class="empty-chart">暂无趋势数据</div>
        </section>

        <section class="panel-card">
          <h3>执行结果分布</h3>
          <div class="donut-wrap">
            <div class="donut-chart" :style="{ background: donutBackground }">
              <div class="donut-core">
                <strong>{{ summary.total_count }}</strong>
                <span>总记录</span>
              </div>
            </div>
          </div>
          <div class="legend-row">
            <div class="legend-item"><span class="dot pass"></span>成功 {{ summary.success_count }}</div>
            <div class="legend-item"><span class="dot fail"></span>失败 {{ failedCount }}</div>
            <div class="legend-item"><span class="dot total"></span>运行中 {{ summary.running_count }}</div>
          </div>
        </section>
      </div>

      <section class="panel-card">
        <div class="panel-head">
          <h3>最近执行记录</h3>
          <div class="panel-actions">
            <button class="ghost-btn" @click="router.push(activeProject ? `/project/${activeProject.id}/reports` : '/projects')">查看报告</button>
            <button class="ghost-btn" @click="router.push(activeProject ? `/project/${activeProject.id}/executions` : '/projects')">执行中心</button>
          </div>
        </div>

        <div v-if="loading" class="state-block">正在加载执行记录...</div>
        <div v-else-if="recentRuns.length === 0" class="state-block">当前项目暂无执行记录</div>
        <div v-else class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>测试名称</th>
                <th>类型</th>
                <th>状态</th>
                <th>耗时</th>
                <th>执行时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recentRuns" :key="`${item.run_type}-${item.run_id}`">
                <td>#{{ item.run_id }}</td>
                <td class="name-cell">
                  <strong>{{ item.case_name }}</strong>
                  <small>#{{ item.case_id }}</small>
                </td>
                <td>
                  <span class="type-pill" :class="item.run_type">{{ item.run_type === 'api' ? 'API' : 'UI' }}</span>
                </td>
                <td>
                  <span class="status-pill" :class="item.status">{{ statusLabel(item.status) }}</span>
                </td>
                <td>{{ item.duration_ms ? `${item.duration_ms}ms` : '--' }}</td>
                <td>{{ formatDate(item.created_at) }}</td>
                <td>
                  <div class="link-group">
                    <button class="table-link" @click="openRunDetail(item)">详情</button>
                    <button class="table-link" @click="openRunDetail(item)">日志</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getProjects } from '@/api/projects'
import { getProjectReportSummary, getProjectReportTrends } from '@/api/reporting'
import { getUnifiedRuns } from '@/api/unifiedRuns'
import { getActiveProjectId, setActiveProjectId } from '@/utils/projectContext'

const router = useRouter()

const loading = ref(false)
const projects = ref([])
const activeProjectId = ref(getActiveProjectId())
const summary = ref({
  total_count: 0,
  success_count: 0,
  failed_count: 0,
  error_count: 0,
  running_count: 0,
  pass_rate: 0,
})
const trends = ref({ items: [] })
const recentRuns = ref([])

const activeProject = computed(() => projects.value.find((item) => item.id === activeProjectId.value) || null)
const failedCount = computed(() => summary.value.failed_count + summary.value.error_count)

const trendRows = computed(() => (trends.value.items || []).slice(-7))
const maxTrendValue = computed(() => {
  const values = trendRows.value.flatMap((item) => [item.total_count, item.success_count, item.failed_count + item.error_count])
  return values.length ? Math.max(...values, 1) : 1
})

const trendPoints = computed(() => {
  if (!trendRows.value.length) return []
  const startX = 78
  const endX = 564
  const width = endX - startX
  const bottomY = 228
  const topY = 36
  const height = bottomY - topY

  return trendRows.value.map((item, index) => {
    const x = trendRows.value.length === 1 ? startX + width / 2 : startX + (width / (trendRows.value.length - 1)) * index
    const calcY = (value) => bottomY - (value / maxTrendValue.value) * height
    return {
      label: item.bucket_label,
      x,
      totalY: calcY(item.total_count),
      passY: calcY(item.success_count),
      failY: calcY(item.failed_count + item.error_count),
    }
  })
})

const yTicks = computed(() => {
  const top = maxTrendValue.value
  return [0, 0.33, 0.66, 1].map((ratio) => ({
    value: Math.round(top * ratio),
    y: 228 - 192 * ratio,
  }))
})

const donutBackground = computed(() => {
  const total = summary.value.total_count || 1
  const successAngle = (summary.value.success_count / total) * 360
  const failAngle = ((failedCount.value) / total) * 360
  return `conic-gradient(#27ae60 0deg ${successAngle}deg, #e74c3c ${successAngle}deg ${successAngle + failAngle}deg, #3498db ${successAngle + failAngle}deg 360deg)`
})

const percent = (value) => `${((Number(value) || 0) * 100).toFixed(1)}%`

const normalizeTimestamp = (value) => {
  if (!value) return 0
  const numeric = Number(value)
  return numeric > 1e12 ? numeric : numeric * 1000
}

const formatDate = (value) => {
  if (!value) return '--'
  return new Date(normalizeTimestamp(value)).toLocaleString('zh-CN')
}

const statusLabel = (status) => {
  if (status === 'success') return '成功'
  if (status === 'failed') return '失败'
  if (status === 'error') return '异常'
  if (status === 'running') return '运行中'
  return status || '--'
}

const trendPolyline = (key) => trendPoints.value.map((point) => `${point.x},${point[`${key}Y`]}`).join(' ')

const openRunDetail = (item) => {
  if (!activeProjectId.value) return
  if (item.run_type === 'web') {
    router.push(`/project/${activeProjectId.value}/web-runs/${item.run_id}`)
    return
  }
  router.push(`/project/${activeProjectId.value}/runs/${item.run_id}`)
}

const fetchProjects = async () => {
  projects.value = await getProjects()
  if (!activeProjectId.value && projects.value.length) {
    activeProjectId.value = projects.value[0].id
    setActiveProjectId(activeProjectId.value)
  }
}

const fetchProjectOverview = async () => {
  if (!activeProjectId.value) return
  const [summaryResp, trendResp, runResp] = await Promise.all([
    getProjectReportSummary(activeProjectId.value),
    getProjectReportTrends(activeProjectId.value, { granularity: 'day' }),
    getUnifiedRuns(activeProjectId.value, { page: 1, page_size: 6 }),
  ])
  summary.value = summaryResp
  trends.value = trendResp
  recentRuns.value = runResp.items || []
}

const refreshAll = async () => {
  loading.value = true
  try {
    await fetchProjects()
    await fetchProjectOverview()
  } catch (err) {
    alert(err.response?.data?.detail || '加载仪表盘失败')
  } finally {
    loading.value = false
  }
}

watch(activeProjectId, async (value, oldValue) => {
  if (!value || value === oldValue) return
  setActiveProjectId(value)
  await refreshAll()
})

onMounted(refreshAll)
</script>

<style scoped>
.dashboard-page { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.page-caption,
.stat-card,
.panel-card,
.empty-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); box-shadow: var(--surface-shadow); }
.page-caption { padding: 20px 24px; display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.page-caption h2 { margin: 0 0 8px; font-size: 20px; font-weight: 500; color: var(--text-strong); }
.page-caption p { margin: 0; font-size: 13px; color: var(--text-muted); }
.caption-actions { display: flex; gap: 12px; }
.stats-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.stat-card { padding: 20px; }
.stat-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.stat-label { font-size: 14px; color: var(--text-main); }
.stat-icon { font-size: 16px; color: var(--primary); }
.stat-icon.success { color: var(--success); }
.stat-icon.danger { color: var(--danger); }
.stat-icon.info { color: var(--primary); }
.stat-value { font-size: 28px; line-height: 1; font-weight: 500; color: var(--text-strong); margin-bottom: 8px; }
.stat-foot { font-size: 12px; color: var(--text-muted); }
.chart-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; }
.panel-card { padding: 20px; }
.panel-card h3 { margin: 0 0 16px; font-size: 16px; font-weight: 500; color: var(--text-strong); }
.line-chart-wrap { min-height: 312px; display: flex; flex-direction: column; }
.trend-svg { width: 100%; height: 280px; }
.grid-line { stroke: var(--border-color); stroke-dasharray: 4 4; }
.trend-line { fill: none; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }
.trend-line.total { stroke: #3498db; }
.trend-line.pass { stroke: #27ae60; }
.trend-line.fail { stroke: #e74c3c; }
.point.total { fill: #3498db; }
.point.pass { fill: #27ae60; }
.point.fail { fill: #e74c3c; }
.axis-label { fill: var(--text-muted); font-size: 12px; }
.chart-legend,
.legend-row { display: flex; align-items: center; justify-content: center; gap: 20px; flex-wrap: wrap; }
.chart-legend span,
.legend-item { display: inline-flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-main); }
.dot { width: 10px; height: 10px; border-radius: 999px; display: inline-block; }
.dot.total { background: #3498db; }
.dot.pass { background: #27ae60; }
.dot.fail { background: #e74c3c; }
.donut-wrap { min-height: 280px; display: grid; place-items: center; }
.donut-chart {
  width: 210px;
  height: 210px;
  border-radius: 50%;
  display: grid;
  place-items: center;
}
.donut-core {
  width: 132px;
  height: 132px;
  border-radius: 50%;
  background: var(--bg-card);
  display: grid;
  place-items: center;
  text-align: center;
}
.donut-core strong { display: block; font-size: 30px; color: var(--text-strong); }
.donut-core span { font-size: 12px; color: var(--text-muted); }
.panel-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 14px; }
.panel-actions,
.caption-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table thead tr { background: var(--bg-muted); border-bottom: 1px solid var(--border-color); }
.data-table th { padding: 12px 16px; text-align: left; font-size: 13px; font-weight: 500; color: var(--text-main); }
.data-table td { padding: 14px 16px; border-bottom: 1px solid var(--border-color); font-size: 13px; color: var(--text-main); vertical-align: top; }
.name-cell { display: flex; flex-direction: column; gap: 4px; }
.name-cell strong { color: var(--text-strong); }
.name-cell small { color: var(--text-muted); }
.type-pill,
.status-pill { display: inline-flex; align-items: center; justify-content: center; padding: 4px 10px; border-radius: 999px; font-size: 12px; }
.type-pill.api { background: #e3f2fd; color: #3498db; }
.type-pill.web { background: #f0e6ff; color: #9b59b6; }
.status-pill.success { background: #e8f5e9; color: #27ae60; }
.status-pill.failed,
.status-pill.error { background: #ffebee; color: #e74c3c; }
.status-pill.running { background: #e3f2fd; color: #3498db; }
.link-group { display: flex; align-items: center; gap: 12px; }
.table-link { border: 0; background: transparent; color: var(--primary); font-size: 13px; padding: 0; }
.state-block,
.empty-chart,
.empty-card { min-height: 180px; display: grid; place-items: center; text-align: center; color: var(--text-muted); }
.empty-card { padding: 32px; }
.empty-card h3 { margin: 0 0 8px; color: var(--text-strong); }
.empty-card p { margin: 0 0 16px; }
.primary-btn,
.ghost-btn { min-height: 32px; padding: 0 14px; border-radius: var(--radius); font-size: 13px; }
.primary-btn { border: 1px solid var(--primary); background: var(--primary); color: #fff; }
.ghost-btn { border: 1px solid var(--border-color-strong); background: transparent; color: var(--text-main); }

@media (max-width: 1180px) {
  .stats-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .chart-grid { grid-template-columns: 1fr; }
}

@media (max-width: 860px) {
  .dashboard-page { padding: 16px; }
  .page-caption,
  .panel-head { flex-direction: column; align-items: flex-start; }
  .stats-grid { grid-template-columns: 1fr; }
}
</style>
