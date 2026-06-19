<template>
  <div class="space-y-5 max-w-2xl">
    <h1 class="text-xl font-bold text-slate-800 dark:text-slate-100">Konfiguration</h1>

    <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-6 shadow-sm space-y-6">

      <!-- Primäre Server -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <div>
            <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Primäre NTP-Server</h2>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
              Eintrag mit <code class="text-ks-600 dark:text-ks-300 font-mono">iburst prefer</code>
            </p>
          </div>
          <button @click="addServer('primary')"
            class="text-xs text-ks-600 dark:text-ks-400 hover:text-ks-800 dark:hover:text-ks-200 flex items-center gap-1 font-medium">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Hinzufügen
          </button>
        </div>
        <div class="space-y-2">
          <div v-for="(_, i) in primary" :key="'p'+i" class="flex gap-2">
            <input v-model="primary[i]" type="text" placeholder="10.122.3.35"
              class="flex-1 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm font-mono text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 dark:focus:border-ks-400 transition-colors" />
            <button @click="remove(primary, i)"
              class="px-2 text-slate-300 dark:text-slate-600 hover:text-red-500 dark:hover:text-red-400 transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p v-if="primary.length === 0" class="text-xs text-slate-400 italic">Keine primären Server konfiguriert</p>
        </div>
      </div>

      <hr class="border-slate-100 dark:border-slate-700" />

      <!-- Fallback Server -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <div>
            <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Fallback-Server (Internet)</h2>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
              Eintrag mit <code class="text-ks-600 dark:text-ks-300 font-mono">iburst</code> — nur aktiv wenn primäre nicht erreichbar
            </p>
          </div>
          <button @click="addServer('fallback')"
            class="text-xs text-ks-600 dark:text-ks-400 hover:text-ks-800 dark:hover:text-ks-200 flex items-center gap-1 font-medium">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Hinzufügen
          </button>
        </div>
        <div class="space-y-2">
          <div v-for="(_, i) in fallback" :key="'f'+i" class="flex gap-2">
            <input v-model="fallback[i]" type="text" placeholder="0.pool.ntp.org"
              class="flex-1 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm font-mono text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 dark:focus:border-ks-400 transition-colors" />
            <button @click="remove(fallback, i)"
              class="px-2 text-slate-300 dark:text-slate-600 hover:text-red-500 dark:hover:text-red-400 transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p v-if="fallback.length === 0" class="text-xs text-slate-400 italic">Keine Fallback-Server konfiguriert</p>
        </div>
      </div>

      <!-- Speichern -->
      <div class="flex items-center gap-3 pt-1">
        <button @click="save" :disabled="saving"
          class="bg-ks-600 hover:bg-ks-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors shadow-sm">
          {{ saving ? 'Speichern…' : 'Speichern & Reload' }}
        </button>
        <button @click="load" class="text-sm text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
          Zurücksetzen
        </button>
        <span v-if="saved" class="text-sm text-green-500 dark:text-green-400 font-medium">✓ Gespeichert</span>
        <span v-if="error" class="text-sm text-red-500 dark:text-red-400">{{ error }}</span>
      </div>
    </div>

    <!-- Hinweis -->
    <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/40 rounded-xl p-4 text-sm text-amber-700 dark:text-amber-300">
      <strong>Hinweis:</strong> Beim Speichern wird
      <code class="font-mono text-amber-800 dark:text-amber-200">/etc/chrony/chrony.conf</code>
      neu geschrieben und chrony neu geladen. Andere Direktiven (makestep, driftfile…) bleiben erhalten.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api.js'

const primary = ref([])
const fallback = ref([])
const saving  = ref(false)
const saved   = ref(false)
const error   = ref('')

async function load() {
  error.value = ''
  try {
    const cfg = await api.getConfig()
    primary.value  = cfg.primary.map(s => s.address)
    fallback.value = cfg.fallback.map(s => s.address)
  } catch {
    error.value = 'Laden fehlgeschlagen — API Key korrekt?'
  }
}

function addServer(type) {
  if (type === 'primary') primary.value.push('')
  else fallback.value.push('')
}

function remove(list, i) { list.splice(i, 1) }

async function save() {
  error.value = ''; saved.value = false; saving.value = true
  try {
    const p = primary.value.map(s => s.trim()).filter(Boolean)
    const f = fallback.value.map(s => s.trim()).filter(Boolean)
    await api.putConfig({ primary: p, fallback: f })
    saved.value = true
    setTimeout(() => saved.value = false, 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Fehler beim Speichern'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
