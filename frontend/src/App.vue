<template>
  <div class="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-900" :class="{ dark: isDark }">
    <AppSidebar />
    <main class="flex-1 overflow-y-auto px-6 py-5">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppSidebar from './components/AppSidebar.vue'

const isDark = ref(false)

function applyTheme() {
  isDark.value = localStorage.getItem('chrony_theme') === 'dark'
}

onMounted(applyTheme)
window.addEventListener('storage', applyTheme)
</script>
