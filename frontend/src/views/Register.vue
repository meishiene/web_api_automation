<template>
  <div class="register-container">
    <div class="register-card">
      <h2>注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>用户名</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            required
          />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            required
          />
        </div>
        <div class="form-group">
          <label>确认密码</label>
          <input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            required
          />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">注册成功！正在跳转登录...</p>
        <button type="submit" :disabled="loading || success">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <div class="footer">
        已有账号？<router-link to="/login">登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'

const router = useRouter()
const form = ref({ username: '', password: '', confirmPassword: '' })
const loading = ref(false)
const error = ref('')
const success = ref(false)

const handleRegister = async () => {
  if (form.value.password !== form.value.confirmPassword) {
    error.value = '两次密码输入不一致'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await request.post('/api/auth/register', {
      username: form.value.username,
      password: form.value.password,
    })
    success.value = true
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    error.value = err.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}
.register-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
h2 {
  margin: 0 0 1.5rem 0;
  text-align: center;
}
.form-group {
  margin-bottom: 1rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
}
input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 0.75rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.error {
  color: #f44336;
  margin: 0.5rem 0;
  font-size: 0.875rem;
}
.success {
  color: #4CAF50;
  margin: 0.5rem 0;
  font-size: 0.875rem;
}
.footer {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.875rem;
}
.footer a {
  color: #4CAF50;
  text-decoration: none;
}
</style>
