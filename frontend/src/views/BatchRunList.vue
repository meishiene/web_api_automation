<template>
  <section class="batches-page">
    <div class="hero-card">
      <div>
        <router-link :to="`/project/${projectId}`" class="back-link">← 返回测试用例</router-link>
        <span class="eyebrow">Batch Runs</span>
        <h2>批次结果</h2>
        <p>查看项目下套件批量执行历史，快速定位失败批次。</p>
      </div>
    </div>

    <section class="panel-card">
      <div class="panel-head">
        <h3>批次列表</h3>
      </div>

      <div v-if="loading" class="state-block">
        <p>正在加载批次数据...</p>
      </div>

      <div v-else-if="batches.length === 0" class="state-block">
        <p>暂无批次执行记录，先在测试用例页触发套件执行。</p>
      </div>

      <div v-else class="table-wrap">
        <table class="batches-table">
          <thead>
            <tr>
              <th>批次ID</th>
              <th>状态</th>
              <th>总数</th>
              <th>成功/失败/错误</th>
              <th>开始时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="batch in batches" :key="batch.id">
              <td>#{{ batch.id }}</td>
              <td><span class="status-pill" :class="batch.status">{{ batch.status }}</span></td>
              <td>{{ batch.total_cases }}</td>
              <td>{{ batch.passed_cases }} / {{ batch.failed_cases }} / {{ batch.error_cases }}</td>
              <td>{{ formatDate(batch.started_at || batch.created_at) }}</td>
              <td>
                <router-link class="table-link" :to="`/project/${projectId}/batches/${batch.id}`">查看详情</router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getBatchRuns } from '@/api/testRuns'

const route = useRoute()
const projectId = Number(route.params.projectId)

const loading = ref(false)
const batches = ref([])

const normalizeTimestamp = (value) => {
  if (!value) return 0
  const numeric = Number(value)
  return numeric > 1e12 ? numeric : numeric * 1000
}

const formatDate = (value) => {
  if (!value) return '--'
  return new Date(normalizeTimestamp(value)).toLocaleString('zh-CN')
}

const fetchBatches = async () => {
  loading.value = true
  try {
    batches.value = await getBatchRuns(projectId)
  } catch {
    alert('获取批次列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchBatches)
</script>

<style scoped>
.batches-page { display: flex; flex-direction: column; gap: 20px; }
.hero-card, .panel-card { background: rgba(255,255,255,0.84); border: 1px solid var(--border-color); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); }
.hero-card { padding: 24px 28px; }
.panel-card { padding: 22px; }
.back-link { color: var(--text-muted); text-decoration: none; }
.eyebrow { display:inline-block; margin-top:10px; padding:6px 10px; border-radius:999px; background:var(--primary-soft); color:var(--primary-dark); font-size:12px; font-weight:700; }
.panel-head h3 { margin: 0 0 16px; }
.table-wrap { overflow:auto; border:1px solid var(--border-color); border-radius: 18px; }
.batches-table { width:100%; border-collapse: collapse; min-width: 780px; }
.batches-table th, .batches-table td { padding: 14px 16px; border-bottom: 1px solid #edf2f1; text-align: left; }
.batches-table thead th { background: #f8fbfb; color: var(--text-muted); font-size: 13px; }
.status-pill { display:inline-flex; padding: 6px 10px; border-radius: 999px; font-weight: 700; text-transform: capitalize; }
.status-pill.success { background:#e4fbf3; color:#0f8f6b; }
.status-pill.failed, .status-pill.error { background:#ffe7e7; color:#d44a4a; }
.status-pill.running { background:#eef2ff; color:#4c63d2; }
.table-link { color: var(--primary-dark); font-weight: 700; text-decoration: none; }
.state-block { min-height: 220px; display:grid; place-items:center; border:1px dashed var(--border-strong); border-radius:16px; color:var(--text-muted); }
</style>
