<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { formatExperience, formatWorkFormat, formatEmployment, formatSalary } from '../utils/vacancyFormatters'

const props = defineProps({
  vacancy: { type: Object, required: true },
  isLiked: { type: Boolean, default: false },
})

const emit = defineEmits(['like'])

const description = ref('')
const isLoadingDescription = ref(false)
const descriptionError = ref(false)

async function loadDescription() {
  isLoadingDescription.value = true
  descriptionError.value = false
  try {
    const response = await axios.get(`/api/vacancies/${props.vacancy.id}/description/`)
    description.value = response.data.description || 'Описание недоступно'
  } catch (err) {
    descriptionError.value = true
    console.error('Не удалось загрузить описание', err)
  } finally {
    isLoadingDescription.value = false
  }
}
</script>

<template>
  <div class="vacancy-card">
    <div class="card-header">
      <h3 class="card-title">{{ vacancy.title }}</h3>
      <button
        class="like-button"
        :class="{ liked: isLiked }"
        :disabled="isLiked"
        @click="emit('like', vacancy)"
        aria-label="Добавить в отслеживаемые"
      >
        {{ isLiked ? '♥' : '♡' }}
      </button>
    </div>

    <div class="card-meta-row">
      <span v-if="formatSalary(vacancy.salary_from, vacancy.salary_to)" class="card-salary">
        {{ formatSalary(vacancy.salary_from, vacancy.salary_to) }}
      </span>

      <span v-if="vacancy.experience" class="tag">{{ formatExperience(vacancy.experience) }}</span>
      <span v-if="vacancy.work_format" class="tag">{{ formatWorkFormat(vacancy.work_format) }}</span>
      <span v-if="vacancy.employment" class="tag">{{ formatEmployment(vacancy.employment) }}</span>
    </div>

    <p class="card-company">{{ vacancy.company }}</p>
    <p v-if="vacancy.location" class="card-location">{{ vacancy.location }}</p>

    <p v-if="description" class="card-description">{{ description }}</p>
    <p v-else-if="descriptionError" class="card-description-error">Не удалось загрузить описание</p>
    <button
      v-else
      class="show-description-button"
      :disabled="isLoadingDescription"
      @click="loadDescription"
    >
      {{ isLoadingDescription ? 'Загружаем...' : 'Показать описание' }}
    </button>

    <a :href="vacancy.url" target="_blank" class="card-apply-button">
      Открыть на hh.ru →
    </a>
  </div>
</template>

<style scoped>
.vacancy-card {
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: #1a1a1a;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  line-height: 1.3;
}

.like-button {
  border: none;
  background: transparent;
  color: #999;
  font-size: 20px;
  cursor: pointer;
  flex-shrink: 0;
  line-height: 1;
  padding: 4px;
}

.like-button.liked {
  color: #e74c3c;
  cursor: default;
}

.card-meta-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.card-salary {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
}

.tag {
  background: #f2f3f5;
  color: #555;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  white-space: nowrap;
}

.card-company {
  font-size: 14px;
  color: #333;
  margin: 4px 0 0 0;
  font-weight: 500;
}

.card-location {
  font-size: 13px;
  color: #888;
  margin: 0;
}

.card-description {
  font-size: 13px;
  color: #555;
  line-height: 1.5;
  margin: 4px 0 0 0;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-description-error {
  font-size: 13px;
  color: #e74c3c;
  margin: 4px 0 0 0;
}

.show-description-button {
  background: transparent;
  border: none;
  color: #2563eb;
  font-size: 13px;
  cursor: pointer;
  padding: 0;
  text-align: left;
  align-self: flex-start;
}

.show-description-button:disabled {
  color: #999;
  cursor: default;
}

.card-apply-button {
  margin-top: 8px;
  align-self: flex-start;
  background: #2563eb;
  color: #fff;
  text-decoration: none;
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
}

.card-apply-button:hover {
  background: #1d4ed8;
}
</style>