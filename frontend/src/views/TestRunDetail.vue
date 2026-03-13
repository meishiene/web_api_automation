<template>
  <section class="run-page">
    <div class="hero-card">
      <div>
        <router-link :to="`/project/${projectId}/batches`" class="back-link">← 返回批次列表</router-link>
        <span class="eyebrow">Run #{{ runId }}</span>
        <h2>执行详情</h2>
        <p v-if="detail">{{ detail.test_case_name }}（{{ detail.test_case_method }}）</p>
      </div>
    </div>

    <section class="panel-card">
      <div v-if="loading" class="state-block"><p>正在加载执行详情...</p></div>
      <div v-else-if="!detail" class="state-block"><p>执行详情不存在或无权限访问。</p></div>
      <div v-else class="content-grid">
        <article class="info-card">
          <h3>执行摘要</h3>
          <p><strong>状态：</strong>{{ detail.status }}</p>
          <p><strong>响应状态：</strong>{{ detail.actual_status ?? '--' }}</p>
          <p><strong>耗时：</strong>{{ detail.duration_ms ?? '--' }} ms</p>
          <p><strong>期望状态：</strong>{{ detail.test_case_expected_status }}</p>
          <p><strong>URL：</strong>{{ detail.test_case_url }}</p>
        </article>

        <article class="info-card full">
          <h3>响应体</h3>
          <pre>{{ formatJson(detail.actual_body) || '无响应体' }}</pre>
        </article>

        <article v-if="detail.error_message" class="info-card full">
          <h3>错误信息</h3>
          <pre class="error-pre">{{ detail.error_message }}</pre>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getTestRunDetail } from '@/api/testRuns'

const route = useRoute()
const projectId = Number(route.params.projectId)
const runId = Number(route.params.runId)

const loading = ref(false)
const detail = ref(null)

const formatJson = (data) => {
  if (!data) return ''
  if (typeof data === 'string') {
    try {
      return JSON.stringify(JSON.parse(data), null, 2)
    } catch {
      return data
    }
  }
  return JSON.stringify(data, null, 2)
}

const fetchDetail = async () => {
  loading.value = true
  try {
    detail.value = await getTestRunDetail(runId)
  } catch {
    detail.value = null
    alert('获取执行详情失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchDetail)
</script>

<style scoped>
.run-page { display:flex; flex-direction:column; gap:20px; }
.hero-card, .panel-card, .info-card { background: rgba(255,255,255,0.84); border:1px solid var(--border-color); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); }
.hero-card { padding:24px 28px; }
.panel-card { padding:22px; }
.back-link { color: var(--text-muted); text-decoration:none; }
.eyebrow { display:inline-block; margin-top:10px; padding:6px 10px; border-radius:999px; background:var(--primary-soft); color:var(--primary-dark); font-size:12px; font-weight:700; }
.content-grid { display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 14px; }
.info-card { padding: 16px; }
.info-card h3 { margin: 0 0 10px; }
.info-card p { margin: 8px 0; }
.info-card.full { grid-column: 1 / -1; }
.info-card pre { margin:0; white-space:pre-wrap; word-break:break-word; background:#f8fbfb; border-radius:14px; padding:14px; }
.error-pre { color:#b42318; }
.state-block { min-height:220px; display:grid; place-items:center; border:1px dashed var(--border-strong); border-radius:16px; color:var(--text-muted); }
@media (max-width: 900px) { .content-grid { grid-template-columns: 1fr; } }
</style>
