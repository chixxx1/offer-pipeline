<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useProfileStore } from '../../stores/profile'

const props = defineProps({
  // Навыки могут прийти как массив строк ["python", "django"]
  // или как массив объектов [{ id, name }].
  skills: { type: Array, default: () => [] },
})

const emit = defineEmits(['update'])

const profileStore = useProfileStore()

const skillInput = ref('')
const skillSuggestions = ref([])
const showSuggestions = ref(false)
const isLoadingSkills = ref(false)

let suggestionsTimer = null

// Нормализуем навыки к единому виду { id, name }.
// Строки получают устойчивый id на основе названия.
const normalizedSkills = computed(() => {
  return (props.skills || []).map((s, index) => {
    if (typeof s === 'string') {
      return { id: `skill_${index}_${s}`, name: s }
    }
    return { id: s.id || `skill_${index}_${s.name}`, name: s.name }
  })
})

function normalizeSkillName(name) {
  return name.trim().toLowerCase().replace(/\s+/g, ' ')
}

// Синхронизируем выбранные ID с актуальным списком навыков из props.
const selectedSkillIds = computed(() => normalizedSkills.value.map(s => s.id))

async function fetchSuggestions(query) {
  if (suggestionsTimer) {
    clearTimeout(suggestionsTimer)
    suggestionsTimer = null
  }
  if (!query.trim()) {
    skillSuggestions.value = []
    showSuggestions.value = false
    return
  }
  // Debounce, чтобы не слать запрос на каждый символ ввода.
  suggestionsTimer = setTimeout(async () => {
    isLoadingSkills.value = true
    try {
      const data = await profileStore.fetchSkills(query)
      const existingNames = new Set(normalizedSkills.value.map(s => s.name.toLowerCase()))
      skillSuggestions.value = data.filter(
        (s) => !existingNames.has(s.name.toLowerCase())
      )
      showSuggestions.value = skillSuggestions.value.length > 0
    } catch (err) {
      skillSuggestions.value = []
      showSuggestions.value = false
    } finally {
      isLoadingSkills.value = false
    }
  }, 300)
}

function skillsAsNames() {
  return normalizedSkills.value.map((s) => s.name)
}

async function selectSuggestion(skill) {
  if (suggestionsTimer) {
    clearTimeout(suggestionsTimer)
    suggestionsTimer = null
  }
  const normalized = normalizeSkillName(skill.name)
  const exists = normalizedSkills.value.some(
    (s) => s.name.toLowerCase() === normalized
  )
  if (!exists) {
    const updatedSkills = [...normalizedSkills.value, skill]
    emit('update', updatedSkills)
    await profileStore.updateProfile({ skills: updatedSkills.map((s) => s.name) })
  }
  skillInput.value = ''
  showSuggestions.value = false
}

async function addCustomSkill() {
  if (suggestionsTimer) {
    clearTimeout(suggestionsTimer)
    suggestionsTimer = null
  }
  const normalized = normalizeSkillName(skillInput.value)
  if (!normalized) return

  const exists = normalizedSkills.value.some(
    (s) => s.name.toLowerCase() === normalized
  )
  if (exists) {
    skillInput.value = ''
    return
  }

  const newSkill = { id: `custom_${Date.now()}`, name: normalized }
  const updatedSkills = [...normalizedSkills.value, newSkill]
  emit('update', updatedSkills)
  await profileStore.updateProfile({ skills: updatedSkills.map((s) => s.name) })
  skillInput.value = ''
  showSuggestions.value = false
}

async function removeSkill(skillId) {
  if (suggestionsTimer) {
    clearTimeout(suggestionsTimer)
    suggestionsTimer = null
  }
  const updatedSkills = normalizedSkills.value.filter((s) => s.id !== skillId)
  emit('update', updatedSkills)
  await profileStore.updateProfile({ skills: updatedSkills.map((s) => s.name) })
}

function handleKeydown(e) {
  if (e.key === 'Enter') {
    e.preventDefault()
    if (showSuggestions.value && skillSuggestions.value.length > 0) {
      selectSuggestion(skillSuggestions.value[0])
    } else {
      addCustomSkill()
    }
  } else if (e.key === 'Escape') {
    showSuggestions.value = false
  }
}

function handleInputFocus() {
  if (skillInput.value.trim()) {
    fetchSuggestions(skillInput.value)
  }
}

function handleClickOutside(e) {
  if (!e.target.closest('.skills-input-wrapper')) {
    showSuggestions.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  if (suggestionsTimer) {
    clearTimeout(suggestionsTimer)
    suggestionsTimer = null
  }
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="profile-section">
    <p class="filter-title">Навыки</p>

    <div class="skills-tags">
      <span
        v-for="skill in normalizedSkills"
        :key="skill.id"
        class="skill-tag"
      >
        {{ skill.name }}
        <button
          type="button"
          class="skill-tag-remove"
          @click="removeSkill(skill.id)"
          aria-label="Удалить навык"
        >
          ✕
        </button>
      </span>
    </div>

    <div class="skills-input-wrapper" @keydown="handleKeydown">
      <input
        v-model="skillInput"
        type="text"
        placeholder="Введите навык и нажмите Enter..."
        class="form-input"
        @input="fetchSuggestions(skillInput)"
        @focus="handleInputFocus"
      />
      <span v-if="isLoadingSkills" class="loading-spinner"></span>

      <div v-if="showSuggestions && skillSuggestions.length > 0" class="suggestions-dropdown">
        <div
          v-for="skill in skillSuggestions"
          :key="skill.id"
          class="suggestion-item"
          @click="selectSuggestion(skill)"
        >
          {{ skill.name }}
        </div>
      </div>
    </div>

    <p class="skills-hint">Нажмите Enter для добавления навыка. Доступно автодополнение по существующим навыкам.</p>
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

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  min-height: 40px;
}

.skill-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #eef0f5;
  color: #333;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
}

.skill-tag-remove {
  border: none;
  background: transparent;
  color: #888;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  transition: all 0.2s;
}

.skill-tag-remove:hover {
  background: #fee2e2;
  color: #ef4444;
}

.skills-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.skills-input-wrapper .form-input {
  flex: 1;
  padding-right: 40px;
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

.loading-spinner {
  position: absolute;
  right: 12px;
  width: 18px;
  height: 18px;
  border: 2px solid #eef0f5;
  border-top-color: #4a6cf7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.suggestions-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 10px 12px;
  font-size: 14px;
  color: #1a1a1a;
  cursor: pointer;
  transition: background 0.15s;
}

.suggestion-item:hover {
  background: #f4f5f7;
}

.skills-hint {
  margin: 12px 0 0 0;
  font-size: 12px;
  color: #888;
}
</style>
