<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useApplicationStore } from '../stores/applications'
import VacancySearchCard from '../components/VacancySearchCard.vue'

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
      <VacancySearchCard
        v-for="vacancy in results"
        :key="vacancy.id"
        :vacancy="vacancy"
        :is-liked="likedVacancyIds.has(vacancy.id)"
        @like="handleLike"
      />
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
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (max-width: 700px) {
  .results-grid {
    grid-template-columns: 1fr;
  }
}с

.error-text {
  color: #e74c3c;
}

.empty-text {
  color: #888;
}
</style>