<script setup>
import { ref, watch } from 'vue'
import { useApplicationStore } from '../stores/applications'

const props = defineProps({
  application: { type: Object, default: null },
})
const emit = defineEmits(['close'])

const applicationStore = useApplicationStore()
const notesDraft = ref('')
const isSaving = ref(false)

watch(() => props.application, (app) => {
  notesDraft.value = app ? app.notes : ''
})

async function handleSaveNotes() {
  isSaving.value = true
  await applicationStore.updateNotes(props.application.id, notesDraft.value)
  isSaving.value = false
}
</script>

<template>
  <div v-if="application" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <button class="modal-close" @click="emit('close')">✕</button>

      <h2>{{ application.vacancy.title }}</h2>
      <p class="modal-company">{{ application.vacancy.company }}</p>

      <a :href="application.vacancy.url" target="_blank" class="modal-link">
        Открыть на hh.ru →
      </a>

      <div class="modal-notes">
        <label class="modal-notes-label">Заметка</label>
        <textarea
          v-model="notesDraft"
          class="modal-notes-textarea"
          rows="5"
          placeholder="Например: связаться с HR через неделю"
        ></textarea>
        <button class="modal-notes-save" :disabled="isSaving" @click="handleSaveNotes">
          {{ isSaving ? 'Сохраняем...' : 'Сохранить заметку' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  padding: 28px;
  max-width: 480px;
  width: 100%;
  position: relative;
  color: #1a1a1a;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  border: none;
  background: transparent;
  font-size: 18px;
  cursor: pointer;
}

.modal-company {
  color: #666;
  margin-top: -8px;
}

.modal-link {
  display: inline-block;
  margin-top: 8px;
  color: #2563eb;
  text-decoration: none;
  font-size: 14px;
}

.modal-notes {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.modal-notes-label {
  font-size: 13px;
  color: #888;
}

.modal-notes-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}

.modal-notes-save {
  align-self: flex-start;
  background: #2563eb;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
}

.modal-notes-save:disabled {
  opacity: 0.6;
}
</style>