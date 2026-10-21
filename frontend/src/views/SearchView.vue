<script setup>
import { ref, onMounted, watch } from 'vue'
import { useApplicationStore } from '../stores/applications'
import { useSearchStore } from '../stores/search'
import { useRecommendationsStore } from '../stores/recommendations'
import { useProfileStore } from '../stores/profile'
import VacancySearchCard from '../components/VacancySearchCard.vue'
import FiltersPanel from '../components/FiltersPanel.vue'

const applicationStore = useApplicationStore()
const searchStore = useSearchStore()
const recommendationsStore = useRecommendationsStore()
const profileStore = useProfileStore()

const isFiltersOpen = ref(false)
const recommendationsPanelRef = ref(null)

onMounted(async () => {
  if (applicationStore.applications.length === 0) {
    await applicationStore.fetchApplications()
  }
  await profileStore.fetchProfile()
  recommendationsStore.setMode('recommendations')
  await recommendationsStore.loadRecommendations()
})

watch(
  () => recommendationsStore.mode,
  (mode) => {
    if (mode === 'recommendations') {
      searchStore.results = []
      searchStore.query = ''
    }
  }
)

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

function handleSearch() {
  searchStore.search()
  recommendationsStore.setMode('search')
}

async function handleSyncRecommendations() {
  await recommendationsStore.syncRecommendations()
}

async function handleDismiss(id) {
  await recommendationsStore.dismissRecommendation(id)
}

async function handleMarkSeen() {
  const newIds = recommendationsStore.filteredRecommendations
    .filter((r) => r.is_new)
    .map((r) => r.id)
  await recommendationsStore.markSeen(newIds)
}

function hasSkills() {
  return profileStore.skills && profileStore.skills.length > 0
}

</script>

<template>
  <div class="search-page">
    <div class="search-bar">
      <form class="search-form" @submit.prevent="handleSearch">
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

    <!-- Режимы: рекомендации / результаты поиска -->
    <div class="mode-panel">
      <button
        class="mode-button"
        :class="{ active: recommendationsStore.mode === 'recommendations' }"
        @click="recommendationsStore.setMode('recommendations')"
      >
        Рекомендации по профилю
      </button>
      <button
        class="mode-button"
        :class="{ active: recommendationsStore.mode === 'search' }"
        @click="handleSearch"
      >
        Результаты поиска
      </button>
    </div>

    <!-- Панель рекомендаций (открыта по умолчанию) -->
    <div v-if="recommendationsStore.mode === 'recommendations'" class="recommendations-panel">
      <div class="recommendations-controls">
        <p class="panel-title">Рекомендации по профилю</p>

        <div class="profile-pills">
          <button
            class="profile-pill"
            :class="{ active: recommendationsStore.selectedVariantId === null }"
            @click="recommendationsStore.setSelectedVariantId(null)"
          >
            Базовый профиль
          </button>
          <button
            v-for="variant in profileStore.variants"
            :key="variant.id"
            class="profile-pill"
            :class="{ active: recommendationsStore.selectedVariantId === variant.id }"
            @click="recommendationsStore.setSelectedVariantId(variant.id)"
          >
            {{ variant.title }}
          </button>
        </div>

        <label class="only-new-label">
          <input
            type="checkbox"
            :checked="recommendationsStore.onlyNew"
            @change="recommendationsStore.setOnlyNew($event.target.checked)"
          />
          Только новые
        </label>

        <button
          class="sync-button"
          :disabled="recommendationsStore.isLoading"
          @click="handleSyncRecommendations"
        >
          {{ recommendationsStore.isLoading ? 'Обновляем...' : 'Обновить рекомендации' }}
        </button>
      </div>

      <div v-if="recommendationsStore.error" class="error-text">
        {{ recommendationsStore.error }}
      </div>

      <div
        v-if="recommendationsStore.filteredRecommendations.length > 0"
        class="results-grid"
      >
        <VacancySearchCard
          v-for="rec in recommendationsStore.filteredRecommendations"
          :key="rec.id"
          :vacancy="rec.vacancy"
          :is-liked="applicationStore.likedVacancyIds.has(rec.vacancy.id)"
          :match="rec.score"
          :is-new="rec.is_new"
          :matched-skills="rec.matched_skills"
          :missing-skills="rec.missing_skills"
          :is-recommendation="true"
          :recommendation-id="rec.id"
          :on-dismiss="(recommendationId) => handleDismiss(recommendationId)"
          @like="handleLike"
        />
      </div>

      <div
        v-else
        :class="[
          'empty-state',
          recommendationsStore.isLoading ? 'loading' : '',
        ]"
      >
        <p v-if="recommendationsStore.isLoading">Загружаем рекомендации…</p>
        <p v-else-if="!hasSkills()">
          Чтобы подобрать вакансии по вашим навыкам, укажите их в профиле.
        </p>
        <p v-else>Подходящих вакансий пока нет.</p>

        <button class="btn-primary" @click="handleSyncRecommendations">
          Подобрать свежие вакансии по моим навыкам
        </button>
      </div>

      <div v-if="recommendationsStore.filteredRecommendations.length > 0" class="recommendations-footer">
        <button
          class="mark-seen-button"
          :disabled="recommendationsStore.isLoading"
          @click="handleMarkSeen"
        >
          Отметить просмотренными
        </button>
      </div>
    </div>

    <!-- Результаты обычного поиска -->
    <div v-if="recommendationsStore.mode === 'search'">
      <div
        v-if="searchStore.results.length > 0"
        class="results-grid"
      >
        <VacancySearchCard
          v-for="vacancy in searchStore.results"
          :key="vacancy.id"
          :vacancy="vacancy"
          :is-liked="applicationStore.likedVacancyIds.has(vacancy.id)"
          @like="handleLike"
        />
      </div>

      <p
        v-else-if="!searchStore.isLoading && searchStore.query"
        class="empty-text"
      >
        Ничего не найдено — попробуйте другой запрос
      </p>
    </div>

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
  margin-bottom: 16px;
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

