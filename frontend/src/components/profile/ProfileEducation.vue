<script setup>
import { ref, reactive } from 'vue'
import { useProfileStore } from '../../stores/profile'

const props = defineProps({
  education: { type: Array, default: () => [] },
})

const emit = defineEmits(['update'])

const profileStore = useProfileStore()

const showAddForm = ref(false)
const editingId = ref(null)
const form = reactive({
  institution: '',
  degree: '',
  field_of_study: '',
  start_year: '',
  end_year: '',
})
const formErrors = ref({})
const isSubmitting = ref(false)

const currentYear = new Date().getFullYear()
const years = Array.from({ length: currentYear - 1950 + 1 }, (_, i) => currentYear - i)

function openAddForm() {
  editingId.value = null
  resetForm()
  showAddForm.value = true
}

function openEditForm(edu) {
  editingId.value = edu.id
  form.institution = edu.institution
  form.degree = edu.degree
  form.field_of_study = edu.field_of_study
  form.start_year = String(edu.start_year)
  form.end_year = edu.end_year ? String(edu.end_year) : ''
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
  form.institution = ''
  form.degree = ''
  form.field_of_study = ''
  form.start_year = ''
  form.end_year = ''
}

function validateForm() {
  formErrors.value = {}
  if (!form.institution.trim()) formErrors.value.institution = 'Укажите учебное заведение'
  if (!form.degree.trim()) formErrors.value.degree = 'Укажите степень/квалификацию'
  if (!form.field_of_study.trim()) formErrors.value.field_of_study = 'Укажите специальность'
  if (!form.start_year) formErrors.value.start_year = 'Укажите год начала'
  if (form.end_year && form.start_year && parseInt(form.end_year) < parseInt(form.start_year)) {
    formErrors.value.end_year = 'Год окончания не может быть раньше года начала'
  }
  return Object.keys(formErrors.value).length === 0
}

async function handleSubmit() {
  if (!validateForm()) return
  
  isSubmitting.value = true
  try {
    const data = {
      institution: form.institution.trim(),
      degree: form.degree.trim(),
      field_of_study: form.field_of_study.trim(),
      start_year: parseInt(form.start_year),
      end_year: form.end_year ? parseInt(form.end_year) : null,
    }
    
    if (editingId.value) {
      await profileStore.updateEducation(editingId.value, data)
    } else {
      await profileStore.createEducation(data)
    }
    emit('update', profileStore.education)
    closeForm()
  } catch (err) {
    formErrors.value.submit = 'Не удалось сохранить'
  } finally {
    isSubmitting.value = false
  }
}

async function handleDelete(id) {
  if (!confirm('Удалить эту запись об образовании?')) return
  try {
    await profileStore.deleteEducation(id)
    emit('update', profileStore.education)
  } catch (err) {
    alert('Не удалось удалить')
  }
}
</script>

<template>
  <div class="profile-section">
    <div class="section-header">
      <h3 class="section-title">Образование</h3>
      <button class="btn btn-secondary" @click="openAddForm">
        + Добавить
      </button>
    </div>

    <div v-if="showAddForm" class="education-form">
      <h4>{{ editingId ? 'Редактировать' : 'Добавить' }} образование</h4>
      
      <div v-if="formErrors.submit" class="error-message">{{ formErrors.submit }}</div>

      <div class="form-grid">
        <div class="form-field full-width">
          <label>Учебное заведение *</label>
          <input
            v-model="form.institution"
            type="text"
            placeholder="Например: МГУ, ВШЭ, МФТИ..."
            class="form-input"
            :class="{ error: formErrors.institution }"
          />
          <span v-if="formErrors.institution" class="field-error">{{ formErrors.institution }}</span>
        </div>

        <div class="form-field">
          <label>Степень / Квалификация *</label>
          <input
            v-model="form.degree"
            type="text"
            placeholder="Бакалавр, Магистр, Специалист..."
            class="form-input"
            :class="{ error: formErrors.degree }"
          />
          <span v-if="formErrors.degree" class="field-error">{{ formErrors.degree }}</span>
        </div>

        <div class="form-field full-width">
          <label>Специальность *</label>
          <input
            v-model="form.field_of_study"
            type="text"
            placeholder="Например: Программная инженерия, Экономика..."
            class="form-input"
            :class="{ error: formErrors.field_of_study }"
          />
          <span v-if="formErrors.field_of_study" class="field-error">{{ formErrors.field_of_study }}</span>
        </div>

        <div class="form-field">
          <label>Год начала *</label>
          <select
            v-model="form.start_year"
            class="form-input"
            :class="{ error: formErrors.start_year }"
          >
            <option value="">Выберите год</option>
            <option v-for="y in years" :key="y" :value="String(y)">{{ y }}</option>
          </select>
          <span v-if="formErrors.start_year" class="field-error">{{ formErrors.start_year }}</span>
        </div>

        <div class="form-field">
          <label>Год окончания</label>
          <select
            v-model="form.end_year"
            class="form-input"
          >
            <option value="">Выберите год</option>
            <option v-for="y in years" :key="y" :value="String(y)">{{ y }}</option>
          </select>
          <span v-if="formErrors.end_year" class="field-error">{{ formErrors.end_year }}</span>
        </div>
      </div>

      <div class="form-actions">
        <button class="btn btn-secondary" @click="closeForm">Отмена</button>
        <button class="btn btn-primary" @click="handleSubmit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Сохранение...' : (editingId ? 'Сохранить изменения' : 'Добавить') }}
        </button>
      </div>
    </div>

    <div v-else class="education-list">
      <div
        v-for="edu in education"
        :key="edu.id"
        class="education-card"
      >
        <div class="education-header">
          <div>
            <p class="education-degree">{{ edu.degree }}, {{ edu.field_of_study }}</p>
            <p class="education-institution">{{ edu.institution }}</p>
          </div>
          <div class="education-dates">
            <span class="date">{{ edu.start_year }}</span>
            <span>—</span>
            <span class="date">{{ edu.end_year || 'по н.в.' }}</span>
          </div>
        </div>

        <div class="education-actions">
          <button class="btn-text" @click="openEditForm(edu)">Редактировать</button>
          <button class="btn-text btn-danger" @click="handleDelete(edu.id)">Удалить</button>
        </div>
      </div>

      <p v-if="education.length === 0" class="empty-state">
        Образование не добавлено. Нажмите «Добавить», чтобы создать первую запись.
      </p>
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

.education-form {
  background: #ffffff;
  border: 1px solid #e5e4e7;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.education-form h4 {
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

.education-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.education-card {
  background: #ffffff;
  border: 1px solid #e5e4e7;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.education-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 8px;
}

.education-degree {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #1a1a1a;
}

.education-institution {
  font-size: 14px;
  color: #555;
  margin: 0;
}

.education-dates {
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

.education-actions {
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