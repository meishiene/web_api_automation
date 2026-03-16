<template>
  <section class="scheduling-page">
    <div class="hero-card">
      <div>
        <router-link :to="`/project/${projectId}`" class="back-link">返回项目</router-link>
        <span class="eyebrow">Stage 4</span>
        <h2>调度与 Worker 监控</h2>
        <p>查看调度入队任务、当前队列状态与 Worker 心跳。</p>
      </div>
      <button class="secondary-btn" @click="refreshAll" :disabled="loading">
        {{ loading ? '刷新中...' : '刷新数据' }}
      </button>
    </div>

    <div class="stats-grid">
      <article class="stat-card">
        <span>队列总数</span>
        <strong>{{ queueItems.length }}</strong>
      </article>
      <article class="stat-card accent">
        <span>排队中</span>
        <strong>{{ queuedCount }}</strong>
      </article>
      <article class="stat-card soft">
        <span>在线 Worker</span>
        <strong>{{ onlineWorkers }}</strong>
      </article>
    </div>

    <section class="panel-card">
      <div class="panel-head">
        <h3>队列任务</h3>
        <select v-model="statusFilter" @change="refreshQueueOnly">
          <option value="">全部状态</option>
          <option value="queued">queued</option>
          <option value="running">running</option>
          <option value="success">success</option>
          <option value="failed">failed</option>
          <option value="error">error</option>
        </select>
      </div>

      <div v-if="loading" class="state-block">正在加载队列...</div>
      <div v-else-if="queueItems.length === 0" class="state-block">暂无队列记录</div>
      <div v-else class="table-wrap">
        <table class="queue-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>状态</th>
              <th>类型</th>
              <th>目标</th>
              <th>优先级</th>
              <th>Worker</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in queueItems" :key="item.id">
              <td>#{{ item.id }}</td>
              <td><span class="status-pill" :class="item.status">{{ item.status }}</span></td>
              <td>{{ item.run_type }}</td>
              <td>{{ item.target_type }}#{{ item.target_id }}</td>
              <td>{{ item.priority }}</td>
              <td>{{ item.worker_id || '--' }}</td>
              <td>{{ formatDate(item.created_at) }}</td>
              <td><button class="table-link" @click="openQueueDetail(item.id)">详情</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel-card">
      <div class="panel-head">
        <h3>Worker 心跳</h3>
      </div>

      <div v-if="loading" class="state-block">正在加载 Worker...</div>
      <div v-else-if="workerItems.length === 0" class="state-block">暂无 Worker 心跳记录</div>
      <div v-else class="table-wrap">
        <table class="queue-table">
          <thead>
            <tr>
              <th>Worker ID</th>
              <th>状态</th>
              <th>类型</th>
              <th>当前任务</th>
              <th>最近心跳</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="worker in workerItems" :key="worker.id">
              <td>{{ worker.worker_id }}</td>
              <td><span class="status-pill" :class="worker.status">{{ worker.status }}</span></td>
              <td>{{ worker.run_type || '--' }}</td>
              <td>{{ worker.current_queue_item_id || '--' }}</td>
              <td>{{ formatDate(worker.last_heartbeat_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="detailOpen" class="modal-mask" @click.self="detailOpen = false">
      <div class="modal-card">
        <div class="panel-head">
          <h3>队列详情 #{{ detailItem?.id }}</h3>
          <button class="secondary-btn" @click="detailOpen = false">关闭</button>
        </div>
        <pre class="payload-pre">{{ detailText }}</pre>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getQueueItemDetail, getQueueItems, getWorkerHeartbeats } from '@/api/queueWorker'

const route = useRoute()
const projectId = Number(route.params.projectId)

const loading = ref(false)
const statusFilter = ref('')
const queueItems = ref([])
const workerItems = ref([])
const detailOpen = ref(false)
const detailItem = ref(null)

const queuedCount = computed(() => queueItems.value.filter(item => item.status === 'queued').length)
const onlineWorkers = computed(() => workerItems.value.filter(item => item.status === 'online').length)
const detailText = computed(() => {
  if (!detailItem.value) return ''
  return JSON.stringify(detailItem.value, null, 2)
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

const refreshQueueOnly = async () => {
  const params = {}
  if (statusFilter.value) params.status = statusFilter.value
  const response = await getQueueItems(projectId, params)
  queueItems.value = response.items || []
}

const refreshAll = async () => {
  loading.value = true
  try {
    await Promise.all([
      refreshQueueOnly(),
      getWorkerHeartbeats(projectId).then(response => {
        workerItems.value = response.items || []
      }),
    ])
  } catch (err) {
    alert(err.response?.data?.detail || '加载调度数据失败')
  } finally {
    loading.value = false
  }
}

const openQueueDetail = async (queueItemId) => {
  try {
    detailItem.value = await getQueueItemDetail(queueItemId)
    detailOpen.value = true
  } catch (err) {
    alert(err.response?.data?.detail || '加载队列详情失败')
  }
}

onMounted(refreshAll)
</script>

<style scoped>
.scheduling-page { display: flex; flex-direction: column; gap: 20px; }
.hero-card, .panel-card, .stat-card, .modal-card { background: rgba(255, 255, 255, 0.84); border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); border-radius: var(--radius-lg); }
.hero-card { padding: 24px 28px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.back-link { display: inline-block; margin-bottom: 10px; color: var(--text-muted); text-decoration: none; }
.eyebrow { display: inline-block; padding: 6px 10px; border-radius: 999px; background: var(--primary-soft); color: var(--primary-dark); font-size: 12px; font-weight: 700; }
.stats-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.stat-card { padding: 20px; border-radius: var(--radius-md); }
.stat-card span { color: var(--text-muted); font-size: 13px; }
.stat-card strong { display: block; margin-top: 10px; font-size: 34px; color: var(--text-strong); }
.stat-card.accent { background: linear-gradient(135deg, rgba(18, 179, 165, 0.14), rgba(255, 255, 255, 0.88)); }
.stat-card.soft { background: linear-gradient(135deg, rgba(91, 124, 255, 0.08), rgba(255, 255, 255, 0.88)); }
.panel-card { padding: 22px; }
.panel-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 14px; }
.panel-head h3 { margin: 0; color: var(--text-strong); }
.table-wrap { overflow: auto; border: 1px solid var(--border-color); border-radius: 18px; background: #fff; }
.queue-table { width: 100%; border-collapse: collapse; min-width: 820px; }
.queue-table th, .queue-table td { padding: 12px 14px; border-bottom: 1px solid #edf2f1; text-align: left; }
.queue-table th { background: #f8fbfb; color: var(--text-muted); font-size: 13px; }
.status-pill { display: inline-flex; border-radius: 999px; padding: 6px 10px; text-transform: capitalize; font-weight: 700; }
.status-pill.queued { background: #eef2ff; color: #4c63d2; }
.status-pill.running { background: #e6f2ff; color: #2b6cb0; }
.status-pill.success, .status-pill.online { background: #e4fbf3; color: #0f8f6b; }
.status-pill.failed, .status-pill.error, .status-pill.offline { background: #ffe7e7; color: #d44a4a; }
.status-pill.busy { background: #fff3df; color: #b7791f; }
.state-block { min-height: 120px; display: grid; place-items: center; color: var(--text-muted); border: 1px dashed var(--border-strong); border-radius: 16px; }
.secondary-btn { background: #f4f7f7; color: var(--text-main); border: 1px solid var(--border-color); border-radius: 12px; padding: 8px 12px; font-weight: 700; }
.table-link { border: 0; background: none; color: var(--primary-dark); font-weight: 700; cursor: pointer; }
.modal-mask { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.36); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 999; }
.modal-card { width: min(760px, 100%); padding: 18px; background: #fff; }
.payload-pre { margin: 0; background: #f8fbfb; border-radius: 14px; padding: 14px; max-height: 60vh; overflow: auto; }
@media (max-width: 980px) {
  .stats-grid { grid-template-columns: 1fr; }
  .hero-card { flex-direction: column; align-items: flex-start; }
}
</style>
