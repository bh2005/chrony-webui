<template>
  <div class="space-y-5 max-w-3xl">
    <h1 class="text-xl font-bold text-slate-800 dark:text-slate-100">Konfiguration</h1>

    <!-- Tabs -->
    <div class="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-xl p-1 w-fit">
      <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
        class="px-4 py-1.5 text-sm font-medium rounded-lg transition-colors"
        :class="activeTab === tab.id
          ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
          : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'">
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab: Server -->
    <div v-if="activeTab === 'servers'" class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-6 shadow-sm space-y-6">

      <div>
        <div class="flex items-center justify-between mb-3">
          <div>
            <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Primäre NTP-Server</h2>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
              Eintrag mit <code class="text-ks-600 dark:text-ks-300 font-mono">iburst prefer</code>
            </p>
          </div>
          <button @click="primary.push('')"
            class="text-xs text-ks-600 dark:text-ks-400 hover:text-ks-800 font-medium flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>Hinzufügen
          </button>
        </div>
        <div class="space-y-2">
          <div v-for="(_, i) in primary" :key="'p'+i" class="flex gap-2">
            <input v-model="primary[i]" type="text" placeholder="10.122.3.35"
              class="flex-1 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:border-ks-500 transition-colors" />
            <button @click="primary.splice(i,1)" class="px-2 text-slate-300 hover:text-red-500 transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <p v-if="primary.length === 0" class="text-xs text-slate-400 italic">Keine primären Server</p>
        </div>
      </div>

      <hr class="border-slate-100 dark:border-slate-700"/>

      <div>
        <div class="flex items-center justify-between mb-3">
          <div>
            <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Fallback-Server (Internet)</h2>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
              Eintrag mit <code class="text-ks-600 dark:text-ks-300 font-mono">iburst</code>
            </p>
          </div>
          <button @click="fallback.push('')"
            class="text-xs text-ks-600 dark:text-ks-400 hover:text-ks-800 font-medium flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>Hinzufügen
          </button>
        </div>
        <div class="space-y-2">
          <div v-for="(_, i) in fallback" :key="'f'+i" class="flex gap-2">
            <input v-model="fallback[i]" type="text" placeholder="0.pool.ntp.org"
              class="flex-1 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:border-ks-500 transition-colors" />
            <button @click="fallback.splice(i,1)" class="px-2 text-slate-300 hover:text-red-500 transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <p v-if="fallback.length === 0" class="text-xs text-slate-400 italic">Keine Fallback-Server</p>
        </div>
      </div>

      <div class="flex items-center gap-3 pt-1">
        <button @click="saveServers" :disabled="savingServers"
          class="bg-ks-600 hover:bg-ks-700 disabled:opacity-50 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors shadow-sm">
          {{ savingServers ? 'Speichern…' : 'Speichern & Reload' }}
        </button>
        <button @click="loadServers" class="text-sm text-slate-400 hover:text-slate-600 transition-colors">Zurücksetzen</button>
        <span v-if="serversSaved" class="text-sm text-green-500 font-medium">✓ Gespeichert</span>
        <span v-if="serversError" class="text-sm text-red-500">{{ serversError }}</span>
      </div>
    </div>

    <!-- Tab: chrony.conf -->
    <div v-if="activeTab === 'raw'" class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm overflow-hidden">
      <div class="px-4 py-3 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
        <div>
          <span class="text-sm font-semibold text-slate-700 dark:text-slate-200">chrony.conf</span>
          <span class="ml-2 text-xs text-slate-400 font-mono">/etc/chrony/chrony.conf</span>
        </div>
        <button @click="loadRaw" class="text-xs text-slate-400 hover:text-slate-600 transition-colors">↻ Neu laden</button>
      </div>
      <textarea v-model="rawConf"
        spellcheck="false"
        class="w-full h-96 bg-slate-950 text-green-400 font-mono text-sm p-4 resize-y focus:outline-none border-0"
        placeholder="Lade…"
      ></textarea>
      <div class="px-4 py-3 border-t border-slate-100 dark:border-slate-700 flex items-center gap-3">
        <button @click="saveRaw" :disabled="savingRaw"
          class="bg-ks-600 hover:bg-ks-700 disabled:opacity-50 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors shadow-sm">
          {{ savingRaw ? 'Speichern…' : 'Speichern & Reload' }}
        </button>
        <span v-if="rawSaved"  class="text-sm text-green-500 font-medium">✓ Gespeichert</span>
        <span v-if="rawError"  class="text-sm text-red-500">{{ rawError }}</span>
      </div>
    </div>

    <!-- Tab: Dienste -->
    <div v-if="activeTab === 'services'" class="space-y-4">

      <!-- Service-Status Card -->
      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-5 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">chrony Dienst</h2>
          <button @click="loadServiceStatus" class="text-xs text-slate-400 hover:text-slate-600 transition-colors">↻ Aktualisieren</button>
        </div>

        <div v-if="svcStatus" class="flex items-center gap-3 mb-4">
          <span :class="svcStatus.active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'"
            class="text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wide">
            {{ svcStatus.status }}
          </span>
          <span v-if="svcStatus.since" class="text-xs text-slate-400">seit {{ svcStatus.since }}</span>
        </div>

        <div v-if="svcStatus?.detail"
          class="bg-slate-950 text-slate-300 font-mono text-xs p-3 rounded-lg overflow-x-auto whitespace-pre max-h-40 overflow-y-auto mb-4">{{ svcStatus.detail }}</div>

        <div class="flex gap-3">
          <button @click="restart" :disabled="restarting"
            class="flex items-center gap-2 bg-ks-600 hover:bg-ks-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors shadow-sm">
            <svg :class="restarting && 'animate-spin'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            {{ restarting ? 'Neustart…' : 'chrony neu starten' }}
          </button>
          <span v-if="restartMsg" class="text-sm" :class="restartOk ? 'text-green-500' : 'text-red-500'">
            {{ restartMsg }}
          </span>
        </div>
      </div>

      <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/40 rounded-xl p-4 text-sm text-amber-700 dark:text-amber-300">
        <strong>Hinweis:</strong> Ein Neustart von chrony unterbricht kurzzeitig die NTP-Synchronisation.
      </div>
    </div>

    <!-- Tab: Konto -->
    <div v-if="activeTab === 'account'" class="max-w-sm">
      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-6 shadow-sm space-y-4">
        <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Passwort ändern</h2>

        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5">Aktuelles Passwort</label>
            <input v-model="pwCurrent" type="password" autocomplete="current-password"
              class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-ks-500 transition-colors" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5">Neues Passwort</label>
            <input v-model="pwNew" type="password" autocomplete="new-password"
              class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-ks-500 transition-colors" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5">Neues Passwort wiederholen</label>
            <input v-model="pwConfirm" type="password" autocomplete="new-password"
              class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-ks-500 transition-colors"
              :class="pwConfirm && pwNew !== pwConfirm ? 'border-red-400 dark:border-red-500' : ''" />
            <p v-if="pwConfirm && pwNew !== pwConfirm" class="text-xs text-red-500 mt-1">Passwörter stimmen nicht überein</p>
          </div>
        </div>

        <div class="flex items-center gap-3 pt-1">
          <button @click="savePassword"
            :disabled="pwSaving || !pwCurrent || !pwNew || pwNew !== pwConfirm"
            class="bg-ks-600 hover:bg-ks-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors shadow-sm">
            {{ pwSaving ? 'Speichern…' : 'Passwort ändern' }}
          </button>
          <span v-if="pwOk"    class="text-sm text-green-500 font-medium">✓ Geändert</span>
          <span v-if="pwError" class="text-sm text-red-500">{{ pwError }}</span>
        </div>

        <p class="text-xs text-slate-400 dark:text-slate-500 pt-1">
          Mindestens 6 Zeichen. Das neue Passwort gilt bis zum nächsten Container-Neustart.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api.js'

