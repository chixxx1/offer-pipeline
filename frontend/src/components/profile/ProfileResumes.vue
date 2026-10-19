<script setup>
import { ref } from 'vue'
import { useProfileStore } from '../../stores/profile'

const props = defineProps({
  resumeFiles: { type: Array, default: () => [] },
  variants: { type: Array, default: () => [] },
})

const emit = defineEmits(['update'])

const profileStore = useProfileStore()

const showUploadForm = ref(false)
const selectedVariantId = ref(null)
const uploadFile = ref(null)
const uploadError = ref(null)
const isUploading = ref(false)
const uploadingFileName = ref('')

function triggerFileInput() {
  document.getElementById('resume-file-input').click()
}

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (!file) return

  const ext = file.name.toLowerCase().split('.').pop()
  if (!['pdf', 'docx'].includes(ext)) {
    uploadError.value = 'Разрешены только файлы .pdf и .docx'
    e.target.value = ''
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    uploadError.value = 'Размер файла не должен превышать 10 МБ'
    e.target.value = ''
    return
  }

  uploadFile.value = file
  uploadError.value = null
  showUploadForm.value = true
  e.target.value = ''
}

function clearFile() {
  uploadFile.value = null
  uploadError.value = null
}

async function handleUpload() {
  if (!uploadFile.value) return

  isUploading.value = true
  uploadingFileName.value = uploadFile.value.name
  uploadError.value = null

  try {
    await profileStore.uploadResume(uploadFile.value, selectedVariantId.value || null)
    emit('update', profileStore.resumeFiles)
    clearFile()
    showUploadForm.value = false
    selectedVariantId.value = null
  } catch (err) {
    if (err.response?.data?.file) {
      uploadError.value = err.response.data.file[0]
    } else if (err.response?.data?.variant) {
      uploadError.value = err.response.data.variant[0]
    } else {
      uploadError.value = 'Не удалось загрузить файл'
    }
  } finally {
    isUploading.value = false
    uploadingFileName.value = ''
  }
}

async function handleDownload(id) {
  try {
    await profileStore.downloadResumeFile(id)
  } catch (err) {
    alert('Не удалось скачать файл')
  }
}

async function handleDelete(id) {
  if (!confirm('Удалить этот файл резюме?')) return
  try {
    await profileStore.deleteResumeFile(id)
    emit('update', profileStore.resumeFiles)
  } catch (err) {
    alert('Не удалось удалить')
  }
}

function getFileIcon(fileName) {
  const ext = fileName.toLowerCase().split('.').pop()
  return ext === 'pdf' ? 'PDF' : 'DOCX'
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' Б'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' КБ'
  return (bytes / (1024 * 1024)).toFixed(1) + ' МБ'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function getVariantTitle(variantId) {
  if (!variantId) return 'Базовый профиль'
  const variant = props.variants.find(v => v.id === variantId)
  return variant ? variant.title : 'Неизвестный вариант'
}
</script>

<template>
  <div class="profile-section">
    <div class="section-header">
      <p class="filter-title">Файлы резюме</p>
      <button class="btn btn-primary" @click="triggerFileInput">
        + Загрузить резюме
      </button>
      <input
        id="resume-file-input"
        type="file"
        accept=".pdf,.docx"
        @change="handleFileSelect"
        style="display: none"
      />
    </div>

    <div v-if="showUploadForm" class="upload-form">
      <h4>Загрузка резюме</h4>

      <div v-if="uploadError" class="error-message">{{ uploadError }}</div>

      <div class="form-field">
        <label>Файл</label>
        <div class="selected-file">
          <span class="file-icon">{{ getFileIcon(uploadFile?.name || '') }}</span>
          <span class="file-name">{{ uploadFile?.name }}</span>
          <span class="file-size">{{ uploadFile ? formatFileSize(uploadFile.size) : '' }}</span>
          <button type="button" class="file-remove" @click="clearFile" :disabled="isUploading">Удалить</button>
        </div>
      </div>

      <div class="form-field">
        <label>Привязать к варианту профиля</label>
        <select
          v-model="selectedVariantId"
          class="form-input"
        >
          <option value="">Базовый профиль</option>
          <option v-for="v in variants" :key="v.id" :value="v.id">{{ v.title }}</option>
        </select>
      </div>

      <div class="form-actions">
        <button class="btn btn-secondary" @click="clearFile" :disabled="isUploading">Отмена</button>
        <button class="btn btn-primary" @click="handleUpload" :disabled="isUploading || !uploadFile">
          {{ isUploading ? 'Загрузка...' : 'Загрузить' }}
        </button>
      </div>
    </div>

    <div class="resumes-list">
      <div
        v-for="resume in resumeFiles"
        :key="resume.id"
        class="resume-card"
      >
        <div class="resume-info">
          <span class="resume-icon">{{ getFileIcon(resume.original_name) }}</span>
          <div class="resume-details">
            <p class="resume-name">{{ resume.original_name }}</p>
            <p class="resume-meta">
              {{ formatFileSize(resume.file?.size || 0) }} • {{ formatDate(resume.uploaded_at) }} • {{ getVariantTitle(resume.variant) }}
            </p>
          </div>
        </div>

        <div class="resume-actions">
          <button class="btn-text" @click="handleDownload(resume.id)" title="Скачать">
            Скачать
          </button>
          <button class="btn-text btn-danger" @click="handleDelete(resume.id)" title="Удалить">
            Удалить
          </button>
        </div>
      </div>

      <p v-if="resumeFiles.length === 0 && !showUploadForm" class="empty-state">
        Файлов резюме нет. Нажмите «Загрузить резюме», чтобы добавить первый файл.
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
  flex-wrap: wrap;
  gap: 12px;
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
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.2s;
}

.btn-text:hover {
  background: #f0f4ff;
}

.btn-danger {
  color: #ef4444;
}

.btn-danger:hover {
  background: #fee2e2;
  color: #dc2626;
}

.upload-form {
  background: #ffffff;
  border: 1px solid #e5e4e7;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.upload-form h4 {
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

.selected-file {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.file-icon {
  font-size: 16px;
  color: #1a1a1a;
  font-weight: 600;
}

.file-name {
  flex: 1;
  font-size: 14px;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 13px;
  color: #888;
}

.file-remove {
  border: none;
  background: transparent;
  color: #888;
  font-size: 14px;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
  border-radius: 4px;
  transition: all 0.2s;
}

.file-remove:hover:not(:disabled) {
  background: #fee2e2;
  color: #ef4444;
}

.file-remove:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.resumes-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resume-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #ffffff;
  border: 1px solid #e5e4e7;
  border-radius: 12px;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.resume-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.resume-icon {
  font-size: 16px;
  color: #1a1a1a;
  font-weight: 600;
  flex-shrink: 0;
}

.resume-details {
  min-width: 0;
}

.resume-name {
  font-size: 15px;
  font-weight: 500;
  color: #1a1a1a;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.resume-meta {
  font-size: 12px;
  color: #888;
  margin: 0;
}

.resume-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  color: #888;
  padding: 40px 20px;
  margin: 0;
  font-size: 14px;
}
</style>