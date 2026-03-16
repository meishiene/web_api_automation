<template>
  <section class="env-page">
    <div class="hero-card">
      <div>
        <router-link :to="`/project/${projectId}`" class="back-link">← 返回用例列表</router-link>
        <span class="eyebrow">Project {{ projectId }}</span>
        <h2>环境与变量治理</h2>
      </div>
    </div>

    <section class="panel-card">
      <div class="panel-head">
        <h3>环境</h3>
        <div class="inline-row">
          <input v-model.trim="newEnvironment.name" placeholder="环境名称（如 staging）" />
          <input v-model.trim="newEnvironment.description" placeholder="描述（可选）" />
          <button class="primary-btn" @click="createEnvironment">新增环境</button>
        </div>
      </div>
      <div class="chips">
        <button
          v-for="env in environments"
          :key="env.id"
          class="chip"
          :class="{ active: selectedEnvironmentId === env.id }"
          @click="selectEnvironment(env.id)"
        >
          {{ env.name }}
        </button>
      </div>
    </section>

    <section class="panel-card">
      <div class="panel-head">
        <h3>项目变量（支持变量组）</h3>
      </div>
      <div class="inline-row">
        <input v-model.trim="newProjectVariable.key" placeholder="key" />
        <input v-model="newProjectVariable.value" placeholder="value" />
        <input v-model.trim="newProjectVariable.group_name" placeholder="group（可选）" />
        <label class="checkbox"><input type="checkbox" v-model="newProjectVariable.is_secret" />secret</label>
        <button class="primary-btn" @click="saveProjectVariable">保存</button>
      </div>
      <table class="table">
        <thead><tr><th>Key</th><th>Group</th><th>Value</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="item in projectVariables" :key="`pv-${item.id}`">
            <td>{{ item.key }}</td>
            <td>{{ item.group_name || '--' }}</td>
            <td>{{ item.value }}</td>
            <td>
              <button v-if="item.is_secret" class="secondary-btn" @click="revealProject(item.key)">查看密钥</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="panel-card" v-if="selectedEnvironmentId">
      <div class="panel-head">
        <h3>环境变量（{{ selectedEnvironmentName }}）</h3>
      </div>
      <div class="inline-row">
        <input v-model.trim="newEnvironmentVariable.key" placeholder="key" />
        <input v-model="newEnvironmentVariable.value" placeholder="value" />
        <label class="checkbox"><input type="checkbox" v-model="newEnvironmentVariable.is_secret" />secret</label>
        <button class="primary-btn" @click="saveEnvironmentVariable">保存</button>
      </div>
      <table class="table">
        <thead><tr><th>Key</th><th>Value</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="item in environmentVariables" :key="`ev-${item.id}`">
            <td>{{ item.key }}</td>
            <td>{{ item.value }}</td>
            <td>
              <button v-if="item.is_secret" class="secondary-btn" @click="revealEnv(item.key)">查看密钥</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="panel-card" v-if="selectedEnvironmentId">
      <div class="panel-head">
        <h3>变量组绑定（复用）</h3>
      </div>
      <div class="inline-row">
        <select v-model="groupToBind">
          <option value="">选择变量组</option>
          <option v-for="group in projectGroups" :key="group.group_name" :value="group.group_name">
            {{ group.group_name }}（{{ group.variable_count }}）
          </option>
        </select>
        <button class="primary-btn" @click="bindGroup">绑定到当前环境</button>
      </div>
      <ul class="binding-list">
        <li v-for="binding in environmentGroupBindings" :key="binding.id">
          <span>{{ binding.group_name }}</span>
          <button class="secondary-btn" @click="unbindGroup(binding.group_name)">解绑</button>
        </li>
      </ul>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  bindEnvironmentVariableGroup,
  createProjectEnvironment,
  getEnvironmentVariableGroups,
  getEnvironmentVariables,
  getProjectEnvironments,
  getProjectVariableGroups,
  getProjectVariables,
  revealEnvironmentSecret,
  revealProjectSecret,
  unbindEnvironmentVariableGroup,
  upsertEnvironmentVariable,
  upsertProjectVariable,
} from '@/api/environments'

const route = useRoute()
const projectId = Number(route.params.projectId)

const environments = ref([])
const selectedEnvironmentId = ref(null)
const projectVariables = ref([])
const projectGroups = ref([])
const environmentVariables = ref([])
const environmentGroupBindings = ref([])
const groupToBind = ref('')

const newEnvironment = ref({ name: '', description: '' })
const newProjectVariable = ref({ key: '', value: '', is_secret: false, group_name: '' })
const newEnvironmentVariable = ref({ key: '', value: '', is_secret: false })

const selectedEnvironmentName = computed(() => {
  const target = environments.value.find((item) => item.id === selectedEnvironmentId.value)
  return target?.name || ''
})

const fetchEnvironments = async () => {
  environments.value = await getProjectEnvironments(projectId)
  if (!selectedEnvironmentId.value && environments.value.length > 0) {
    selectedEnvironmentId.value = environments.value[0].id
  }
}

