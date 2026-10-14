<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const generalError = ref('')

const errors = ref({
  username: '',
  password: ''
})

function validate() {
  let isValid = true
  errors.value = { username: '', password: '' }

  if (!username.value.trim()) {
    errors.value.username = 'Введите логин'
    isValid = false
  } else if (username.value.length < 3) {
    errors.value.username = 'Логин должен быть не менее 3 символов'
    isValid = false
  }

  if (!password.value) {
    errors.value.password = 'Введите пароль'
    isValid = false
  } else if (password.value.length < 6) {
    errors.value.password = 'Пароль должен быть не менее 6 символов'
    isValid = false
  }

  return isValid
}

async function handleSubmit() {
  if (!validate()) return

  isLoading.value = true
  generalError.value = ''

  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    generalError.value = 'Неверный логин или пароль'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <h2>С возвращением!</h2>
        <p>Введите данные для входа в аккаунт</p>
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="username">Логин</label>
          <input 
            id="username"
            v-model="username" 
            type="text" 
            placeholder="Ваш логин" 
            class="auth-input"
            :class="{ 'input-error': errors.username }"
            @input="errors.username = ''"
          />
          <span v-if="errors.username" class="field-error">{{ errors.username }}</span>
        </div>

        <div class="form-group">
          <label for="password">Пароль</label>
          <input 
            id="password"
            v-model="password" 
            type="password" 
            placeholder="••••••••" 
            class="auth-input"
            :class="{ 'input-error': errors.password }"
            @input="errors.password = ''"
          />
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>

        <p v-if="generalError" class="general-error">{{ generalError }}</p>

        <button type="submit" class="auth-button" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          {{ isLoading ? 'Входим...' : 'Войти' }}
        </button>

        <div class="auth-footer">
          <span>Нет аккаунта?</span>
          <router-link to="/register" class="auth-link">Зарегистрироваться</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, var(--bg) 0%, var(--code-bg) 100%);
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 40px 32px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: var(--text-h);
}

.auth-header p {
  margin: 0;
  font-size: 14px;
  color: var(--text);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  margin-left: 4px;
}

.auth-input {
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid var(--border);
  font-size: 14px;
  background: var(--bg);
  color: var(--text-h);
  transition: all 0.2s ease;
  outline: none;
}

.auth-input:focus {
  border-color: #4a6cf7;
  box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.1);
}

.auth-input.input-error {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.field-error {
  font-size: 12px;
  color: #ef4444;
  margin-left: 4px;
}

.general-error {
  background: #fef2f2;
  color: #ef4444;
  padding: 10px;
  border-radius: 8px;
  font-size: 13px;
  text-align: center;
  margin: 0;
  border: 1px solid #fecaca;
}

.auth-button {
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: #4a6cf7;
  color: white;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
}

.auth-button:hover:not(:disabled) {
  background: #3b5bdb;
  transform: translateY(-1px);
}

.auth-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.auth-footer {
  text-align: center;
  font-size: 14px;
  color: var(--text);
  margin-top: 8px;
}

.auth-link {
  color: #4a6cf7;
  text-decoration: none;
  font-weight: 600;
  margin-left: 4px;
  transition: color 0.2s;
}

.auth-link:hover {
  color: #3b5bdb;
  text-decoration: underline;
}
</style>