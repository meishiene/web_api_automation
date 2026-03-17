<template>
  <section class="governance-page">
    <div class="hero-card">
      <div>
        <router-link :to="`/project/${projectId}`" class="back-link">返回项目</router-link>
        <span class="eyebrow">Stage 6</span>
        <h2>集成治理看板</h2>
        <p>查看集成健康、失败积压，并对失败事件与死信执行批量重试。</p>
      </div>
      <div class="hero-actions">
        <button class="secondary-btn" @click="refreshAll" :disabled="loading">{{ loading ? '刷新中...' : '刷新' }}</button>
        <button class="primary-btn" @click="retryBacklog" :disabled="loading || retrying">{{ retrying ? '重试中...' : '重试失败积压' }}</button>
      </div>
    </div>

    <div v-if="errorText" class="error-banner">{{ errorText }}</div>

    <div class="stats-grid" v-if="health">
      <article class="stat-card">
        <span>启用配置</span>
        <strong>{{ health.config_counts.enabled }}</strong>
      </article>
      <article class="stat-card accent">
        <span>事件重试积压</span>
        <strong>{{ health.retry_backlog.events }}</strong>
      </article>
      <article class="stat-card soft">
        <span>投递重试积压</span>
        <strong>{{ health.retry_backlog.deliveries }}</strong>
      </article>
      <article class="stat-card warn">
        <span>开放缺陷</span>
        <strong>{{ health.defect_open_count }}</strong>
      </article>
    </div>

    <section class="panel-card" v-if="health">
      <div class="panel-head">
        <h3>状态分布</h3>
      </div>
      <div class="status-grid">
        <div>
          <h4>事件状态</h4>
          <ul>
            <li v-for="(count, status) in health.event_status_counts" :key="`event-${status}`">{{ status }}: {{ count }}</li>
          </ul>
        </div>
        <div>
          <h4>投递状态</h4>
          <ul>
            <li v-for="(count, status) in health.delivery_status_counts" :key="`delivery-${status}`">{{ status }}: {{ count }}</li>
          </ul>
        </div>
      </div>
    </section>

    <section class="panel-card" v-if="health">
      <div class="panel-head">
        <h3>最近失败记录</h3>
      </div>
      <div v-if="health.recent_failures.length === 0" class="state-block">暂无失败积压</div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>来源</th>
              <th>ID</th>
              <th>状态</th>
              <th>错误</th>
              <th>更新时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in health.recent_failures" :key="`${item.source}-${item.record_id}`">
              <td>{{ item.source }}</td>
              <td>#{{ item.record_id }}</td>
              <td><span class="status-pill" :class="item.status">{{ item.status }}</span></td>
              <td>{{ item.message || '--' }}</td>
              <td>{{ formatDate(item.updated_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getIntegrationGovernanceHealth, retryIntegrationGovernanceBacklog } from '@/api/integrations'

const route = useRoute()
const projectId = Number(route.params.projectId)

const loading = ref(false)
const retrying = ref(false)
const health = ref(null)
const errorText = ref('')

const normalizeTimestamp = (value) => {
  if (!value) return 0
  const numeric = Number(value)
  return numeric > 1e12 ? numeric : numeric * 1000
}

const formatDate = (value) => {
  if (!value) return '--'
  return new Date(normalizeTimestamp(value)).toLocaleString('zh-CN')
}

const refreshAll = async () => {
  loading.value = true
  errorText.value = ''
  try {
    health.value = await getIntegrationGovernanceHealth(projectId)
  } catch (err) {
    errorText.value = err.response?.data?.error?.message || '加载治理数据失败'
  } finally {
    loading.value = false
  }
}

const retryBacklog = async () => {
  retrying.value = true
  errorText.value = ''
  try {
    await retryIntegrationGovernanceBacklog(projectId, { max_events: 20, max_deliveries: 20 })
    await refreshAll()
  } catch (err) {
    errorText.value = err.response?.data?.error?.message || '重试失败积压失败'
  } finally {
    retrying.value = false
  }
}

onMounted(refreshAll)
</script>

<style scoped>
.governance-page { display: flex; flex-direction: column; gap: 20px; }
.hero-card, .panel-card, .stat-card { background: rgba(255,255,255,0.84); border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); border-radius: var(--radius-lg); }
.hero-card { padding: 24px 28px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.hero-actions { display: flex; gap: 10px; }
.back-link { display: inline-block; margin-bottom: 10px; color: var(--text-muted); text-decoration: none; }
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
.status-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
.status-grid h4 { margin: 0 0 8px; }
.status-grid ul { margin: 0; padding-left: 18px; color: var(--text-main); }
.table-wrap { overflow: auto; border: 1px solid var(--border-color); border-radius: 16px; background: #fff; }
.data-table { width: 100%; border-collapse: collapse; min-width: 760px; }
.data-table th, .data-table td { padding: 12px 14px; border-bottom: 1px solid #edf2f1; text-align: left; }
.data-table th { background: #f8fbfb; color: var(--text-muted); font-size: 13px; }
.status-pill { display: inline-flex; border-radius: 999px; padding: 6px 10px; font-weight: 700; }
.status-pill.failed, .status-pill.dead_letter { background: #ffe7e7; color: #d44a4a; }
.status-pill.retry_pending { background: #fff3df; color: #b7791f; }
.status-pill.processed, .status-pill.sent { background: #e4fbf3; color: #0f8f6b; }
.state-block { min-height: 120px; display: grid; place-items: center; color: var(--text-muted); border: 1px dashed var(--border-strong); border-radius: 16px; }
.primary-btn { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: #fff; border: 0; border-radius: 12px; padding: 8px 12px; font-weight: 700; }
.secondary-btn { background: #f4f7f7; color: var(--text-main); border: 1px solid var(--border-color); border-radius: 12px; padding: 8px 12px; font-weight: 700; }
.error-banner { background: #ffe7e7; color: #d44a4a; border: 1px solid #f4b1b1; border-radius: 12px; padding: 10px 12px; }
@media (max-width: 980px) {
  .stats-grid { grid-template-columns: 1fr; }
  .status-grid { grid-template-columns: 1fr; }
  .hero-card { flex-direction: column; align-items: flex-start; }
}
</style>
