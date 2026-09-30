<script setup>
import { ref } from 'vue'

const isCollapsed = ref(false)

const toggleNav = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<template>
  <div class="app-shell">
    <aside class="app-sidebar" :class="{ 'is-collapsed': isCollapsed }">
      <button class="sidebar-toggle" @click="toggleNav" :title="isCollapsed ? 'Развернуть' : 'Свернуть'">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="20" 
          height="20" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2" 
          stroke-linecap="round" 
          stroke-linejoin="round"
          class="toggle-icon"
          :class="{ 'rotated': isCollapsed }"
        >
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>

      <nav class="app-nav">
        <router-link to="/" class="nav-link" active-class="nav-link-active">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="9" y1="3" x2="9" y2="21"></line>
          </svg>
          <span class="nav-text">Доска</span>
        </router-link>

        <router-link to="/search" class="nav-link" active-class="nav-link-active">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <span class="nav-text">Поиск вакансий</span>
        </router-link>
      </nav>
    </aside>

    <main class="app-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
  position: relative;
  box-sizing: border-box;
}

.app-content {
  flex: 1;
  padding: 24px;
  text-align: left;
  overflow-y: auto;
  overflow-x: hidden;
  height: 100vh;
}

.app-content::-webkit-scrollbar {
  width: 8px;
}
.app-content::-webkit-scrollbar-track {
  background: transparent;
}
.app-content::-webkit-scrollbar-thumb {
  background: var(--border, #e5e4e7);
  border-radius: 10px;
}
.app-content::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}

.app-sidebar {
  width: 240px;
  background-color: var(--code-bg);
  border-radius: 20px;
  border-right: 1px solid var(--border);
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  padding-top: 24px;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  flex-shrink: 0;
  height: 100vh;
  margin: 8px 8px 8px 0;
  box-sizing: border-box;
}

@media (prefers-color-scheme: dark) {
  .app-sidebar {
    background-color: #1e1f26;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
  }
}

.app-sidebar.is-collapsed {
  width: 72px;
}

.sidebar-toggle {
  position: absolute;
  top: 16px;
  right: 16px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text);
  transition: all 0.2s;
  z-index: 10;
}

.sidebar-toggle:hover {
  background: var(--accent-bg);
  color: var(--accent);
  border-color: var(--accent-border);
}

.toggle-icon {
  transition: transform 0.3s ease;
}

.toggle-icon.rotated {
  transform: rotate(180deg);
}

.app-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 48px 12px 24px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 500;
  font-size: 15px;
  transition: all 0.2s ease;
  overflow: hidden;
  color: var(--text);
}

.nav-link:hover {
  background: var(--social-bg);
  color: var(--text-h);
}

.nav-link-active {
  background-color: rgba(74, 108, 247, 0.1);
  color: #4a6cf7;
  font-weight: 600;
}

.nav-link-active:hover {
  background-color: rgba(74, 108, 247, 0.1);
  color: #4a6cf7;
}

.nav-icon {
  color: var(--text);
  transition: color 0.2s;
  flex-shrink: 0;
}

.nav-link:hover .nav-icon {
  color: var(--text-h);
}

.nav-link-active .nav-icon {
  color: #4a6cf7;
}

.nav-link-active:hover .nav-icon {
  color: #4a6cf7;
}

@media (prefers-color-scheme: dark) {
  .nav-link {
    color: #e2e8f0;
  }
  .nav-icon {
    color: #cbd5e0;
  }
  .nav-link:hover .nav-icon {
    color: #ffffff;
  }
  .nav-link-active, 
  .nav-link-active:hover {
    color: #60a5fa; 
    background-color: rgba(96, 165, 250, 0.15);
  }
  .nav-link-active .nav-icon,
  .nav-link-active:hover .nav-icon {
    color: #60a5fa;
  }
}

.nav-text {
  white-space: nowrap;
  opacity: 1;
  transition: opacity 0.2s ease, width 0.3s ease;
}

.app-sidebar.is-collapsed .nav-text {
  opacity: 0;
  width: 0;
  pointer-events: none;
}

.app-sidebar.is-collapsed .nav-link {
  justify-content: center;
  padding: 12px 0;
}

@media (max-width: 768px) {
  .app-shell {
    flex-direction: column;
    height: auto;
    min-height: 100vh;
    overflow: auto;
  }
  
  .app-content {
    height: auto;
    overflow-y: visible;
  }

  .app-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--border);
    border-radius: 20px;
    order: -1;
    padding-top: 12px;
    margin-right: 0;
    margin-bottom: 8px;
    height: auto;
    position: static;
  }

  .app-sidebar.is-collapsed {
    width: 100%; 
  }

  .sidebar-toggle {
    display: none;
  }

  .app-nav {
    flex-direction: row;
    justify-content: space-around;
    padding: 12px;
  }

  .nav-link {
    flex-direction: column;
    gap: 4px;
    font-size: 12px;
    padding: 8px 16px;
  }
  
  .nav-text {
    opacity: 1 !important;
    width: auto !important;
  }
}
</style>