.mode-panel {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  border-bottom: 1px solid #e5e4e7;
  padding-bottom: 12px;
}

.mode-button {
  padding: 10px 18px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: #fff;
  color: #1a1a1a;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.mode-button:hover {
  border-color: #4a6cf7;
  color: #4a6cf7;
}

.mode-button.active {
  background: #4a6cf7;
  border-color: #4a6cf7;
  color: #fff;
}

.recommendations-panel {
  margin-bottom: 24px;
}

.recommendations-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
  padding: 16px;
  background: #fafbfd;
  border: 1px solid #e5e4e7;
  border-radius: 14px;
}

.panel-title {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
}

.profile-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.profile-pill {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid #ddd;
  background: #fff;
  color: #555;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.profile-pill:hover {
  border-color: #4a6cf7;
  color: #4a6cf7;
}

.profile-pill.active {
  background: #4a6cf7;
  border-color: #4a6cf7;
  color: #fff;
}

.only-new-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #555;
  cursor: pointer;
  margin-left: auto;
}

.only-new-label input[type="checkbox"] {
  accent-color: #4a6cf7;
  width: 16px;
  height: 16px;
}

.sync-button {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #4a6cf7;
  background: #fff;
  color: #4a6cf7;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.sync-button:hover:not(:disabled) {
  background: #4a6cf7;
  color: #fff;
}

.sync-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

  .mode-panel {
    flex-direction: column;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  color: #666;
}

.empty-state p {
  margin: 0 0 16px 0;
}

.btn-primary {
  padding: 10px 20px;
  border-radius: 10px;
  border: none;
  background: #4a6cf7;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #3b5bdb;
}

.recommendations-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.mark-seen-button {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: transparent;
  color: #555;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.mark-seen-button:hover:not(:disabled) {
  background: #f4f5f7;
  border-color: #ccc;
  color: #1a1a1a;
}

.mark-seen-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-text {
  color: #e74c3c;
}

.empty-text {
  color: #888;
}
</style>
