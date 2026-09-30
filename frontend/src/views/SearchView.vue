<script setup>
import { onMounted } from 'vue'
import { useApplicationStore } from '../stores/applications'
import { useSearchStore } from '../stores/search'
import VacancySearchCard from '../components/VacancySearchCard.vue'
import FiltersPanel from '../components/FiltersPanel.vue'
import { ref } from 'vue'

const applicationStore = useApplicationStore()
const searchStore = useSearchStore()

const isFiltersOpen = ref(false)

onMounted(() => {
  if (applicationStore.applications.length === 0) {
    applicationStore.fetchApplications()
  }
})

async function handleLike(vacancy) {
  const isLiked = applicationStore.likedVacancyIds.has(vacancy.id);

  if (isLiked) {
    const appToDelete = applicationStore.applications.find(
      (app) => app.vacancy.id === vacancy.id
    );
    if (appToDelete) {
      await applicationStore.removeApplication(appToDelete.id);
    }
  } else {
    await applicationStore.createApplicationFromVacancy(vacancy.id);
  }
}
</script>

<template>
  <div class="search-page">
    <div class="search-bar">
      <form class="search-form" @submit.prevent="searchStore.search()">
        <input
          v-model="searchStore.query"
          type="text"
          placeholder="Например: python developer"
          class="search-input"
        />
        <button type="submit" class="search-button" :disabled="searchStore.isLoading">
          {{ searchStore.isLoading ? 'Ищем...' : 'Найти' }}
        </button>
      </form>

      <button class="filters-toggle" @click="isFiltersOpen = true">Фильтры</button>
    </div>

    <p v-if="searchStore.error" class="error-text">{{ searchStore.error }}</p>

    <div v-if="searchStore.results.length > 0" class="results-grid">
      <VacancySearchCard
        v-for="vacancy in searchStore.results"
        :key="vacancy.id"
        :vacancy="vacancy"
        :is-liked="applicationStore.likedVacancyIds.has(vacancy.id)"
        @like="handleLike"
      />
    </div>

    <p v-else-if="!searchStore.isLoading && searchStore.query" class="empty-text">
      Ничего не найдено — попробуйте другой запрос
    </p>

    <FiltersPanel
      :is-open="isFiltersOpen"
      v-model="searchStore.filters"
      @close="isFiltersOpen = false"
      @apply="searchStore.search()"
    />
  </div>
</template>

<style scoped>
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 24px;
}

.search-form {
  display: flex;
  gap: 10px;
  flex: 1;
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

.filters-toggle {
  padding: 10px 18px;
  border-radius: 8px;
  border: 1px solid #444;
  background: transparent;
  color: inherit;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  align-items: start;
}

@media (max-width: 700px) {
  .results-grid {
    grid-template-columns: 1fr;
  }
}

.error-text {
  color: #e74c3c;
}

.empty-text {
  color: #888;
}
</style>