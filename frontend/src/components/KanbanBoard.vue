<script setup>
import { onMounted, computed } from 'vue';
import  draggable from 'vuedraggable';
import { useApplicationStore } from '../stores/applications'

const store = useApplicationStore()

onMounted(() => {
    store.fetchApplications()
})

const columns = [
  { key: 'found', label: 'Найдено' },
  { key: 'applied', label: 'Откликнулся' },
  { key: 'interview', label: 'Собеседование' },
  { key: 'offer', label: 'Оффер' },
  { key: 'rejected', label: 'Отказ' },
]

function columnModel(statusKey) {
  return computed(() => store.applications.filter((app) => app.status === statusKey))
}

const columnModels = Object.fromEntries(
  columns.map((column) => [column.key, columnModel(column.key)])
)

function onChange(event, statusKey) {
  if (event.added) {
    const movedApplication = event.added.element
    store.updateStatus(movedApplication.id, statusKey)
  }
}
</script>

<template>
  <div class="board">
    <p v-if="store.isLoading">Загрузка...</p>
    <p v-else-if="store.error">{{ store.error }}</p>

    <div v-else class="board-columns">
      <div v-for="column in columns" :key="column.key" class="column">
        <h3 class="column-title">
          {{ column.label }}
          <span class="column-count">{{ columnModels[column.key].length }}</span>
        </h3>

        <draggable
          :list="columnModels[column.key].value"
          :group="'applications'"
          item-key="id"
          :animation="200"
          :force-fallback="true"
          ghost-class="card-ghost"
          chosen-class="card-chosen"
          drag-class="card-dragging"
          class="column-cards"
          @change="(event) => onChange(event, column.key)"
        >
          <template #item="{ element }">
            <div class="card">
              <p class="card-title">{{ element.vacancy.title }}</p>
              <p class="card-company">{{ element.vacancy.company }}</p>
            </div>
          </template>
        </draggable>
      </div>
    </div>
  </div>
</template>

<style scoped>
.board {
  padding: 24px;
  font-family: system-ui, sans-serif;
}

.board-columns {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  align-items: start;
}

.column {
  background: #f4f5f7;
  border-radius: 10px;
  padding: 12px;
  min-height: 300px;
}

.column-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
  color: #444;
  margin: 0 0 12px 0;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.column-count {
  background: #dcdfe4;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 12px;
}

.column-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 250px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  cursor: grab;
}

.card:active {
  cursor: grabbing;
}

.card-title {
  font-weight: 600;
  margin: 0 0 4px 0;
  font-size: 14px;
}

.card-company {
  color: #666;
  font-size: 13px;
  margin: 0;
}

.card-ghost {
  opacity: 0.4;
  background: #e0e7ff;
  border: 2px dashed #4a6cf7;
}

.card-chosen {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-dragging {
  opacity: 0.9;
  transform: rotate(2deg);
  cursor: grabbing;
}
</style>