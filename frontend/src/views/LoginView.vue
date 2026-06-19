<template>
  <div class="min-h-screen bg-slate-900 flex items-center justify-center px-4" :class="{ dark: isDark }">
    <div class="w-full max-w-sm">

      <!-- Logo / Titel -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-ks-700 mb-4 shadow-lg">
          <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75"
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-white tracking-tight">chrony-webui</h1>
        <p class="text-slate-400 text-sm mt-1">NTP Manager</p>
      </div>

      <!-- Login Card -->
      <div class="bg-slate-800 border border-slate-700 rounded-2xl p-6 shadow-xl">
        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5">
              Benutzername
            </label>
            <input
              v-model="username"
              type="text"
              autocomplete="username"
              placeholder="admin"
              class="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-ks-400 transition-colors"
              :disabled="loading"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5">
              Passwort
            </label>
            <input
              v-model="password"
              type="password"
              autocomplete="current-password"
              placeholder="••••••••"
              class="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-ks-400 transition-colors"
              :disabled="loading"
            />
          </div>

          <div v-if="error" class="text-sm text-red-400 bg-red-900/20 border border-red-800/40 rounded-lg px-3 py-2">
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading || !username || !password"
            class="w-full bg-ks-600 hover:bg-ks-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium text-sm py-2.5 rounded-lg transition-colors shadow-sm mt-2"
          >
            {{ loading ? 'Anmelden…' : 'Anmelden' }}
          </button>
        </form>
      </div>

      <p class="text-center text-slate-600 text-xs mt-6">Status-Dashboard ist ohne Login zugänglich</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api, setToken } from '../api.js'

const router   = useRouter()
const route    = useRoute()
const username = ref('')
const password = ref('')
const error    = ref('')
const loading  = ref(false)
const isDark   = ref(false)

onMounted(() => {
  isDark.value = localStorage.getItem('chrony_theme') === 'dark'
})

async function submit() {
  error.value = ''; loading.value = true
  try {
    const res = await api.login(username.value, password.value)
    setToken(res.token)
    const redirect = route.query.redirect || '/config'
    router.push(redirect)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Anmeldung fehlgeschlagen'
  } finally {
    loading.value = false
  }
}
</script>
