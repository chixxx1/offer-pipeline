<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useProfileStore } from '../../stores/profile'

const props = defineProps({
  skills: { type: Array, default: () => [] },
})

const emit = defineEmits(['update'])

const profileStore = useProfileStore()

const skillInput = ref('')
const skillSuggestions = ref([])
const showSuggestions = ref(false)
const selectedSkillIds = ref([])
const isLoadingSkills = ref(false)

function normalizeSkillName(name) {
  return name.trim().toLowerCase().replace(/\s+/g, ' ')
}

async function fetchSuggestions(query) {
  if (!query.trim()) {
    skillSuggestions.value = []
    showSuggestions.value = false
    return
  }
  isLoadingSkills.value = true
  try {
    const data = await profileStore.fetchSkills(query)
    skillSuggestions.value = data.filter(s =>
      !props.skills.some(existing => existing.name.toLowerCase() === s.name.toLowerCase()) &&
      !selectedSkillIds.value.includes(s.id)
    )
    showSuggestions.value = skillSuggestions.value.length > 0
  } catch (err) {
    skillSuggestions.value = []
    showSuggestions.value = false
  } finally {
    isLoadingSkills.value = false
  }
}

function selectSuggestion(skill) {
  const normalized = normalizeSkillName(skill.name)
  if (!props.skills.some(s => s.name.toLowerCase() === normalized) &&
      !selectedSkillIds.value.includes(skill.id)) {
    selectedSkillIds.value.push(skill.id)
    const updatedSkills = [...props.skills, skill]
    emit('update', updatedSkills)
    profileStore.updateProfile({ skills: updatedSkills.map(s => s.name) })
  }
  skillInput.value = ''
  showSuggestions.value = false
}

function addCustomSkill() {
  const normalized = normalizeSkillName(skillInput.value)
  if (!normalized) return

  if (props.skills.some(s => s.name.toLowerCase() === normalized)) {
    skillInput.value = ''
    return
  }

  const tempId = `temp_${Date.now()}`
  const newSkill = { id: tempId, name: normalized, slug: normalized }
  selectedSkillIds.value.push(tempId)
  const updatedSkills = [...props.skills, newSkill]
  emit('update', updatedSkills)
  profileStore.updateProfile({ skills: updatedSkills.map(s => s.name) })
  skillInput.value = ''
  showSuggestions.value = false
}

function removeSkill(skillId) {
  selectedSkillIds.value = selectedSkillIds.value.filter(id => id !== skillId)
  const updatedSkills = props.skills.filter(s => s.id !== skillId)
  emit('update', updatedSkills)
  profileStore.updateProfile({ skills: updatedSkills.map(s => s.name) })
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
  selectedSkillIds.value = props.skills.map(s => s.id)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="profile-section">
    <p class="filter-title">Навыки</p>

    <div class="skills-tags">
      <span
        v-for="skill in skills"
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
        :disabled="isLoadingSkills"
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