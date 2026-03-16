<template>
  <section class="runs-page">
    <div class="hero-card">
      <div>
        <router-link :to="`/project/${projectId}`" class="back-link">← 返回 API 用例页</router-link>
        <span class="eyebrow">Execution Center</span>
        <h2>统一执行结果</h2>
        <p>按统一字段聚合 API/Web 执行记录，支持筛选、分页与快速定位失败记录。</p>
      </div>
    </div>

    <section class="panel-card">
      <div class="panel-head">
        <h3>执行记录</h3>
      </div>

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
          <span>状态</span>
          <select v-model="filters.status">
            <option value="">全部</option>
            <option value="success">success</option>
            <option value="failed">failed</option>
            <option value="error">error</option>
            <option value="running">running</option>
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
          <span>每页</span>
          <select v-model.number="pageSize">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
        </label>

        <div class="filter-actions">
          <button class="secondary-btn" @click="applyFilters">筛选</button>
          <button class="secondary-btn" @click="showFailedOnly">仅看失败</button>
          <button class="secondary-btn" @click="resetFilters">重置</button>
        </div>
      </div>

      <div class="quick-bar">
        <span>总数：{{ total }}，失败/异常：{{ failedCount }}</span>
        <button class="table-link" @click="openFirstFailed" :disabled="!firstFailedItem">快速定位首条失败</button>
      </div>

      <div v-if="loading" class="state-block"><p>正在加载执行记录...</p></div>
      <div v-else-if="runs.length === 0" class="state-block"><p>暂无执行记录。</p></div>
      <div v-else class="table-wrap">
        <table class="runs-table">
          <thead>
            <tr>
              <th>类型</th>
              <th>Run ID</th>
              <th>用例</th>
              <th>状态</th>
              <th>耗时(ms)</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in runs" :key="`${item.run_type}-${item.run_id}`">
              <td><span class="type-pill" :class="item.run_type">{{ item.run_type }}</span></td>
              <td>#{{ item.run_id }}</td>
              <td>
                <div class="case-cell">
                  <strong>{{ item.case_name }}</strong>
                  <small>#{{ item.case_id }}</small>
                </div>
              </td>
              <td><span class="status-pill" :class="item.status">{{ item.status }}</span></td>
              <td>{{ item.duration_ms ?? '--' }}</td>
              <td>{{ formatDate(item.created_at) }}</td>
              <td>
                <button class="table-link" @click="openDetail(item)">查看详情</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination" v-if="total > 0">
        <button class="secondary-btn" @click="prevPage" :disabled="page <= 1">上一页</button>
        <span>第 {{ page }} / {{ totalPages }} 页</span>
        <button class="secondary-btn" @click="nextPage" :disabled="page >= totalPages">下一页</button>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUnifiedRuns } from '@/api/unifiedRuns'

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

const failedCount = computed(() =>
  runs.value.filter(item => item.status === 'failed' || item.status === 'error').length
)
const firstFailedItem = computed(() =>
  runs.value.find(item => item.status === 'failed' || item.status === 'error') || null
)
const totalPages = computed(() => {
  if (!total.value) return 1
  return Math.ceil(total.value / pageSize.value)
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
.runs-page { display: flex; flex-direction: column; gap: 20px; }
.hero-card, .panel-card { background: rgba(255,255,255,0.84); border: 1px solid var(--border-color); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); }
.hero-card { padding: 24px 28px; }
.panel-card { padding: 22px; }
.back-link { color: var(--text-muted); text-decoration: none; }
.eyebrow { display: inline-block; margin-top: 10px; padding: 6px 10px; border-radius: 999px; background: var(--primary-soft); color: var(--primary-dark); font-size: 12px; font-weight: 700; }
.panel-head h3 { margin: 0 0 16px; color: var(--text-strong); }
.filter-bar { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; margin-bottom: 12px; }
.filter-bar label { display: flex; flex-direction: column; gap: 6px; }
.filter-bar span { color: var(--text-muted); font-size: 12px; }
.filter-bar input, .filter-bar select { height: 38px; border: 1px solid var(--border-color); border-radius: 10px; padding: 0 10px; background: var(--bg-card-soft); color: var(--text-main); }
.filter-actions { display: flex; align-items: end; gap: 8px; }
.quick-bar { display: flex; align-items: center; justify-content: space-between; margin: 8px 0 14px; color: var(--text-main); }
.table-wrap { overflow: auto; border: 1px solid var(--border-color); border-radius: 18px; }
.runs-table { width: 100%; min-width: 860px; border-collapse: collapse; }
.runs-table th, .runs-table td { padding: 14px 16px; border-bottom: 1px solid #edf2f1; text-align: left; }
.runs-table thead th { background: #f8fbfb; color: var(--text-muted); font-size: 13px; }
.case-cell { display: flex; flex-direction: column; gap: 4px; }
.case-cell small { color: var(--text-muted); }
.status-pill, .type-pill { display: inline-flex; padding: 6px 10px; border-radius: 999px; font-weight: 700; text-transform: capitalize; }
.status-pill.success { background: #e4fbf3; color: #0f8f6b; }
.status-pill.failed, .status-pill.error { background: #ffe7e7; color: #d44a4a; }
.status-pill.running { background: #eef2ff; color: #4c63d2; }
.type-pill.api { background: #e6f2ff; color: #2b6cb0; }
.type-pill.web { background: #efe8ff; color: #6b46c1; }
.table-link { border: 0; background: none; color: var(--primary-dark); font-weight: 700; cursor: pointer; }
.secondary-btn { background: #f4f7f7; color: var(--text-main); border: 1px solid var(--border-color); border-radius: 12px; padding: 8px 10px; font-weight: 700; }
.pagination { margin-top: 14px; display: flex; align-items: center; justify-content: flex-end; gap: 10px; }
.state-block { min-height: 220px; display: grid; place-items: center; border: 1px dashed var(--border-strong); border-radius: 16px; color: var(--text-muted); }
@media (max-width: 1080px) {
  .filter-bar { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 900px) {
  .filter-bar { grid-template-columns: 1fr; }
  .filter-actions { align-items: stretch; }
  .quick-bar { flex-direction: column; align-items: flex-start; gap: 8px; }
}
</style>
