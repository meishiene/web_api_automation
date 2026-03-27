<template>
  <section class="ops-page">
    <div class="hero-card">
      <div>
        <span class="eyebrow">Stage 7</span>
        <h2>运营总览</h2>
        <p>跨项目观察失败积压、死信积压与重试趋势。</p>
      </div>
      <div class="hero-actions">
        <label>
          <span>趋势窗口</span>
          <select v-model.number="days" @change="refreshAll">
            <option :value="7">7 天</option>
            <option :value="14">14 天</option>
            <option :value="30">30 天</option>
          </select>
        </label>
        <button class="secondary-btn" @click="refreshAll" :disabled="loading">
          {{ loading ? '刷新中...' : '刷新' }}
        </button>
      </div>
    </div>

    <div v-if="errorText" class="error-banner">{{ errorText }}</div>
    <div v-if="overview?.guardrails?.degraded" class="warn-banner">
      当前结果已降级输出：{{ guardrailText }}
    </div>
    <div v-if="overview?.guardrails?.alerts?.length" class="alert-stack">
      <article
        v-for="alert in overview.guardrails.alerts"
        :key="alert.code"
        class="alert-card"
        :class="alert.level"
      >
        <strong>{{ alert.level === 'critical' ? 'Critical' : 'Warning' }}</strong>
        <span>{{ alert.message }}</span>
        <small>{{ alert.metric }} {{ alert.actual }} / {{ alert.threshold }}</small>
      </article>
    </div>

    <div class="stats-grid" v-if="overview">
      <article class="stat-card">
        <span>覆盖项目</span>
        <strong>{{ overview.project_count }}</strong>
      </article>
      <article class="stat-card accent">
        <span>失败积压</span>
        <strong>{{ overview.failed_backlog }}</strong>
      </article>
      <article class="stat-card warn">
        <span>死信积压</span>
        <strong>{{ overview.dead_letter_backlog }}</strong>
      </article>
      <article class="stat-card soft">
        <span>重试积压</span>
        <strong>{{ overview.retry_backlog }}</strong>
      </article>
    </div>

    <section class="panel-card" v-if="overview">
      <div class="panel-head">
        <h3>重试趋势</h3>
      </div>
      <div v-if="overview.retry_trend.length === 0" class="state-block">暂无趋势数据</div>
      <div v-else class="trend-list">
        <article v-for="item in overview.retry_trend" :key="item.bucket_start" class="trend-row">
          <div class="trend-label">{{ item.bucket_label }}</div>
          <div class="trend-bar-track">
            <div class="trend-bar-fill" :style="{ width: `${trendBarWidth(item.total_retries)}%` }"></div>
          </div>
          <div class="trend-meta">
            <strong>{{ item.total_retries }}</strong>
            <span>events {{ item.retry_events }}</span>
            <span>deliveries {{ item.retry_deliveries }}</span>
          </div>
        </article>
      </div>
    </section>

    <section class="panel-card" v-if="overview">
      <div class="panel-head">
        <h3>项目风险信号</h3>
      </div>
      <div v-if="overview.project_signals.length === 0" class="state-block">当前账号暂无可见项目</div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>项目</th>
              <th>失败积压</th>
              <th>死信积压</th>
              <th>重试积压</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in overview.project_signals" :key="item.project_id">
              <td>
                <router-link :to="`/project/${item.project_id}`" class="project-link">{{ item.project_name }}</router-link>
              </td>
              <td>{{ item.failed_backlog }}</td>
              <td>{{ item.dead_letter_backlog }}</td>
              <td>{{ item.retry_backlog }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getOperationsOverview } from '@/api/reporting'

const loading = ref(false)
const errorText = ref('')
const days = ref(7)
const overview = ref(null)

const trendMax = computed(() => {
  const items = overview.value?.retry_trend || []
  return items.length ? Math.max(...items.map(item => item.total_retries)) : 1
})

const trendBarWidth = (value) => {
  if (!trendMax.value) return 0
  return Math.max(6, (value / trendMax.value) * 100)
}

const guardrailText = computed(() => {
  const reasons = overview.value?.guardrails?.degradation_reasons || []
  if (!reasons.length) return ''
  if (reasons.includes('project_signals_truncated')) {
    const returned = overview.value?.guardrails?.project_signal_returned || 0
    const limit = overview.value?.guardrails?.project_signal_limit || 0
    return `项目风险信号仅展示 Top ${returned} / ${limit}`
  }
  return reasons.join(', ')
})

