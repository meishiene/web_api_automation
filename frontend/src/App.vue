<template>
  <div id="app">
    <header v-if="showHeader" class="header">
      <div class="logo">自动化测试平台</div>
      <div class="user-info">
        <span>{{ username }}</span>
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </div>
    </header>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const username = ref('')

const showHeader = computed(() => {
  return !['/login', '/register'].includes(route.path)
})

onMounted(() => {
  const userId = localStorage.getItem('userId')
  if (userId) {
    username.value = `用户 ${userId}`
  }
})

const handleLogout = () => {
  localStorage.removeItem('userId')
  router.push('/login')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f5f5;
}

#app {
  min-height: 100vh;
}

.header {
  background: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.25rem;
  font-weight: bold;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logout-btn {
  padding: 0.5rem 1rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.logout-btn:hover {
  background: #c0392b;
}

.main {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
