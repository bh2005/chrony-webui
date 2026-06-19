<template>
  <div class="min-h-screen bg-gray-950 text-gray-100">
    <!-- Navbar -->
    <nav class="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <svg class="w-6 h-6 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="font-semibold text-lg tracking-tight">chrony-webui</span>
      </div>
      <div class="flex items-center gap-6">
        <router-link to="/dashboard"
          class="text-sm font-medium transition-colors"
          :class="$route.path === '/dashboard' ? 'text-brand-400' : 'text-gray-400 hover:text-gray-100'">
          Status
        </router-link>
        <router-link to="/config"
          class="text-sm font-medium transition-colors"
          :class="$route.path === '/config' ? 'text-brand-400' : 'text-gray-400 hover:text-gray-100'">
          Konfiguration
        </router-link>
        <!-- API-Key Feld -->
        <div class="flex items-center gap-2">
          <input
            v-model="apiKey"
            type="password"
            placeholder="API Key"
            class="text-sm bg-gray-800 border border-gray-700 rounded px-3 py-1 w-36 focus:outline-none focus:border-brand-500"
            @change="saveKey"
          />
          <span :class="keyOk ? 'text-green-400' : 'text-gray-600'" class="text-xs">●</span>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <main class="max-w-5xl mx-auto px-6 py-8">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getApiKey, setApiKey, api } from './api.js'

const apiKey = ref(getApiKey())
const keyOk = ref(false)

function saveKey() {
  setApiKey(apiKey.value)
  checkKey()
}

async function checkKey() {
  try {
    await api.status()
    keyOk.value = true
  } catch {
    keyOk.value = false
  }
}

onMounted(checkKey)
</script>
