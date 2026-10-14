<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

onMounted(() => {
  if (!authStore.user) {
    authStore.fetchMe()
  }
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="profile-page">
    <h2>Профиль</h2>
    <p v-if="authStore.user">Логин: {{ authStore.user.username }}</p>
    <p v-if="authStore.user">Email: {{ authStore.user.email || '—' }}</p>

    <button class="logout-button" @click="handleLogout">Выйти</button>
  </div>
</template>

<style scoped>
.profile-page {
  padding: 24px;
}

.logout-button {
  margin-top: 16px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: #e74c3c;
  color: white;
  font-weight: 600;
  cursor: pointer;
}
</style>