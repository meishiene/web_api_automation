import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
  },
  {
    path: '/',
    name: 'ProjectList',
    component: () => import('@/views/ProjectList.vue'),
  },
  {
    path: '/project/:projectId',
    name: 'TestCaseList',
    component: () => import('@/views/TestCaseList.vue'),
  },
  {
    path: '/project/:projectId/web-test-cases',
    name: 'WebTestCaseList',
    component: () => import('@/views/WebTestCaseList.vue'),
  },
  {
    path: '/project/:projectId/executions',
    name: 'UnifiedRunList',
    component: () => import('@/views/UnifiedRunList.vue'),
  },
  {
    path: '/project/:projectId/batches',
    name: 'BatchRunList',
    component: () => import('@/views/BatchRunList.vue'),
  },
  {
    path: '/project/:projectId/environments',
    name: 'EnvironmentManager',
    component: () => import('@/views/EnvironmentManager.vue'),
  },
  {
    path: '/project/:projectId/scheduling',
    name: 'SchedulingDashboard',
    component: () => import('@/views/SchedulingDashboard.vue'),
  },
  {
    path: '/project/:projectId/batches/:batchId',
    name: 'BatchRunDetail',
    component: () => import('@/views/BatchRunDetail.vue'),
  },
  {
    path: '/project/:projectId/runs/:runId',
    name: 'TestRunDetail',
    component: () => import('@/views/TestRunDetail.vue'),
  },
  {
    path: '/project/:projectId/web-runs/:runId',
    name: 'WebTestRunDetail',
    component: () => import('@/views/WebTestRunDetail.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard - check auth
router.beforeEach((to, from, next) => {
  const accessToken = localStorage.getItem('accessToken')
  if (to.path !== '/login' && to.path !== '/register' && !accessToken) {
    next('/login')
  } else {
    next()
  }
})

export default router
