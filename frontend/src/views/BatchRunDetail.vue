<template>
  <section class="detail-page">
    <div class="hero-card">
      <div>
        <router-link :to="`/project/${projectId}/batches`" class="back-link">← 返回批次列表</router-link>
        <span class="eyebrow">Batch #{{ batchId }}</span>
        <h2>批次详情</h2>
        <p v-if="detail">状态：<strong>{{ detail.status }}</strong>，共 {{ detail.total_cases }} 条。</p>
      </div>
    </div>

    <section class="panel-card">
      <div v-if="loading" class="state-block"><p>正在加载批次详情...</p></div>
      <div v-else-if="!detail" class="state-block"><p>批次详情不存在或无权限访问。</p></div>
      <div v-else class="table-wrap">
        <table class="items-table">
          <thead>
            <tr>
              <th>顺序</th>
              <th>用例</th>
              <th>方法</th>
              <th>状态</th>
              <th>响应状态</th>
              <th>耗时(ms)</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in detail.items" :key="item.id">
              <td>{{ item.order_index }}</td>
              <td>
                <div class="case-cell">
                  <strong>{{ item.test_case_name }}</strong>
                  <small>{{ item.test_case_url }}</small>
                </div>
              </td>
              <td>{{ item.test_case_method }}</td>
              <td><span class="status-pill" :class="item.status">{{ item.status }}</span></td>
              <td>{{ item.actual_status ?? '--' }}</td>
              <td>{{ item.duration_ms ?? '--' }}</td>
              <td>
                <router-link
                  v-if="item.test_run_id"
                  class="table-link"
                  :to="`/project/${projectId}/runs/${item.test_run_id}`"
                >执行详情</router-link>
                <span v-else>--</span>
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
import { getBatchRunDetail } from '@/api/testRuns'

const route = useRoute()
const projectId = Number(route.params.projectId)
const batchId = Number(route.params.batchId)

const loading = ref(false)
const detail = ref(null)

const fetchDetail = async () => {
  loading.value = true
  try {
    detail.value = await getBatchRunDetail(batchId)
  } catch {
    detail.value = null
    alert('获取批次详情失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchDetail)
</script>

<style scoped>
.detail-page { display:flex; flex-direction:column; gap:20px; }
.hero-card, .panel-card { background: rgba(255,255,255,0.84); border:1px solid var(--border-color); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); }
.hero-card { padding:24px 28px; }
.panel-card { padding:22px; }
.back-link { color: var(--text-muted); text-decoration:none; }
.eyebrow { display:inline-block; margin-top:10px; padding:6px 10px; border-radius:999px; background:var(--primary-soft); color:var(--primary-dark); font-size:12px; font-weight:700; }
.table-wrap { overflow:auto; border:1px solid var(--border-color); border-radius: 18px; }
.items-table { width:100%; min-width: 980px; border-collapse:collapse; }
.items-table th, .items-table td { padding: 14px 16px; border-bottom:1px solid #edf2f1; text-align:left; }
.items-table thead th { background:#f8fbfb; color:var(--text-muted); font-size:13px; }
.case-cell { display:flex; flex-direction:column; gap:4px; }
.case-cell small { color: var(--text-muted); }
.status-pill { display:inline-flex; padding:6px 10px; border-radius:999px; font-weight:700; text-transform:capitalize; }
.status-pill.success { background:#e4fbf3; color:#0f8f6b; }
.status-pill.failed, .status-pill.error { background:#ffe7e7; color:#d44a4a; }
.table-link { color: var(--primary-dark); text-decoration:none; font-weight:700; }
.state-block { min-height:220px; display:grid; place-items:center; border:1px dashed var(--border-strong); border-radius:16px; color:var(--text-muted); }
</style>
