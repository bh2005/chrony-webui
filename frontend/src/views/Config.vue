<template>
  <div class="space-y-6 max-w-2xl">
    <h1 class="text-2xl font-bold">Konfiguration</h1>

    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-6">

      <!-- Primäre Server -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <div>
            <h2 class="text-sm font-semibold">Primäre NTP-Server</h2>
            <p class="text-xs text-gray-500 mt-0.5">Werden mit <code class="text-brand-400">iburst prefer</code> eingetragen</p>
          </div>
          <button @click="addServer('primary')"
            class="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Hinzufügen
          </button>
        </div>
        <div class="space-y-2">
          <div v-for="(srv, i) in primary" :key="'p'+i" class="flex gap-2">
            <input v-model="primary[i]" type="text"
              placeholder="10.122.3.35"
              class="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm font-mono focus:outline-none focus:border-brand-500" />
            <button @click="remove(primary, i)"
              class="px-2 text-gray-500 hover:text-red-400 transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p v-if="primary.length === 0" class="text-xs text-gray-600 italic">Keine primären Server</p>
        </div>
      </div>

      <hr class="border-gray-800" />

      <!-- Fallback Server -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <div>
            <h2 class="text-sm font-semibold">Fallback-Server (Internet)</h2>
            <p class="text-xs text-gray-500 mt-0.5">Werden mit <code class="text-brand-400">iburst</code> eingetragen, dienen als Backup</p>
          </div>
          <button @click="addServer('fallback')"
            class="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Hinzufügen
          </button>
        </div>
        <div class="space-y-2">
          <div v-for="(srv, i) in fallback" :key="'f'+i" class="flex gap-2">
            <input v-model="fallback[i]" type="text"
              placeholder="0.pool.ntp.org"
              class="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm font-mono focus:outline-none focus:border-brand-500" />
            <button @click="remove(fallback, i)"
              class="px-2 text-gray-500 hover:text-red-400 transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p v-if="fallback.length === 0" class="text-xs text-gray-600 italic">Keine Fallback-Server</p>
        </div>
      </div>

      <!-- Speichern -->
      <div class="flex items-center gap-3 pt-2">
        <button @click="save" :disabled="saving"
          class="bg-brand-600 hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium px-5 py-2 rounded transition-colors">
          {{ saving ? 'Speichern…' : 'Speichern & Reload' }}
        </button>
        <button @click="load" class="text-sm text-gray-400 hover:text-gray-200">
          Zurücksetzen
        </button>
        <span v-if="saved" class="text-sm text-green-400">✓ Gespeichert</span>
        <span v-if="error" class="text-sm text-red-400">{{ error }}</span>
      </div>
    </div>

    <!-- Hinweis -->
    <div class="bg-yellow-900/20 border border-yellow-800/40 rounded-xl p-4 text-sm text-yellow-300">
      <strong>Hinweis:</strong> Beim Speichern wird <code class="text-yellow-200">/etc/chrony/chrony.conf</code>
      überschrieben und chrony neu geladen. Andere Direktiven (makestep, driftfile…) bleiben erhalten.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api.js'

const primary  = ref([])
const fallback = ref([])
const saving   = ref(false)
const saved    = ref(false)
const error    = ref('')

async function load() {
  error.value = ''
  try {
    const cfg = await api.getConfig()
    primary.value  = cfg.primary.map(s => s.address)
    fallback.value = cfg.fallback.map(s => s.address)
  } catch (e) {
    error.value = 'Laden fehlgeschlagen — API Key korrekt?'
  }
}

function addServer(type) {
  if (type === 'primary') primary.value.push('')
  else fallback.value.push('')
}

function remove(list, i) {
  list.splice(i, 1)
}

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
