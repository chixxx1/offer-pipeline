<script setup>
import { ref, reactive } from 'vue'
import { useProfileStore } from '../../stores/profile'

const props = defineProps({
  experiences: { type: Array, default: () => [] },
})

const emit = defineEmits(['update'])

const profileStore = useProfileStore()

const showAddForm = ref(false)
const editingId = ref(null)
const form = reactive({
  company: '',
  position: '',
  start_date: '',
  end_date: '',
  is_current: false,
  description: '',
})
const formErrors = ref({})
const isSubmitting = ref(false)

function openAddForm() {
  editingId.value = null
  resetForm()
  showAddForm.value = true
}

function openEditForm(exp) {
  editingId.value = exp.id
  form.company = exp.company
  form.position = exp.position
  form.start_date = exp.start_date
  form.end_date = exp.end_date || ''
  form.is_current = exp.is_current
  form.description = exp.description || ''
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
  form.company = ''
  form.position = ''
  form.start_date = ''
  form.end_date = ''
  form.is_current = false
  form.description = ''
}

function validateForm() {
  formErrors.value = {}
  if (!form.company.trim()) formErrors.value.company = 'Укажите компанию'
  if (!form.position.trim()) formErrors.value.position = 'Укажите должность'
  if (!form.start_date) formErrors.value.start_date = 'Укажите дату начала'
  if (form.end_date && form.start_date && form.end_date < form.start_date && !form.is_current) {
    formErrors.value.end_date = 'Дата окончания не может быть раньше даты начала'
  }
  return Object.keys(formErrors.value).length === 0
}

async function handleSubmit() {
  if (!validateForm()) return
  
  isSubmitting.value = true
  try {
    const data = {
      company: form.company.trim(),
      position: form.position.trim(),
      start_date: form.start_date,
      end_date: form.is_current ? null : (form.end_date || null),
      is_current: form.is_current,
      description: form.description.trim(),
    }
    
    if (editingId.value) {
      await profileStore.updateWorkExperience(editingId.value, data)
    } else {
      await profileStore.createWorkExperience(data)
    }
    emit('update', profileStore.workExperiences)
    closeForm()
  } catch (err) {
    formErrors.value.submit = 'Не удалось сохранить'
  } finally {
    isSubmitting.value = false
  }
}

async function handleDelete(id) {
  if (!confirm('Удалить эту запись об опыте работы?')) return
  try {
    await profileStore.deleteWorkExperience(id)
    emit('update', profileStore.workExperiences)
  } catch (err) {
    alert('Не удалось удалить')
  }
}
</script>

<template>
  <div class="profile-section">
    <div class="section-header">
      <h3 class="section-title">Опыт работы</h3>
      <button class="btn btn-secondary" @click="openAddForm">
        + Добавить
      </button>
    </div>

    <div v-if="showAddForm" class="experience-form">
      <h4>{{ editingId ? 'Редактировать' : 'Добавить' }} опыт работы</h4>
      
      <div v-if="formErrors.submit" class="error-message">{{ formErrors.submit }}</div>

      <div class="form-grid">
        <div class="form-field">
          <label>Компания *</label>
          <input
            v-model="form.company"
            type="text"
            placeholder="Название компании"
            class="form-input"
            :class="{ error: formErrors.company }"
          />
          <span v-if="formErrors.company" class="field-error">{{ formErrors.company }}</span>
        </div>

        <div class="form-field">
          <label>Должность *</label>
          <input
            v-model="form.position"
            type="text"
            placeholder="Ваша должность"
            class="form-input"
            :class="{ error: formErrors.position }"
          />
          <span v-if="formErrors.position" class="field-error">{{ formErrors.position }}</span>
        </div>

        <div class="form-field">
          <label>Начало *</label>
          <input
            v-model="form.start_date"
            type="month"
            class="form-input"
            :class="{ error: formErrors.start_date }"
          />
          <span v-if="formErrors.start_date" class="field-error">{{ formErrors.start_date }}</span>
        </div>

        <div class="form-field">
          <label>Окончание</label>
          <input
            v-model="form.end_date"
            type="month"
            class="form-input"
            :disabled="form.is_current"
            :class="{ error: formErrors.end_date }"
          />
          <span v-if="formErrors.end_date" class="field-error">{{ formErrors.end_date }}</span>
        </div>

        <div class="form-field checkbox-field">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="form.is_current"
            />
            <span>Настоящее время</span>
          </label>
        </div>
      </div>

      <div class="form-field full-width">
        <label>Описание</label>
        <textarea
          v-model="form.description"
          rows="3"
          placeholder="Обязанности, достижения, технологии..."
          class="form-input"
        ></textarea>
      </div>

      <div class="form-actions">
        <button class="btn btn-secondary" @click="closeForm">Отмена</button>
        <button class="btn btn-primary" @click="handleSubmit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Сохранение...' : (editingId ? 'Сохранить изменения' : 'Добавить') }}
        </button>
      </div>
    </div>

    <div v-else class="experiences-list">
      <div
        v-for="exp in experiences"
        :key="exp.id"
        class="experience-card"
      >
        <div class="experience-header">
          <div>
            <p class="experience-position">{{ exp.position }}</p>
            <p class="experience-company">{{ exp.company }}</p>
          </div>
          <div class="experience-dates">
            <span class="date">{{ formatDate(exp.start_date) }}</span>
            <span>—</span>
            <span class="date">
              {{ exp.is_current ? 'Настоящее время' : formatDate(exp.end_date) }}
            </span>
          </div>
        </div>

        <p v-if="exp.description" class="experience-description">{{ exp.description }}</p>

        <div class="experience-actions">
          <button class="btn-text" @click="openEditForm(exp)">Редактировать</button>
          <button class="btn-text btn-danger" @click="handleDelete(exp.id)">Удалить</button>
        </div>
      </div>

      <p v-if="experiences.length === 0" class="empty-state">
        Опыт работы не добавлен. Нажмите «Добавить», чтобы создать первую запись.
      </p>
    </div>
  </div>
</template>

<script>
function formatDate(dateStr) {
  if (!dateStr) return ''
  const [year, month] = dateStr.split('-')
  const months = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
  return `${months[parseInt(month) - 1]} ${year}`
}
</script>

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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: #1a1a1a;
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

.experience-form {
  background: #ffffff;
  border: 1px solid #e5e4e7;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.experience-form h4 {
  margin: 0 0 16px 0;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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

.form-input.error {
  border-color: #ef4444;
}

.field-error {
  font-size: 12px;
  color: #ef4444;
}

.checkbox-field {
  margin-top: auto;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  accent-color: #4a6cf7;
  width: 16px;
  height: 16px;
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

.experiences-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.experience-card {
  background: #ffffff;
  border: 1px solid #e5e4e7;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.experience-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 8px;
}

.experience-position {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #1a1a1a;
}

.experience-company {
  font-size: 14px;
  color: #555;
  margin: 0;
}

.experience-dates {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #888;
  white-space: nowrap;
  flex-shrink: 0;
}

.date {
  font-weight: 500;
}

.experience-description {
  font-size: 13px;
  color: #555;
  line-height: 1.5;
  margin: 0 0 12px 0;
}

.experience-actions {
  display: flex;
  gap: 12px;
}

.empty-state {
  text-align: center;
  color: #888;
  padding: 32px;
  margin: 0;
  font-size: 14px;
}
</style>