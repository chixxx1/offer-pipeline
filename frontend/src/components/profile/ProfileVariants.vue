<script setup>
import { ref, reactive, computed } from 'vue'
import { useProfileStore } from '../../stores/profile'

const props = defineProps({
  variants: { type: Array, default: () => [] },
  allSkills: { type: Array, default: () => [] },
  allExperiences: { type: Array, default: () => [] },
})

const emit = defineEmits(['update'])

const profileStore = useProfileStore()

const activeTab = ref(0)
const showAddForm = ref(false)
const editingId = ref(null)
const form = reactive({
  title: '',
  about: '',
  skills: [],
  experience_ids: [],
})
const formErrors = ref({})
const isSubmitting = ref(false)

const skillOptions = computed(() => props.allSkills.map(s => ({ id: s.id, name: s.name })))
const experienceOptions = computed(() => (props.allExperiences || []).map(e => ({
  id: e.id,
  label: `${e.position || ''} в ${e.company || ''} (${formatDate(e.start_date)}${e.is_current ? ' — наст.вр.' : ` — ${formatDate(e.end_date)}`})`,
})))

function formatDate(dateStr) {
  if (!dateStr) return ''
  const [year, month] = dateStr.split('-')
  const months = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
  return `${months[parseInt(month) - 1]} ${year}`
}

function openAddForm() {
  editingId.value = null
  resetForm()
  showAddForm.value = true
}

function openEditForm(variant) {
  editingId.value = variant.id
  form.title = variant.title
  form.about = variant.about || ''
  form.skills = (variant.skills || []).map(s => s.id)
  form.experience_ids = variant.experience_ids || []
  showAddForm.value = true
  formErrors.value = {}
}

function closeForm() {
  showAddForm.value = false
  editingId.value = null
  resetForm()
  formErrors.value = {}
}

function resetForm() {
  form.title = ''
  form.about = ''
  form.skills = []
  form.experience_ids = []
}

function validateForm() {
  formErrors.value = {}
  if (!form.title.trim()) formErrors.value.title = 'Укажите название варианта'
  return Object.keys(formErrors.value).length === 0
}

function toggleSkill(skillId) {
  const idx = form.skills.indexOf(skillId)
  if (idx === -1) form.skills.push(skillId)
  else form.skills.splice(idx, 1)
}

function toggleExperience(expId) {
  const idx = form.experience_ids.indexOf(expId)
  if (idx === -1) form.experience_ids.push(expId)
  else form.experience_ids.splice(idx, 1)
}

async function handleSubmit() {
  if (!validateForm()) return

  isSubmitting.value = true
  try {
    const data = {
      title: form.title.trim(),
      about: form.about.trim(),
      skills: form.skills,
      experience_ids: form.experience_ids,
    }

    if (editingId.value) {
      await profileStore.updateVariant(editingId.value, data)
    } else {
      await profileStore.createVariant(data)
    }
    emit('update', profileStore.variants)
    closeForm()
  } catch (err) {
    formErrors.value.submit = 'Не удалось сохранить вариант'
  } finally {
    isSubmitting.value = false
  }
}

async function handleDelete(id) {
  if (!confirm('Удалить этот вариант профиля?')) return
  try {
    await profileStore.deleteVariant(id)
    emit('update', profileStore.variants)
    if (activeTab.value >= profileStore.variants.length) {
      activeTab.value = Math.max(0, profileStore.variants.length - 1)
    }
  } catch (err) {
    alert('Не удалось удалить')
  }
}
</script>

