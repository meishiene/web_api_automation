<template>
  <section class="projects-page">
    <div class="toolbar-card">
      <div class="toolbar-left">
        <button class="primary-btn" @click="openCreateModal">新建项目</button>
        <div class="filter-group">
          <label>状态筛选</label>
          <select v-model="statusFilter">
            <option value="all">全部</option>
            <option value="active">进行中</option>
            <option value="archived">已归档（预留）</option>
          </select>
        </div>
      </div>

      <div class="toolbar-stats">
        <div><span>总项目</span><strong>{{ projects.length }}</strong></div>
        <div><span>进行中</span><strong class="success">{{ activeProjects.length }}</strong></div>
        <div><span>已归档</span><strong class="muted">0</strong></div>
      </div>
    </div>

    <div v-if="loading" class="state-card">正在加载项目...</div>
    <div v-else-if="filteredProjects.length === 0" class="state-card">当前没有匹配的项目</div>

    <div v-else class="projects-grid">
      <article v-for="project in filteredProjects" :key="project.id" class="project-card">
        <div class="project-head">
          <div class="project-copy">
            <div class="title-row">
              <h3>{{ project.name }}</h3>
              <span class="status-pill active">进行中</span>
            </div>
            <p>{{ project.description || '当前项目暂无描述' }}</p>
            <small>项目代码：{{ projectCode(project) }}</small>
          </div>

          <div class="project-actions">
            <button class="icon-btn" @click="openEditModal(project)">编辑</button>
            <button class="icon-btn" @click="openMembersModal(project)">成员</button>
            <button class="icon-btn" @click="openProjectEnvironment(project.id)">环境</button>
            <button class="icon-btn danger" @click="deleteProjectById(project.id)">删除</button>
          </div>
        </div>

        <div class="project-metrics">
          <div class="metric-box">
            <strong>{{ projectStats[project.id]?.totalCases ?? '--' }}</strong>
            <span>测试用例</span>
          </div>
          <div class="metric-box">
            <strong class="primary">{{ projectStats[project.id]?.apiTests ?? '--' }}</strong>
            <span>API测试</span>
          </div>
          <div class="metric-box">
            <strong class="violet">{{ projectStats[project.id]?.uiTests ?? '--' }}</strong>
            <span>UI测试</span>
          </div>
          <div class="metric-box">
            <strong class="amber">{{ projectStats[project.id]?.memberCount ?? '--' }}</strong>
            <span>成员数量</span>
          </div>
        </div>

        <div class="project-footer">
          <div class="footer-meta">
            <span>创建于 {{ formatDate(project.created_at) }}</span>
            <span>更新于 {{ formatDate(project.updated_at || project.created_at) }}</span>
          </div>
          <div class="footer-links">
            <button class="link-btn" @click="openProjectDetail(project)">详情</button>
            <button class="link-btn" @click="openApiProject(project.id)">API</button>
            <button class="link-btn" @click="openUiProject(project.id)">UI</button>
            <button class="link-btn" @click="openTaskProject(project.id)">任务</button>
            <button class="link-btn" @click="openReportProject(project.id)">报告</button>
          </div>
        </div>
      </article>
    </div>

    <div v-if="showModal" class="modal-mask" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-head">
          <h2>{{ modalMode === 'create' ? '新建项目' : '编辑项目' }}</h2>
          <button class="close-btn" @click="closeModal">×</button>
        </div>

        <form class="modal-form" @submit.prevent="submitProject">
          <label class="field-block">
            <span>项目名称 <em>*</em></span>
            <input v-model.trim="form.name" type="text" placeholder="请输入项目名称" />
          </label>

          <label class="field-block">
            <span>项目代码</span>
            <input :value="projectCode(form)" type="text" disabled />
            <small>当前后端仅保存名称 / 描述，项目代码前端预留展示。</small>
          </label>

          <label class="field-block">
            <span>项目描述</span>
            <textarea v-model.trim="form.description" rows="3" placeholder="请输入项目描述"></textarea>
          </label>

          <div class="double-grid">
            <label class="field-block">
              <span>项目状态</span>
              <select disabled>
                <option>进行中</option>
              </select>
            </label>
            <label class="field-block">
              <span>项目负责人</span>
              <input :value="username" disabled />
            </label>
          </div>

          <label class="field-block">
            <span>项目成员</span>
            <div class="placeholder-box">可先保存项目，再通过“成员”按钮进入成员治理弹窗维护角色与协作入口。</div>
          </label>

          <p v-if="formError" class="form-error">{{ formError }}</p>

          <div class="modal-actions">
            <button type="button" class="ghost-btn" @click="closeModal">取消</button>
            <button type="submit" class="primary-btn" :disabled="saving">
              {{ saving ? '保存中...' : modalMode === 'create' ? '创建项目' : '保存修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showMembersModal" class="modal-mask" @click.self="closeMembersModal">
      <div class="modal-card member-modal">
        <div class="modal-head">
          <h2>项目成员管理</h2>
          <button class="close-btn" @click="closeMembersModal">×</button>
        </div>

        <div class="member-layout">
          <section class="member-panel">
            <div class="member-head">
              <div>
                <h3>{{ selectedProjectForMembers?.name }}</h3>
                <p>负责人：{{ ownerName(selectedProjectForMembers?.owner_id) }}</p>
              </div>
              <button class="ghost-btn" @click="reloadMembers" :disabled="memberLoading">{{ memberLoading ? '刷新中...' : '刷新成员' }}</button>
            </div>

            <div class="member-list" v-if="projectMembers.length">
              <article v-for="member in projectMembers" :key="member.id" class="member-card">
                <div>
                  <strong>{{ member.username || `用户 #${member.user_id}` }}</strong>
                  <p>User ID：{{ member.user_id }}</p>
                </div>
                <div class="member-actions">
                  <select v-model="member.role" @change="updateMemberRole(member)">
                    <option value="maintainer">maintainer</option>
                    <option value="editor">editor</option>
                    <option value="viewer">viewer</option>
                  </select>
                  <button class="link-btn danger" @click="removeMember(member)">移除</button>
                </div>
              </article>
            </div>
            <div v-else class="placeholder-box">当前项目还没有额外成员，负责人默认拥有全部管理权限。</div>
          </section>

          <section class="member-panel">
            <div class="member-head">
              <div>
                <h3>添加成员</h3>
                <p>从现有用户中选择，并指定在本项目中的角色。</p>
              </div>
            </div>

            <div class="modal-form">
              <label class="field-block">
                <span>选择用户</span>
                <select v-model.number="memberForm.user_id">
                  <option :value="0">请选择用户</option>
                  <option v-for="user in availableUsers" :key="user.id" :value="user.id">
                    {{ user.username }}（#{{ user.id }} / {{ user.role }}）
                  </option>
                </select>
              </label>

              <label class="field-block">
                <span>项目角色</span>
                <select v-model="memberForm.role">
                  <option value="maintainer">maintainer</option>
                  <option value="editor">editor</option>
                  <option value="viewer">viewer</option>
                </select>
              </label>

              <div class="role-guide">
                <div><strong>maintainer</strong><span>可管理成员与项目资产</span></div>
                <div><strong>editor</strong><span>可维护和执行测试资产</span></div>
                <div><strong>viewer</strong><span>可查看项目与执行结果</span></div>
              </div>

              <p v-if="memberError" class="form-error">{{ memberError }}</p>

              <div class="modal-actions">
                <button class="primary-btn" @click="addMember" :disabled="memberSaving">{{ memberSaving ? '保存中...' : '添加成员' }}</button>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>

    <div v-if="showDetailDrawer" class="drawer-mask" @click.self="closeDetailDrawer">
      <div class="drawer-card">
        <div class="drawer-head">
          <div>
            <h2>{{ detailProject?.name }}</h2>
            <p>{{ detailProject?.description || '当前项目暂无描述' }}</p>
          </div>
          <button class="close-btn" @click="closeDetailDrawer">×</button>
        </div>

        <div class="drawer-body">
          <section class="detail-section">
            <h3>项目概览</h3>
            <div class="detail-grid">
              <div><label>项目代码</label><span>{{ projectCode(detailProject) }}</span></div>
              <div><label>负责人</label><span>{{ ownerName(detailProject?.owner_id) }}</span></div>
              <div><label>创建时间</label><span>{{ formatDate(detailProject?.created_at) }}</span></div>
              <div><label>最近更新</label><span>{{ formatDate(detailProject?.updated_at || detailProject?.created_at) }}</span></div>
            </div>
          </section>

          <section class="detail-section">
            <h3>资产概览</h3>
            <div class="asset-metrics">
              <div class="asset-box"><strong>{{ detailStats?.totalCases ?? '--' }}</strong><span>总用例</span></div>
              <div class="asset-box"><strong class="primary">{{ detailStats?.apiTests ?? '--' }}</strong><span>API</span></div>
              <div class="asset-box"><strong class="violet">{{ detailStats?.uiTests ?? '--' }}</strong><span>UI</span></div>
              <div class="asset-box"><strong class="amber">{{ detailStats?.memberCount ?? '--' }}</strong><span>成员</span></div>
            </div>
          </section>

          <section class="detail-section">
            <h3>资产流转入口</h3>
            <div class="asset-actions">
              <button class="primary-btn" @click="openApiProject(detailProject.id)">进入 API 工作台</button>
              <button class="ghost-btn" @click="openUiProject(detailProject.id)">进入 UI 工作台</button>
              <button class="ghost-btn" @click="openProjectEnvironment(detailProject.id)">环境治理</button>
              <button class="ghost-btn" @click="openMembersModal(detailProject)">成员治理</button>
              <button class="ghost-btn" @click="handleExportProjectCases(detailProject.id)">导出 API 用例</button>
              <button class="ghost-btn" @click="openReportProject(detailProject.id)">查看报告</button>
            </div>
          </section>

          <section class="detail-section">
            <h3>最近活动</h3>
            <div class="activity-list">
              <article class="activity-card">
                <strong>项目创建</strong>
                <span>{{ formatDate(detailProject?.created_at) }}</span>
              </article>
              <article class="activity-card">
                <strong>最近维护</strong>
                <span>{{ formatDate(detailProject?.updated_at || detailProject?.created_at) }}</span>
              </article>
              <article class="activity-card">
                <strong>资产规模</strong>
                <span>API {{ detailStats?.apiTests ?? '--' }} / UI {{ detailStats?.uiTests ?? '--' }}</span>
              </article>
            </div>
          </section>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createProject, deleteProject, deleteProjectMember, getProjectMembers, getProjects, updateProject, upsertProjectMember } from '@/api/projects'
import { exportTestCases, getTestCases } from '@/api/testCases'
import { getUsers } from '@/api/users'
import { getWebTestCases } from '@/api/webTestCases'
import { setActiveProjectId } from '@/utils/projectContext'

const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const projects = ref([])
const projectStats = ref({})
const allUsers = ref([])
const statusFilter = ref('all')
const showModal = ref(false)
const modalMode = ref('create')
const editingId = ref(null)
const formError = ref('')
const showMembersModal = ref(false)
const selectedProjectForMembers = ref(null)
const projectMembers = ref([])
const memberLoading = ref(false)
const memberSaving = ref(false)
const memberError = ref('')
const memberForm = ref({ user_id: 0, role: 'viewer' })
const showDetailDrawer = ref(false)
const detailProject = ref(null)
const form = ref({ name: '', description: '' })
const username = localStorage.getItem('username') || '测试工程师'

const activeProjects = computed(() => projects.value)
const userMap = computed(() => Object.fromEntries(allUsers.value.map((item) => [item.id, item])))
const filteredProjects = computed(() => {
  if (statusFilter.value === 'archived') return []
  return projects.value
})
const availableUsers = computed(() => {
  const currentProject = selectedProjectForMembers.value
  if (!currentProject) return []
  const memberIds = new Set(projectMembers.value.map((item) => item.user_id))
  return allUsers.value.filter((user) => user.id !== currentProject.owner_id && !memberIds.has(user.id))
})

const normalizeTimestamp = (value) => {
  if (!value) return 0
  const numeric = Number(value)
  return numeric > 1e12 ? numeric : numeric * 1000
}

const formatDate = (value) => {
  if (!value) return '--'
  return new Date(normalizeTimestamp(value)).toLocaleDateString('zh-CN')
}

const projectCode = (project) => {
  const name = project?.name || ''
  if (!name) return 'PROJECT_CODE'
  return name
    .trim()
    .toUpperCase()
    .replace(/[^A-Z0-9\u4E00-\u9FFF]+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '') || 'PROJECT_CODE'
}

const fetchProjects = async () => {
  loading.value = true
  try {
    projects.value = await getProjects()
  } catch (err) {
    alert(err.response?.data?.detail || '获取项目失败')
  } finally {
    loading.value = false
  }
}

const fetchUsers = async () => {
  allUsers.value = await getUsers()
}

const fetchProjectStats = async () => {
  const statsEntries = await Promise.all(
    projects.value.map(async (project) => {
      try {
        const [apiCases, uiCases, members] = await Promise.all([
          getTestCases(project.id),
          getWebTestCases(project.id),
          getProjectMembers(project.id),
        ])
        return [
          project.id,
          {
            apiTests: apiCases.length,
            uiTests: uiCases.length,
            totalCases: apiCases.length + uiCases.length,
            memberCount: members.length + 1,
          },
        ]
      } catch (err) {
        return [
          project.id,
          {
            apiTests: '--',
            uiTests: '--',
            totalCases: '--',
            memberCount: '--',
          },
        ]
      }
    })
  )
  projectStats.value = Object.fromEntries(statsEntries)
}

const refreshAll = async () => {
  await fetchProjects()
  await fetchUsers()
  if (projects.value.length) {
    await fetchProjectStats()
  } else {
    projectStats.value = {}
  }
}

const ownerName = (userId) => userMap.value[userId]?.username || `用户 #${userId}`

const openCreateModal = () => {
  modalMode.value = 'create'
  editingId.value = null
  form.value = { name: '', description: '' }
  formError.value = ''
  showModal.value = true
}

const openEditModal = (project) => {
  modalMode.value = 'edit'
  editingId.value = project.id
  form.value = {
    name: project.name || '',
    description: project.description || '',
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  saving.value = false
  formError.value = ''
}

const openMembersModal = async (project) => {
  selectedProjectForMembers.value = project
  memberForm.value = { user_id: 0, role: 'viewer' }
  memberError.value = ''
  showMembersModal.value = true
  await reloadMembers()
}

const closeMembersModal = () => {
  showMembersModal.value = false
  selectedProjectForMembers.value = null
  projectMembers.value = []
  memberError.value = ''
  memberSaving.value = false
}

const openProjectDetail = (project) => {
  detailProject.value = project
  showDetailDrawer.value = true
}

const closeDetailDrawer = () => {
  showDetailDrawer.value = false
  detailProject.value = null
}

const detailStats = computed(() => {
  if (!detailProject.value) return null
  return projectStats.value[detailProject.value.id] || null
})

const reloadMembers = async () => {
  if (!selectedProjectForMembers.value) return
  memberLoading.value = true
  try {
    projectMembers.value = await getProjectMembers(selectedProjectForMembers.value.id)
  } catch (err) {
    memberError.value = err.response?.data?.detail || '加载成员失败'
  } finally {
    memberLoading.value = false
  }
}

const addMember = async () => {
  if (!selectedProjectForMembers.value) return
  if (!memberForm.value.user_id) {
    memberError.value = '请选择要添加的用户'
    return
  }
  memberSaving.value = true
  memberError.value = ''
  try {
    await upsertProjectMember(selectedProjectForMembers.value.id, { ...memberForm.value })
    memberForm.value = { user_id: 0, role: 'viewer' }
    await Promise.all([reloadMembers(), fetchProjectStats()])
  } catch (err) {
    memberError.value = err.response?.data?.detail || '添加成员失败'
  } finally {
    memberSaving.value = false
  }
}

const updateMemberRole = async (member) => {
  if (!selectedProjectForMembers.value) return
  try {
    await upsertProjectMember(selectedProjectForMembers.value.id, {
      user_id: member.user_id,
      role: member.role,
    })
    await Promise.all([reloadMembers(), fetchProjectStats()])
  } catch (err) {
    memberError.value = err.response?.data?.detail || '更新成员角色失败'
  }
}

const removeMember = async (member) => {
  if (!selectedProjectForMembers.value) return
  if (!confirm(`确定移除成员「${member.username || member.user_id}」吗？`)) return
  try {
    await deleteProjectMember(selectedProjectForMembers.value.id, member.user_id)
    await Promise.all([reloadMembers(), fetchProjectStats()])
  } catch (err) {
    memberError.value = err.response?.data?.detail || '移除成员失败'
  }
}

const handleExportProjectCases = async (projectId) => {
  try {
    const payload = await exportTestCases(projectId)
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `project-${projectId}-api-test-cases.json`
    link.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    alert(err.response?.data?.detail || '导出 API 用例失败')
  }
}

const submitProject = async () => {
  if (!form.value.name.trim()) {
    formError.value = '项目名称不能为空'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    if (modalMode.value === 'create') {
      await createProject({ ...form.value })
    } else {
      await updateProject(editingId.value, { ...form.value })
    }
    closeModal()
    await refreshAll()
  } catch (err) {
    formError.value = err.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

const deleteProjectById = async (projectId) => {
  if (!confirm('确定要删除这个项目吗？')) return
  try {
    await deleteProject(projectId)
    await refreshAll()
  } catch (err) {
    alert(err.response?.data?.detail || '删除失败')
  }
}

const useProject = (projectId, path) => {
  setActiveProjectId(projectId)
  router.push(path)
}

const openApiProject = (projectId) => useProject(projectId, `/project/${projectId}`)
const openUiProject = (projectId) => useProject(projectId, `/project/${projectId}/web-test-cases`)
const openTaskProject = (projectId) => useProject(projectId, `/project/${projectId}/scheduling`)
const openReportProject = (projectId) => useProject(projectId, `/project/${projectId}/reports`)
const openProjectEnvironment = (projectId) => useProject(projectId, `/project/${projectId}/environments`)

onMounted(refreshAll)
</script>

<style scoped>
.projects-page { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.toolbar-card,
.project-card,
.modal-card,
.state-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); box-shadow: var(--surface-shadow); }
.toolbar-card { padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.toolbar-left,
.toolbar-stats { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.toolbar-stats div { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-main); }
.toolbar-stats strong { color: var(--text-strong); font-size: 16px; }
.toolbar-stats strong.success { color: var(--success); }
.toolbar-stats strong.muted { color: var(--text-muted); }
.filter-group { display: flex; align-items: center; gap: 8px; }
.filter-group label { font-size: 13px; color: var(--text-main); }
.filter-group select,
.field-block input,
.field-block select,
.field-block textarea {
  width: 100%;
  border: 1px solid var(--border-color-strong);
  border-radius: var(--radius);
  background: var(--bg-card);
  color: var(--text-main);
  outline: none;
}
.filter-group select { height: 32px; padding: 0 12px; min-width: 140px; }
.projects-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.project-card { padding: 20px; display: flex; flex-direction: column; gap: 18px; }
.project-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.project-copy h3 { margin: 0; font-size: 16px; font-weight: 500; color: var(--text-strong); }
.project-copy p { margin: 10px 0 6px; font-size: 13px; color: var(--text-main); }
.project-copy small { font-size: 12px; color: var(--text-muted); }
.title-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.project-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.icon-btn,
.primary-btn,
.ghost-btn,
.link-btn { min-height: 32px; padding: 0 14px; border-radius: var(--radius); font-size: 13px; }
.icon-btn { border: 1px solid var(--border-color-strong); background: transparent; color: var(--text-main); }
.icon-btn.danger { color: var(--danger); }
.primary-btn { border: 1px solid var(--primary); background: var(--primary); color: #fff; }
.ghost-btn { border: 1px solid var(--border-color-strong); background: transparent; color: var(--text-main); }
.link-btn { border: 0; background: transparent; color: var(--primary); padding: 0; min-height: auto; }
.status-pill { display: inline-flex; align-items: center; justify-content: center; padding: 4px 10px; border-radius: 999px; font-size: 12px; }
.status-pill.active { background: #e8f5e9; color: #27ae60; }
.project-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  padding: 16px 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}
.metric-box { text-align: center; }
.metric-box strong { display: block; margin-bottom: 6px; font-size: 22px; font-weight: 500; color: var(--text-strong); }
.metric-box strong.primary { color: var(--primary); }
.metric-box strong.violet { color: #9b59b6; }
.metric-box strong.amber { color: var(--warning); font-size: 16px; }
.metric-box span { font-size: 12px; color: var(--text-muted); }
.project-footer { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.footer-meta { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; font-size: 12px; color: var(--text-muted); }
.footer-links { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.state-card { min-height: 160px; display: grid; place-items: center; color: var(--text-muted); text-align: center; }
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.32); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 999; }
.modal-card { width: min(720px, 100%); padding: 24px; }
.modal-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 18px; }
.modal-head h2 { margin: 0; font-size: 18px; font-weight: 500; color: var(--text-strong); }
.close-btn { border: 0; background: transparent; color: var(--text-muted); font-size: 20px; }
.modal-form { display: flex; flex-direction: column; gap: 16px; }
.field-block { display: flex; flex-direction: column; gap: 8px; }
.field-block span { font-size: 13px; color: var(--text-main); }
.field-block span em { color: var(--danger); font-style: normal; }
.field-block input,
.field-block select { height: 36px; padding: 0 12px; }
.field-block textarea { min-height: 96px; padding: 10px 12px; resize: vertical; }
.field-block small { font-size: 12px; color: var(--text-muted); }
.double-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.placeholder-box { padding: 14px; border-radius: var(--radius); background: var(--bg-muted); font-size: 13px; color: var(--text-muted); line-height: 1.6; }
.form-error { margin: 0; color: var(--danger); font-size: 13px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; }
.member-modal { width: min(980px, 100%); }
.member-layout { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 20px; }
.member-panel { display: flex; flex-direction: column; gap: 16px; }
.member-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.member-head h3 { margin: 0 0 6px; font-size: 16px; color: var(--text-strong); }
.member-head p { margin: 0; font-size: 13px; color: var(--text-muted); }
.member-list { display: flex; flex-direction: column; gap: 12px; }
.member-card { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px; border: 1px solid var(--border-color); border-radius: var(--radius); background: var(--bg-muted); }
.member-card strong { color: var(--text-strong); }
.member-card p { margin: 6px 0 0; font-size: 12px; color: var(--text-muted); }
.member-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.member-actions select { height: 32px; min-width: 120px; padding: 0 12px; border: 1px solid var(--border-color-strong); border-radius: var(--radius); background: var(--bg-card); color: var(--text-main); }
.role-guide { display: flex; flex-direction: column; gap: 10px; padding: 14px; border-radius: var(--radius); background: var(--bg-muted); }
.role-guide div { display: flex; flex-direction: column; gap: 4px; }
.role-guide strong { color: var(--text-strong); font-size: 13px; }
.role-guide span { color: var(--text-muted); font-size: 12px; }
.drawer-mask { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.32); display: flex; justify-content: flex-end; z-index: 999; }
.drawer-card { width: min(680px, 100%); height: 100%; background: var(--bg-card); border-left: 1px solid var(--border-color); box-shadow: var(--surface-shadow); overflow-y: auto; }
.drawer-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; padding: 24px; border-bottom: 1px solid var(--border-color); }
.drawer-head h2 { margin: 0 0 8px; font-size: 20px; color: var(--text-strong); }
.drawer-head p { margin: 0; font-size: 13px; color: var(--text-muted); }
.drawer-body { padding: 24px; display: flex; flex-direction: column; gap: 20px; }
.detail-section { display: flex; flex-direction: column; gap: 12px; }
.detail-section h3 { margin: 0; font-size: 16px; color: var(--text-strong); }
.detail-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 16px; }
.detail-grid div { display: flex; flex-direction: column; gap: 6px; }
.detail-grid label { font-size: 12px; color: var(--text-muted); }
.detail-grid span { font-size: 14px; color: var(--text-strong); }
.asset-metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.asset-box { padding: 14px; border: 1px solid var(--border-color); border-radius: var(--radius); background: var(--bg-muted); text-align: center; }
.asset-box strong { display: block; margin-bottom: 6px; font-size: 22px; color: var(--text-strong); }
.asset-box strong.primary { color: var(--primary); }
.asset-box strong.violet { color: #9b59b6; }
.asset-box strong.amber { color: var(--warning); }
.asset-box span { font-size: 12px; color: var(--text-muted); }
.asset-actions { display: flex; gap: 12px; flex-wrap: wrap; }
.activity-list { display: flex; flex-direction: column; gap: 10px; }
.activity-card { padding: 14px; border: 1px solid var(--border-color); border-radius: var(--radius); background: var(--bg-muted); display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: 13px; color: var(--text-main); }
.activity-card strong { color: var(--text-strong); }

@media (max-width: 1100px) {
  .projects-grid { grid-template-columns: 1fr; }
}

@media (max-width: 860px) {
  .projects-page { padding: 16px; }
  .project-head,
  .project-footer,
  .toolbar-card,
  .toolbar-left,
  .member-head,
  .member-card,
  .drawer-head,
  .activity-card { flex-direction: column; align-items: flex-start; }
  .project-metrics,
  .double-grid,
  .member-layout,
  .detail-grid,
  .asset-metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 640px) {
  .double-grid,
  .member-layout,
  .detail-grid,
  .asset-metrics { grid-template-columns: 1fr; }
}
</style>
