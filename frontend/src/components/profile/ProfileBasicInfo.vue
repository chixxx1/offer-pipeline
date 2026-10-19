<script setup>
import { ref, watch } from 'vue'
import { useProfileStore } from '../../stores/profile'

const props = defineProps({
  profile: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update'])

const profileStore = useProfileStore()

const form = ref({
  city: '',
  desired_salary: '',
  work_format: 'any',
  about: '',
  github_url: '',
  linkedin_url: '',
  telegram: '',
  contact_email: '',
})

const workFormatOptions = [
  { value: 'any', label: 'Любой' },
  { value: 'remote', label: 'Удалённо' },
  { value: 'office', label: 'Офис' },
  { value: 'hybrid', label: 'Гибрид' },
]

const isSaving = ref(false)
const saveError = ref(null)

watch(
  () => props.profile,
  (newProfile) => {
    if (newProfile) {
      form.value = {
        city: newProfile.city || '',
        desired_salary: newProfile.desired_salary || '',
        work_format: newProfile.work_format || 'any',
        about: newProfile.about || '',
        github_url: newProfile.github_url || '',
        linkedin_url: newProfile.linkedin_url || '',
        telegram: newProfile.telegram || '',
        contact_email: newProfile.contact_email || '',
      }
    }
  },
  { immediate: true },
)

async function handleSave() {
  isSaving.value = true
  saveError.value = null
  try {
    const data = { ...form.value }
    if (data.desired_salary === '') data.desired_salary = null
    else data.desired_salary = Number(data.desired_salary)
    await profileStore.updateProfile(data)
    emit('update', profileStore.profile)
  } catch (err) {
    saveError.value = 'Не удалось сохранить изменения'
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div class="profile-section">
    <p class="filter-title">Основная информация</p>

    <div v-if="saveError" class="error-message">{{ saveError }}</div>

    <div class="form-grid">
      <div class="form-field">
        <label for="city">Город</label>
        <input
          id="city"
          v-model="form.city"
          type="text"
          placeholder="Например: Москва"
          class="form-input"
        />
      </div>

      <div class="form-field">
        <label for="desired_salary">Желаемая зарплата (₽)</label>
        <input
          id="desired_salary"
          v-model="form.desired_salary"
          type="number"
          min="0"
          step="1000"
          placeholder="Например: 150000"
          class="form-input"
        />
      </div>

      <div class="form-field">
        <label for="work_format">Формат работы</label>
        <div class="work-format-pills" role="radiogroup">
          <button
            v-for="opt in workFormatOptions"
            :key="opt.value"
            type="button"
            class="format-pill"
            :class="{ active: form.work_format === opt.value }"
            @click="form.work_format = opt.value"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>
    </div>

    <div class="form-field full-width">
      <label for="about">О себе</label>
      <textarea
        id="about"
        v-model="form.about"
        rows="4"
        placeholder="Расскажите о себе, своих навыках и опыте..."
        class="form-input"
      ></textarea>
    </div>

    <p class="filter-title">Контакты</p>
    <div class="form-grid">
      <div class="form-field">
        <label for="github_url">GitHub</label>
        <input
          id="github_url"
          v-model="form.github_url"
          type="url"
          placeholder="https://github.com/username"
          class="form-input"
        />
      </div>

      <div class="form-field">
        <label for="linkedin_url">LinkedIn</label>
        <input
          id="linkedin_url"
          v-model="form.linkedin_url"
          type="url"
          placeholder="https://linkedin.com/in/username"
          class="form-input"
        />
      </div>

      <div class="form-field">
        <label for="telegram">Telegram</label>
        <input
          id="telegram"
          v-model="form.telegram"
          type="text"
          placeholder="@username"
          class="form-input"
        />
      </div>

      <div class="form-field">
        <label for="contact_email">Email для связи</label>
        <input
          id="contact_email"
          v-model="form.contact_email"
          type="email"
          placeholder="email@example.com"
          class="form-input"
        />
      </div>
    </div>

    <button
      class="btn btn-primary"
      @click="handleSave"
      :disabled="isSaving"
    >
      {{ isSaving ? 'Сохранение...' : 'Сохранить' }}
    </button>
  </div>
</template>

<style scoped>
.profile-section {
  background: #ffffff;
  border: 1px solid #e5e4e7;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.filter-title {
  font-size: 13px;
  font-weight: 600;
  color: #888;
  margin: 0 0 12px 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.form-field label {
  font-size: 13px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-input {
  padding: 12px 14px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 14px;
  color: #1a1a1a;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.1);
}

.form-input::placeholder {
  color: #999;
}

.work-format-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.format-pill {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid #ddd;
  background: #fff;
  color: #555;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.format-pill:hover {
  border-color: #4a6cf7;
  color: #4a6cf7;
}

.format-pill.active {
  background: #4a6cf7;
  border-color: #4a6cf7;
  color: #fff;
  box-shadow: 0 2px 8px rgba(74, 108, 247, 0.3);
}

.error-message {
  background: #fee2e2;
  color: #ef4444;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 13px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.btn-primary {
  background: #4a6cf7;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #3b5bdb;
}

.btn-primary:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-primary:disabled {
  background: #a5b4fc;
  cursor: not-allowed;
}
</style>