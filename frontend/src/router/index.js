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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard - check auth
router.beforeEach((to, from, next) => {
  const userId = localStorage.getItem('userId')
  if (to.path !== '/login' && to.path !== '/register' && !userId) {
    next('/login')
  } else {
    next()
  }
})

export default router