const fetchProjectVariables = async () => {
  projectVariables.value = await getProjectVariables(projectId)
  projectGroups.value = await getProjectVariableGroups(projectId)
}

const fetchEnvironmentDetails = async () => {
  if (!selectedEnvironmentId.value) return
  environmentVariables.value = await getEnvironmentVariables(selectedEnvironmentId.value)
  environmentGroupBindings.value = await getEnvironmentVariableGroups(selectedEnvironmentId.value)
}

const selectEnvironment = async (environmentId) => {
  selectedEnvironmentId.value = environmentId
  await fetchEnvironmentDetails()
}

const createEnvironment = async () => {
  if (!newEnvironment.value.name) return
  try {
    await createProjectEnvironment(projectId, {
      name: newEnvironment.value.name,
      description: newEnvironment.value.description || '',
    })
    newEnvironment.value = { name: '', description: '' }
    await fetchEnvironments()
    await fetchEnvironmentDetails()
  } catch {
    alert('创建环境失败')
  }
}

const saveProjectVariable = async () => {
  if (!newProjectVariable.value.key) return
  try {
    await upsertProjectVariable(projectId, {
      key: newProjectVariable.value.key,
      value: newProjectVariable.value.value || '',
      is_secret: newProjectVariable.value.is_secret,
      group_name: newProjectVariable.value.group_name || null,
    })
    newProjectVariable.value = { key: '', value: '', is_secret: false, group_name: '' }
    await fetchProjectVariables()
  } catch {
    alert('保存项目变量失败')
  }
}

const saveEnvironmentVariable = async () => {
  if (!selectedEnvironmentId.value || !newEnvironmentVariable.value.key) return
  try {
    await upsertEnvironmentVariable(selectedEnvironmentId.value, {
      key: newEnvironmentVariable.value.key,
      value: newEnvironmentVariable.value.value || '',
      is_secret: newEnvironmentVariable.value.is_secret,
    })
    newEnvironmentVariable.value = { key: '', value: '', is_secret: false }
    await fetchEnvironmentDetails()
  } catch {
    alert('保存环境变量失败')
  }
}

const bindGroup = async () => {
  if (!selectedEnvironmentId.value || !groupToBind.value) return
  try {
    await bindEnvironmentVariableGroup(selectedEnvironmentId.value, groupToBind.value)
    groupToBind.value = ''
    await fetchEnvironmentDetails()
  } catch {
    alert('绑定变量组失败')
  }
}

const unbindGroup = async (groupName) => {
  if (!selectedEnvironmentId.value) return
  try {
    await unbindEnvironmentVariableGroup(selectedEnvironmentId.value, groupName)
    await fetchEnvironmentDetails()
  } catch {
    alert('解绑变量组失败')
  }
}

const revealProject = async (key) => {
  try {
    const data = await revealProjectSecret(projectId, key)
    alert(`${data.key} = ${data.value}`)
  } catch {
    alert('查看密钥失败')
  }
}

const revealEnv = async (key) => {
  if (!selectedEnvironmentId.value) return
  try {
    const data = await revealEnvironmentSecret(selectedEnvironmentId.value, key)
    alert(`${data.key} = ${data.value}`)
  } catch {
    alert('查看密钥失败')
  }
}

onMounted(async () => {
  await fetchEnvironments()
  await fetchProjectVariables()
  await fetchEnvironmentDetails()
})
</script>

<style scoped>
.env-page { display:flex; flex-direction:column; gap:20px; }
.hero-card, .panel-card { background: rgba(255,255,255,0.84); border:1px solid var(--border-color); border-radius: var(--radius-lg); padding:22px; }
.eyebrow { display:inline-block; margin-top:10px; padding:6px 10px; border-radius:999px; background:var(--primary-soft); color:var(--primary-dark); font-size:12px; font-weight:700; }
.back-link { color: var(--text-muted); text-decoration:none; }
.panel-head { display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:12px; }
.inline-row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
input, select { border:1px solid var(--border-color); border-radius:12px; height:40px; padding:0 12px; background:#fff; }
.primary-btn, .secondary-btn { border-radius:12px; padding:10px 12px; font-weight:700; }
.primary-btn { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color:#fff; }
.secondary-btn { background:#f4f7f7; color:var(--text-main); border:1px solid var(--border-color); }
.chips { display:flex; gap:8px; flex-wrap:wrap; }
.chip { border:1px solid var(--border-color); border-radius:999px; padding:8px 12px; background:#fff; }
.chip.active { background:var(--primary-soft); color:var(--primary-dark); border-color:var(--primary); }
.table { width:100%; border-collapse:collapse; margin-top:12px; }
.table th, .table td { text-align:left; padding:10px; border-bottom:1px solid #edf2f1; }
.checkbox { display:flex; gap:6px; align-items:center; }
.binding-list { margin:10px 0 0; padding:0; list-style:none; display:flex; flex-direction:column; gap:8px; }
.binding-list li { display:flex; justify-content:space-between; align-items:center; border:1px solid var(--border-color); border-radius:12px; padding:10px; }
</style>