const refreshAll = async () => {
  loading.value = true
  errorText.value = ''
  try {
    overview.value = await getOperationsOverview({ days: days.value })
  } catch (err) {
    errorText.value = err.response?.data?.error?.message || '加载运营总览失败'
  } finally {
    loading.value = false
  }
}

onMounted(refreshAll)
</script>

<style scoped>
.ops-page { display: flex; flex-direction: column; gap: 20px; }
.hero-card, .panel-card, .stat-card { background: rgba(255,255,255,0.84); border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); border-radius: var(--radius-lg); }
.hero-card { padding: 24px 28px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.hero-actions { display: flex; align-items: end; gap: 10px; }
.hero-actions label { display: flex; flex-direction: column; gap: 6px; color: var(--text-muted); font-size: 12px; }
.hero-actions select { height: 38px; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-card-soft); padding: 0 10px; }
.eyebrow { display: inline-block; padding: 6px 10px; border-radius: 999px; background: var(--primary-soft); color: var(--primary-dark); font-size: 12px; font-weight: 700; }
.stats-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.stat-card { padding: 18px; border-radius: var(--radius-md); }
.stat-card span { color: var(--text-muted); font-size: 13px; }
.stat-card strong { display: block; margin-top: 10px; font-size: 32px; color: var(--text-strong); }
.stat-card.accent { background: linear-gradient(135deg, rgba(18,179,165,0.14), rgba(255,255,255,0.88)); }
.stat-card.soft { background: linear-gradient(135deg, rgba(91,124,255,0.08), rgba(255,255,255,0.88)); }
.stat-card.warn { background: linear-gradient(135deg, rgba(255,185,77,0.20), rgba(255,255,255,0.88)); }
.panel-card { padding: 22px; }
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.table-wrap { overflow: auto; border: 1px solid var(--border-color); border-radius: 16px; background: #fff; }
.data-table { width: 100%; border-collapse: collapse; min-width: 600px; }
.data-table th, .data-table td { padding: 12px 14px; border-bottom: 1px solid #edf2f1; text-align: left; }
.data-table th { background: #f8fbfb; color: var(--text-muted); font-size: 13px; }
.project-link { color: var(--primary-dark); text-decoration: none; font-weight: 700; }
.project-link:hover { text-decoration: underline; }
.trend-list { display: flex; flex-direction: column; gap: 10px; }
.trend-row { display: grid; grid-template-columns: 110px 1fr 260px; gap: 12px; align-items: center; }
.trend-label { color: var(--text-main); font-weight: 700; }
.trend-bar-track { height: 14px; border-radius: 999px; background: #eef5f4; overflow: hidden; border: 1px solid #dce8e5; }
.trend-bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #12b3a5, #0d9488); }
.trend-meta { display: flex; align-items: center; gap: 12px; color: var(--text-muted); font-size: 13px; }
.trend-meta strong { color: var(--text-strong); min-width: 24px; }
.secondary-btn { background: #f4f7f7; color: var(--text-main); border: 1px solid var(--border-color); border-radius: 12px; padding: 8px 12px; font-weight: 700; }
.state-block { min-height: 120px; display: grid; place-items: center; color: var(--text-muted); border: 1px dashed var(--border-strong); border-radius: 16px; }
.error-banner { background: #ffe7e7; color: #d44a4a; border: 1px solid #f4b1b1; border-radius: 12px; padding: 10px 12px; }
.warn-banner { background: #fff3df; color: #8a5a00; border: 1px solid #f2cf8a; border-radius: 12px; padding: 10px 12px; }
.alert-stack { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.alert-card { border-radius: 16px; padding: 14px; border: 1px solid var(--border-color); background: #fff; display: flex; flex-direction: column; gap: 6px; }
.alert-card strong { color: var(--text-strong); }
.alert-card small { color: var(--text-muted); }
.alert-card.warning { background: linear-gradient(135deg, rgba(255, 243, 223, 0.9), #fff); border-color: #f2cf8a; }
.alert-card.critical { background: linear-gradient(135deg, rgba(255, 231, 231, 0.92), #fff); border-color: #f4b1b1; }
@media (max-width: 980px) {
  .stats-grid { grid-template-columns: 1fr; }
  .hero-card { flex-direction: column; align-items: flex-start; }
  .trend-row { grid-template-columns: 1fr; gap: 8px; }
  .trend-meta { flex-wrap: wrap; }
}
</style>
