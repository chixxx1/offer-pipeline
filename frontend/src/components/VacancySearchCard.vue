<script setup>
import { ref } from 'vue'
import axios from 'axios'
import {
  formatExperience,
  formatWorkFormat,
  formatEmployment,
  formatSalary,
  formatPublishedAt,
} from '../utils/vacancyFormatters'

const props = defineProps({
  vacancy: { type: Object, required: true },
  isLiked: { type: Boolean, default: false },
  match: { type: Number, default: null },
  isNew: { type: Boolean, default: false },
  matchedSkills: { type: Array, default: () => [] },
  missingSkills: { type: Array, default: () => [] },
  isRecommendation: { type: Boolean, default: false },
  recommendationId: { type: Number, default: null },
  onDismiss: { type: Function, default: null },
})

const emit = defineEmits(['like'])

const fullDescription = ref('')
const isLoadingFull = ref(false)
const showFullDescription = ref(false)

async function loadFullDescription() {
  if (fullDescription.value) {
    showFullDescription.value = !showFullDescription.value
    return
  }

  isLoadingFull.value = true
  try {
    const response = await axios.get(`/api/vacancies/${props.vacancy.id}/full-description/`)
    fullDescription.value = response.data.full_description || 'Описание недоступно'
    showFullDescription.value = true
  } catch (err) {
    console.error('Не удалось загрузить подробное описание', err)
  } finally {
    isLoadingFull.value = false
  }
}

function handleDismiss() {
  if (props.onDismiss && props.recommendationId != null) {
    props.onDismiss(props.recommendationId)
  }
}
</script>

<template>
  <div class="vacancy-card" :class="{ recommendation: isRecommendation }">
    <div class="card-header">
      <h3 class="card-title">{{ vacancy.title }}</h3>
      <button
        class="like-button"
        :class="{ liked: isLiked }"
        :title="isLiked ? 'Удалить из отслеживаемых' : 'Добавить в отслеживаемые'"
        @click="emit('like', vacancy)"
        aria-label="Переключить статус отслеживания"
      >
      {{ isLiked ? '♥' : '♡' }}
      </button>

      <span v-if="match !== null" class="match-badge">{{ match }}%</span>

      <span v-if="isNew" class="new-badge">Новая</span>
    </div>

    <div class="card-meta-row">
      <span v-if="formatSalary(vacancy.salary_from, vacancy.salary_to)" class="card-salary">
        {{ formatSalary(vacancy.salary_from, vacancy.salary_to) }}
      </span>

      <span v-if="vacancy.published_at" class="card-published">
        {{ formatPublishedAt(vacancy.published_at) }}
      </span>

      <span v-if="vacancy.experience" class="tag">{{ formatExperience(vacancy.experience) }}</span>
      <span v-if="vacancy.work_format" class="tag">{{ formatWorkFormat(vacancy.work_format) }}</span>
      <span v-if="vacancy.employment" class="tag">{{ formatEmployment(vacancy.employment) }}</span>
    </div>

    <p class="card-company">{{ vacancy.company }}</p>
    <p v-if="vacancy.location" class="card-location">{{ vacancy.location }}</p>

    <div v-if="matchedSkills.length || missingSkills.length" class="card-skills">
      <span v-for="skill in matchedSkills" :key="`matched-${skill}`" class="skill-tag matched">
        {{ skill }}
      </span>
      <span v-for="skill in missingSkills" :key="`missing-${skill}`" class="skill-tag missing">
        {{ skill }}
      </span>
    </div>

    <p v-if="vacancy.description" class="card-description">{{ vacancy.description }}</p>

    <div v-if="showFullDescription" class="card-full-description" v-html="fullDescription"></div>

    <button
      class="show-description-button"
      :disabled="isLoadingFull"
      @click="loadFullDescription"
    >
      {{ isLoadingFull ? 'Загружаем...' : (showFullDescription ? 'Скрыть подробности' : 'Показать подробности') }}
    </button>

    <button v-if="isRecommendation && onDismiss" class="dismiss-button" @click="handleDismiss">
      Скрыть
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

.vacancy-card.recommendation {
  border-color: #e2e8f0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  flex-wrap: wrap;
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

.match-badge {
  font-size: 12px;
  font-weight: 700;
  color: #1a1a1a;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  padding: 4px 10px;
  border-radius: 999px;
  white-space: nowrap;
  margin-left: 8px;
}

.new-badge {
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  background: #10b981;
  padding: 2px 8px;
  border-radius: 999px;
  white-space: nowrap;
  margin-left: 6px;
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

.card-published {
  font-size: 13px;
  color: #666;
  background: #f2f3f5;
  padding: 3px 8px;
  border-radius: 6px;
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

.card-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 6px 0 0 0;
}

.skill-tag {
  font-size: 12px;
  font-weight: 500;
  padding: 3px 8px;
  border-radius: 6px;
  white-space: nowrap;
}

.skill-tag.matched {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #86efac;
}

.skill-tag.missing {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
  opacity: 0.9;
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

.dismiss-button {
  background: transparent;
  border: 1px solid #ddd;
  color: #555;
  font-size: 13px;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 8px;
  cursor: pointer;
  align-self: flex-start;
  margin-top: 4px;
}

.dismiss-button:hover {
  background: #f4f5f7;
  border-color: #ccc;
  color: #1a1a1a;
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

.card-full-description {
  font-size: 13px;
  color: #333;
  line-height: 1.6;
  margin-top: 8px;
  max-height: 300px;
  overflow-y: auto;
  padding-top: 8px;
  border-top: 1px solid #eee;
}

.card-full-description :deep(ul) {
  padding-left: 20px;
}
</style>
