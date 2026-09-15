<script setup>
import { onMounted } from 'vue'
import { useTrackerStore } from '../stores/tracker'

const store = useTrackerStore()

onMounted( () => {
    store.fetchVacancies()
})
</script>

<template>
  <div>
    <p v-if="store.isLoading">Загрузка...</p>
    <p v-else-if="store.error">{{ store.error }}</p>
    <p v-else-if="store.vacancies.length === 0">Вакансий пока нет</p>

    <ul v-else>
      <li v-for="vacancy in store.vacancies" :key="vacancy.id">
        {{ vacancy.title }} — {{ vacancy.company }}
      </li>
    </ul>
  </div>
</template>