const activeTab = ref('servers')
const tabs = [
  { id: 'servers',   label: 'Server' },
  { id: 'raw',       label: 'chrony.conf' },
  { id: 'services',  label: 'Dienste' },
  { id: 'account',   label: 'Konto' },
]

// --- Server Tab ---
const primary      = ref([])
const fallback     = ref([])
const savingServers = ref(false)
const serversSaved  = ref(false)
const serversError  = ref('')

async function loadServers() {
  serversError.value = ''
  try {
    const cfg = await api.getConfig()
    primary.value  = cfg.primary.map(s => s.address)
    fallback.value = cfg.fallback.map(s => s.address)
  } catch { serversError.value = 'Laden fehlgeschlagen' }
}

async function saveServers() {
  serversError.value = ''; serversSaved.value = false; savingServers.value = true
  try {
    await api.putConfig({
      primary:  primary.value.map(s => s.trim()).filter(Boolean),
      fallback: fallback.value.map(s => s.trim()).filter(Boolean),
    })
    serversSaved.value = true
    setTimeout(() => serversSaved.value = false, 3000)
  } catch (e) {
    serversError.value = e.response?.data?.detail || 'Fehler'
  } finally { savingServers.value = false }
}

// --- Raw Tab ---
const rawConf   = ref('')
const savingRaw = ref(false)
const rawSaved  = ref(false)
const rawError  = ref('')

