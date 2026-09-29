<script setup>
import { ref, watch } from 'vue'
import { EXPERIENCE_OPTIONS, WORK_FORMAT_OPTIONS, WORK_SCHEDULE_OPTIONS, EMPLOYMENT_FORM_OPTIONS } from '../utils/vacancyFormatters'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  modelValue: { type: Object, required: true },
})

const emit = defineEmits(['close', 'apply', 'update:modelValue'])

const localFilters = ref({ ...props.modelValue })

watch(() => props.isOpen, (open) => {
  if (open) {
    localFilters.value = {
      experience: [...(props.modelValue.experience || [])],
      work_format: [...(props.modelValue.work_format || [])],
      salary_from: props.modelValue.salary_from || null,
      work_schedule_by_days: [...(props.modelValue.work_schedule_by_days || [])],
      employment_form: [...(props.modelValue.employment_form || [])],
    }
  }
})

function toggleValue(list, value) {
  const index = list.indexOf(value)
  if (index === -1) {
    list.push(value)
  } else {
    list.splice(index, 1)
  }
}

function handleApply() {
  emit('update:modelValue', {
    experience: [...localFilters.value.experience],
    work_format: [...localFilters.value.work_format],
    salary_from: localFilters.value.salary_from,
    work_schedule_by_days: [...localFilters.value.work_schedule_by_days],
    employment_form: [...localFilters.value.employment_form],
  })
  emit('apply')
  emit('close')
}

function handleReset() {
  localFilters.value = {
    experience: [],
    work_format: [],
    salary_from: null,
    work_schedule_by_days: [],
    employment_form: [],
  }
}
</script>

<template>
  <div v-if="isOpen" class="filters-overlay" @click.self="emit('close')">
    <div class="filters-panel">
      <div class="filters-header">
        <h3>Фильтры</h3>
        <button class="filters-close" @click="emit('close')" aria-label="Закрыть фильтры">✕</button>
      </div>

      <div class="filters-body">
        <div class="filter-section">
          <p class="filter-title">Опыт работы</p>
          <label v-for="option in EXPERIENCE_OPTIONS" :key="option.value" class="filter-checkbox">
            <input
              type="checkbox"
              :checked="localFilters.experience.includes(option.value)"
              @change="toggleValue(localFilters.experience, option.value)"
            />
            {{ option.label }}
          </label>
        </div>

        <div class="filter-section">
          <p class="filter-title">Формат работы</p>
          <label v-for="option in WORK_FORMAT_OPTIONS" :key="option.value" class="filter-checkbox">
            <input
              type="checkbox"
              :checked="localFilters.work_format.includes(option.value)"
              @change="toggleValue(localFilters.work_format, option.value)"
            />
            {{ option.label }}
          </label>
        </div>

        <div class="filter-section">
          <p class="filter-title">Уровень дохода</p>
          <input
            v-model.number="localFilters.salary_from"
            type="number"
            placeholder="Например: 100000"
            class="filter-salary-input"
          />
        </div>

        <div class="filter-section">
            <p class="filter-title">Тип занятости</p>
            <label v-for="option in EMPLOYMENT_FORM_OPTIONS" :key="option.value" class="filter-checkbox">
                <input
                    type="checkbox"
                    :checked="localFilters.employment_form.includes(option.value)"
                    @change="toggleValue(localFilters.employment_form, option.value)"
                />
                {{ option.label }}
            </label>
        </div>

        <div class="filter-section">
            <p class="filter-title">График работы</p>
            <div class="filter-pills">
                <button
                    v-for="option in WORK_SCHEDULE_OPTIONS"
                    :key="option.value"
                    type="button"
                    class="filter-pill"
                    :class="{ active: localFilters.work_schedule_by_days.includes(option.value) }"
                    @click="toggleValue(localFilters.work_schedule_by_days, option.value)"
                >
                    {{ option.label }}
                </button>
            </div>
        </div>
      </div>

      <div class="filters-footer">
        <button class="filters-reset" @click="handleReset">Сбросить</button>
        <button class="filters-apply" @click="handleApply">Применить</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filters-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: flex-end;
  z-index: 100;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.filters-panel {
  background: #ffffff;
  color: #1a1a1a;
  width: 360px;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 24px 0 0 24px;
  box-shadow: -8px 0 30px rgba(0, 0, 0, 0.15);
  border-left: 1px solid #e5e4e7;
  animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 16px;
  border-bottom: 1px solid #e5e4e7;
}

.filters-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.filters-close {
  border: none;
  background: #f4f5f7;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  color: #555;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.filters-close:hover {
  background: #fee2e2;
  color: #ef4444;
}

.filters-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.filters-body::-webkit-scrollbar {
  width: 6px;
}
.filters-body::-webkit-scrollbar-track {
  background: transparent;
}
.filters-body::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 10px;
}

.filter-section {
  margin-bottom: 28px;
}

.filter-section:last-child {
  margin-bottom: 0;
}

.filter-title {
  font-size: 13px;
  font-weight: 600;
  color: #888;
  margin: 0 0 12px 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  font-size: 14px;
  color: #1a1a1a;
  cursor: pointer;
  transition: color 0.2s;
}

.filter-checkbox:hover {
  color: #000;
}

.filter-checkbox input[type="checkbox"] {
  accent-color: #4a6cf7;
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.filter-salary-input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 14px;
  background: #fff;
  color: #1a1a1a;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.filter-salary-input::placeholder {
  color: #999;
}

.filter-salary-input:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.1);
}

.filters-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-top: 1px solid #e5e4e7;
  background: #fff;
  border-radius: 0 0 0 24px;
}

.filters-reset {
  background: transparent;
  border: 1px solid #ddd;
  color: #555;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  padding: 10px 16px;
  border-radius: 10px;
  transition: all 0.2s;
}

.filters-reset:hover {
  background: #f4f5f7;
  color: #1a1a1a;
  border-color: #ccc;
}

.filters-apply {
  background: #4a6cf7;
  color: #fff;
  border: none;
  padding: 10px 24px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.filters-apply:hover {
  background: #3b5bdb;
}

.filters-apply:active {
  transform: scale(0.97);
}

.filter-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-pill {
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

.filter-pill:hover {
  border-color: #4a6cf7;
  color: #4a6cf7;
}

.filter-pill.active {
  background: #4a6cf7;
  border-color: #4a6cf7;
  color: #fff;
  box-shadow: 0 2px 8px rgba(74, 108, 247, 0.3);
}
</style>