<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <div class="logo">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        <h1>创建账户</h1>
        <p>加入我们，开始您的API测试之旅</p>
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
            <input
              id="username"
              v-model="form.username"
              type="text"
              placeholder="选择一个用户名"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6zm3 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"/>
            </svg>
            <input
              id="password"
              v-model="form.password"
              type="password"
              placeholder="设置密码"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6zm3 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"/>
            </svg>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              placeholder="再次输入密码"
              required
            />
          </div>
        </div>

        <div v-if="error" class="error-message">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          {{ error }}
        </div>

        <div v-if="success" class="success-message">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          {{ success }}
        </div>

        <button type="submit" :disabled="loading || success" class="register-btn">
          <span v-if="loading" class="loading-spinner"></span>
          <svg v-else viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          {{ loading ? '注册中...' : '创建账户' }}
        </button>
      </form>

      <div class="register-footer">
        <p>已有账户？
          <router-link to="/login" class="login-link">立即登录</router-link>
        </p>
      </div>
    </div>

    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
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
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  position: relative;
  overflow: hidden;
  padding: 2rem 1rem;
}

.register-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: var(--border-radius-lg);
  padding: 3rem 2.5rem;
  width: 100%;
  max-width: 420px;
  box-shadow: var(--shadow-lg);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 10;
}

.register-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.logo {
  width: 4rem;
  height: 4rem;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  color: white;
  box-shadow: var(--shadow-md);
}

.logo svg {
  width: 2rem;
  height: 2rem;
}

.register-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--gray-800);
  margin-bottom: 0.5rem;
}

.register-header p {
  color: var(--gray-600);
  font-size: 1rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--gray-700);
  font-size: 0.875rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  width: 1.25rem;
  height: 1.25rem;
  color: var(--gray-400);
  z-index: 1;
}

.input-wrapper input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  border: 2px solid var(--gray-200);
  border-radius: var(--border-radius);
  font-size: 1rem;
  background: var(--gray-50);
  transition: all 0.2s ease;
  outline: none;
}

.input-wrapper input:focus {
  border-color: var(--primary-color);
  background: white;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.input-wrapper input::placeholder {
  color: var(--gray-400);
}

.error-message,
.success-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  font-weight: 500;
}

.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: var(--error-color);
}

.success-message {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: var(--success-color);
}

.error-message svg,
.success-message svg {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.register-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem 2rem;
  background: linear-gradient(135deg, var(--success-color), #059669);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow);
  position: relative;
  overflow: hidden;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.register-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.register-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

.register-footer {
  text-align: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--gray-200);
}

.register-footer p {
  color: var(--gray-600);
  font-size: 0.875rem;
  margin: 0;
}

.login-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.login-link:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  z-index: 1;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  right: -150px;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  bottom: -100px;
  left: -100px;
  animation-delay: 2s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  left: -75px;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* 响应式设计 */
@media (max-width: 480px) {
  .register-card {
    padding: 2rem 1.5rem;
    margin: 1rem;
  }

  .register-header h1 {
    font-size: 1.75rem;
  }

  .background-decoration {
    display: none;
  }
}
</style>