async function loadRaw() {
  rawError.value = ''
  try {
    const r = await api.getRawConf()
    rawConf.value = r.content
  } catch { rawError.value = 'Laden fehlgeschlagen' }
}

async function saveRaw() {
  rawError.value = ''; rawSaved.value = false; savingRaw.value = true
  try {
    await api.putRawConf(rawConf.value)
    rawSaved.value = true
    setTimeout(() => rawSaved.value = false, 3000)
  } catch (e) {
    rawError.value = e.response?.data?.detail || 'Fehler'
  } finally { savingRaw.value = false }
}

// --- Service Tab ---
const svcStatus  = ref(null)
const restarting = ref(false)
const restartMsg = ref('')
const restartOk  = ref(false)

async function loadServiceStatus() {
  try { svcStatus.value = await api.serviceStatus() }
  catch { svcStatus.value = { active: false, status: 'error', detail: '' } }
}

async function restart() {
  restarting.value = true; restartMsg.value = ''
  try {
    const r = await api.serviceRestart()
    restartOk.value = true
    restartMsg.value = r.message || '✓ Neugestartet'
    setTimeout(() => { restartMsg.value = ''; loadServiceStatus() }, 2000)
  } catch (e) {
    restartOk.value = false
    restartMsg.value = e.response?.data?.detail || 'Neustart fehlgeschlagen'
  } finally { restarting.value = false }
}

// --- Konto Tab ---
const pwCurrent = ref('')
const pwNew     = ref('')
const pwConfirm = ref('')
const pwSaving  = ref(false)
const pwOk      = ref(false)
const pwError   = ref('')

async function savePassword() {
  pwError.value = ''; pwOk.value = false
  if (pwNew.value !== pwConfirm.value) { pwError.value = 'Passwörter stimmen nicht überein'; return }
  pwSaving.value = true
  try {
    await api.changePassword(pwCurrent.value, pwNew.value)
    pwOk.value = true
    pwCurrent.value = ''; pwNew.value = ''; pwConfirm.value = ''
    setTimeout(() => pwOk.value = false, 3000)
  } catch (e) {
    pwError.value = e.response?.data?.detail || 'Fehler beim Ändern'
  } finally { pwSaving.value = false }
}

onMounted(() => {
  loadServers()
  loadRaw()
  loadServiceStatus()
})
</script>