<template>
  <div class="profile-section">
    <p class="filter-title">Варианты профиля</p>

    <p class="variants-description">
      Создайте специализированные версии профиля под разные направления.
      Базовый профиль используется по умолчанию.
    </p>

    <div v-if="showAddForm" class="variant-form">
      <h4>{{ editingId ? 'Редактировать вариант' : 'Создать новый вариант' }}</h4>

      <div v-if="formErrors.submit" class="error-message">{{ formErrors.submit }}</div>

      <div class="form-field">
        <label>Название варианта *</label>
        <input
          v-model="form.title"
          type="text"
          placeholder="Например: Frontend-разработчик, Data Scientist..."
          class="form-input"
          :class="{ error: formErrors.title }"
        />
        <span v-if="formErrors.title" class="field-error">{{ formErrors.title }}</span>
      </div>

      <div class="form-field full-width">
        <label>О себе (для этого варианта)</label>
        <textarea
          v-model="form.about"
          rows="3"
          placeholder="Адаптированное описание под это направление..."
          class="form-input"
        ></textarea>
      </div>

      <div class="form-field full-width">
        <label>Навыки</label>
        <div class="checkbox-group">
          <label v-for="skill in skillOptions" :key="skill.id" class="checkbox-item">
            <input
              type="checkbox"
              :checked="form.skills.includes(skill.id)"
              @change="toggleSkill(skill.id)"
            />
            {{ skill.name }}
          </label>
        </div>
        <p v-if="skillOptions.length === 0" class="empty-hint">Добавьте навыки в основном профиле</p>
      </div>

      <div class="form-field full-width">
        <label>Опыт работы</label>
        <div class="checkbox-group">
          <label v-for="exp in experienceOptions" :key="exp.id" class="checkbox-item">
            <input
              type="checkbox"
              :checked="form.experience_ids.includes(exp.id)"
              @change="toggleExperience(exp.id)"
            />
            {{ exp.label }}
          </label>
        </div>
        <p v-if="experienceOptions.length === 0" class="empty-hint">Добавьте опыт работы в основном профиле</p>
      </div>

      <div class="form-actions">
        <button class="btn btn-secondary" @click="closeForm">Отмена</button>
        <button class="btn btn-primary" @click="handleSubmit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Сохранение...' : (editingId ? 'Сохранить изменения' : 'Создать') }}
        </button>
      </div>
    </div>

    <div v-else class="variants-list">
      <div v-if="variants.length > 0">
        <div class="variant-card">
          <h4>{{ variants[activeTab]?.title || '' }}</h4>
          <p v-if="variants[activeTab]?.about" class="variant-about">{{ variants[activeTab].about }}</p>

          <div class="variant-section">
            <strong>Навыки:</strong>
            <div class="skills-tags">
              <span
                v-for="skill in (variants[activeTab]?.skills || [])"
                :key="skill.id"
                class="skill-tag"
              >
                {{ skill.name }}
              </span>
              <span v-if="!(variants[activeTab]?.skills || []).length" class="empty-tag">не выбрано</span>
            </div>
          </div>

          <div class="variant-section">
            <strong>Опыт работы:</strong>
            <ul class="experience-list">
              <li
                v-for="expId in (variants[activeTab]?.experience_ids || [])"
                :key="expId"
                class="experience-item"
              >
                {{ (props.allExperiences || []).find(e => e.id === expId)?.position }} в {{ (props.allExperiences || []).find(e => e.id === expId)?.company }}
              </li>
              <li v-if="!(variants[activeTab]?.experience_ids || []).length" class="empty-item">не выбрано</li>
            </ul>
          </div>

          <div class="variant-actions">
            <button class="btn-text" @click="openEditForm(variants[activeTab])">Редактировать</button>
            <button class="btn-text btn-danger" @click="handleDelete(variants[activeTab]?.id)">Удалить</button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <p>Вариантов профиля нет.</p>
        <button class="btn btn-primary" @click="openAddForm">Создать первый вариант</button>
      </div>
    </div>
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

.variants-description {
  font-size: 13px;
  color: #888;
  margin: 0 0 20px 0;
}

.variant-form {
  background: #ffffff;
  border: 1px solid #e5e4e7;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.variant-form h4 {
  margin: 0 0 16px 0;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.form-field.full-width {
  /* full width by default */
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

.form-input.error {
  border-color: #ef4444;
}

.field-error {
  font-size: 12px;
  color: #ef4444;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.checkbox-item:hover {
  border-color: #4a6cf7;
  color: #4a6cf7;
}

.checkbox-item input[type="checkbox"] {
  accent-color: #4a6cf7;
}

.empty-hint {
  font-size: 12px;
  color: #999;
  margin: 8px 0 0 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.error-message {
  background: #fee2e2;
  color: #ef4444;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 13px;
}

.variant-card {
  background: #ffffff;
  border: 1px solid #e5e4e7;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.variant-card h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.variant-about {
  font-size: 14px;
  color: #555;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.variant-section {
  margin-bottom: 16px;
}

.variant-section strong {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.skill-tag {
  background: #eef0f5;
  color: #333;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
}

.empty-tag, .empty-item {
  font-size: 13px;
  color: #999;
  font-style: italic;
}

.experience-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.experience-item {
  font-size: 13px;
  color: #555;
  padding: 4px 0;
}

.variant-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e5e4e7;
}

.btn-text {
  background: transparent;
  border: none;
  color: #4a6cf7;
  padding: 4px 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.btn-text:hover {
  text-decoration: underline;
}

.btn-danger {
  color: #ef4444;
}

.btn-danger:hover {
  color: #dc2626;
}

.empty-state {
  text-align: center;
  color: #888;
  padding: 40px 20px;
}

.empty-state p {
  margin: 0 0 16px 0;
  font-size: 14px;
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

.btn-secondary {
  background: transparent;
  border: 1px solid #ddd;
  color: #555;
  border-radius: 10px;
}

.btn-secondary:hover {
  background: #f4f5f7;
  color: #1a1a1a;
  border-color: #ccc;
}
</style>