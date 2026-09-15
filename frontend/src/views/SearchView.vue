<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useApplicationStore } from '../stores/applications'

const applicationStore = useApplicationStore()

const query = ref('')
const results = ref([])
const isLoading = ref(false)
const error = ref(null)
const likedVacancyIds = ref(new Set())

async function handleSearch() {
  if (!query.value.trim()) return

  isLoading.value = true
  error.value = null

  try {
    const response = await axios.post('/api/vacancies/search/', {
      query: query.value,
    })
    results.value = response.data
  } catch (err) {
    error.value = 'Не удалось выполнить поиск'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

async function handleLike(vacancy) {
  const success = await applicationStore.createApplicationFromVacancy(vacancy.id)
  if (success) {
    likedVacancyIds.value.add(vacancy.id)
  }
}
</script>

<template>
  <div class="search-page">
    <form class="search-form" @submit.prevent="handleSearch">
      <input
        v-model="query"
        type="text"
        placeholder="Например: python developer"
        class="search-input"
      />
      <button type="submit" class="search-button" :disabled="isLoading">
        {{ isLoading ? 'Ищем...' : 'Найти' }}
      </button>
    </form>

    <p v-if="error" class="error-text">{{ error }}</p>

    <div v-if="results.length > 0" class="results-grid">
      <div v-for="vacancy in results" :key="vacancy.id" class="vacancy-card">
        <p class="vacancy-title">{{ vacancy.title }}</p>
        <p class="vacancy-company">{{ vacancy.company }}</p>

        <button
          class="like-button"
          :class="{ liked: likedVacancyIds.has(vacancy.id) }"
          :disabled="likedVacancyIds.has(vacancy.id)"
          @click="handleLike(vacancy)"
        >
          {{ likedVacancyIds.has(vacancy.id) ? '✓ Добавлено' : '❤️ Отслеживать' }}
        </button>
      </div>
    </div>

    <p v-else-if="!isLoading && query" class="empty-text">
      Ничего не найдено — попробуйте другой запрос
    </p>
  </div>
</template>

<style scoped>
.search-page {
  padding: 24px;
  font-family: system-ui, sans-serif;
}

.search-form {
  display: flex;
  gap: 10px;
  margin-bottom: 24px;
}

.search-input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid #444;
  font-size: 14px;
}

.search-button {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: #4a6cf7;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.search-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.vacancy-card {
  background: #1e1e2e;
  border-radius: 10px;
  padding: 14px;
}

.vacancy-title {
  font-weight: 600;
  margin: 0 0 4px 0;
  font-size: 14px;
}

.vacancy-company {
  color: #999;
  font-size: 13px;
  margin: 0 0 10px 0;
}

.like-button {
  width: 100%;
  padding: 8px;
  border: none;
  border-radius: 6px;
  background: #333;
  color: white;
  cursor: pointer;
  font-size: 13px;
}

.like-button.liked {
  background: #2ecc71;
  cursor: default;
}

.error-text {
  color: #e74c3c;
}

.empty-text {
  color: #888;
}
</style>