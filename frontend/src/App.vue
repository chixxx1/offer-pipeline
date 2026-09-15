<script setup>
</script>

<template>
  <div class="app-shell">
    <nav class="app-nav">
      <router-link to="/" class="nav-link">Доска</router-link>
      <router-link to="/search" class="nav-link">Поиск вакансий</router-link>
    </nav>

    <router-view />
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.app-nav {
  display: flex;
  gap: 20px;
  padding: 16px 24px;
  background: #1a1a2e;
  border-bottom: 1px solid #2a2a3e;
}

.nav-link {
  color: #aaa;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  padding: 6px 0;
}

.nav-link:hover {
  color: white;
}

.router-link-active {
  color: #4a6cf7;
  border-bottom: 2px solid #4a6cf7;
}
</style>