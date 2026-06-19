<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-slate-800 dark:text-slate-100">NTP Status</h1>
      <button @click="refresh"
        class="flex items-center gap-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-ks-400 hover:text-ks-600 dark:hover:text-ks-300 rounded-lg px-3 py-1.5 transition-colors shadow-sm">
        <svg :class="loading && 'animate-spin'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Aktualisieren
      </button>
    </div>

    <!-- Tracking Cards -->
    <div v-if="tracking" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <StatCard label="Referenz-Server"  :value="refName"                       highlight />
      <StatCard label="Stratum"          :value="String(tracking.stratum)"      :sub="stratumLabel(tracking.stratum)" :color="stratumColor(tracking.stratum)" />
      <StatCard label="System-Offset"    :value="tracking.system_time" />
      <StatCard label="Root-Delay"       :value="tracking.root_delay" />
      <StatCard label="Letzter Offset"   :value="tracking.last_offset" />
      <StatCard label="RMS Offset"       :value="tracking.rms_offset" />
      <StatCard label="Frequenz"         :value="tracking.frequency" />
      <StatCard label="Leap Status"      :value="tracking.leap_status"
        :color="tracking.leap_status === 'Normal' ? 'green' : 'yellow'" />
    </div>

    <div v-if="!tracking && !loading"
      class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-8 text-center text-slate-400 dark:text-slate-500 text-sm">
      Kein Status — API Key in der Sidebar eingeben
    </div>

    <!-- Activity -->
    <div v-if="activity && Object.keys(activity).length"
      class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-4 shadow-sm">
      <h2 class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide mb-3">Aktivität</h2>
      <div class="flex gap-6 text-sm text-slate-600 dark:text-slate-300">
        <span><span class="text-green-500 dark:text-green-400 font-mono font-bold">{{ activity.online }}</span> Online</span>
        <span><span class="text-slate-400 font-mono font-bold">{{ activity.offline }}</span> Offline</span>
        <span><span class="text-amber-500 dark:text-amber-400 font-mono font-bold">{{ activity.unresolved }}</span> Unresolved</span>
      </div>
    </div>

    <!-- Sources Table -->
    <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden shadow-sm">
      <div class="px-4 py-3 border-b border-slate-100 dark:border-slate-700">
        <h2 class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide">NTP-Quellen</h2>
      </div>
      <div v-if="sources.length === 0" class="px-4 py-6 text-slate-400 dark:text-slate-500 text-sm text-center">
        Keine Quellen
      </div>
      <table v-else class="w-full text-sm">
        <thead class="text-xs text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-700/40">
          <tr>
            <th class="px-4 py-2 text-left">Status</th>
            <th class="px-4 py-2 text-left">Server</th>
            <th class="px-4 py-2 text-center">Stratum</th>
            <th class="px-4 py-2 text-center">Poll</th>
            <th class="px-4 py-2 text-center">Reach</th>
            <th class="px-4 py-2 text-right">Last RX</th>
            <th class="px-4 py-2 text-right">Offset</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
          <tr v-for="s in sources" :key="s.name"
            :class="s.state === '*' ? 'bg-ks-50 dark:bg-ks-900/20' : ''">
            <td class="px-4 py-2.5">
              <span :class="stateClass(s.state)"
                class="inline-flex items-center font-mono text-xs font-bold px-1.5 py-0.5 rounded">
                {{ s.mode }}{{ s.state }}
              </span>
            </td>
            <td class="px-4 py-2.5 font-mono text-xs text-slate-700 dark:text-slate-200">{{ s.name }}</td>
            <td class="px-4 py-2.5 text-center text-slate-500 dark:text-slate-400">{{ s.stratum }}</td>
            <td class="px-4 py-2.5 text-center text-slate-500 dark:text-slate-400">{{ s.poll }}</td>
            <td class="px-4 py-2.5 text-center">
              <span :class="reachClass(s.reach)" class="font-mono">{{ s.reach }}</span>
            </td>
            <td class="px-4 py-2.5 text-right text-slate-400 dark:text-slate-500 font-mono text-xs">{{ s.last_rx }}s</td>
            <td class="px-4 py-2.5 text-right text-slate-600 dark:text-slate-300 font-mono text-xs">{{ s.offset }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="text-xs text-slate-400 dark:text-slate-600 text-right">Aktualisiert: {{ lastUpdate }} · alle 10 s</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { api } from '../api.js'
import StatCard from '../components/StatCard.vue'

const tracking   = ref(null)
const activity   = ref({})
const sources    = ref([])
const loading    = ref(false)
const lastUpdate = ref('—')

const refName = computed(() => {
  const id = tracking.value?.reference_id || ''
  const m = id.match(/\(([^)]+)\)/)
  return m ? m[1] : id
})

function stratumLabel(s) {
  if (s === 0) return 'nicht synchron'
  if (s === 1) return 'GPS / Atomuhr'
  if (s <= 3) return 'sehr gut'
  if (s <= 5) return 'gut'
  return 'akzeptabel'
}
function stratumColor(s) {
  if (s === 0) return 'red'
  if (s <= 3) return 'green'
  if (s <= 5) return 'yellow'
  return 'gray'
}
function stateClass(s) {
  return {
    '*': 'text-green-700 dark:text-green-400 bg-green-100 dark:bg-green-900/30',
    '-': 'text-ks-700 dark:text-ks-300 bg-ks-100 dark:bg-ks-900/30',
    '+': 'text-cyan-700 dark:text-cyan-400 bg-cyan-100 dark:bg-cyan-900/30',
    '?': 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30',
  }[s] || 'text-slate-500 bg-slate-100 dark:bg-slate-700'
}
function reachClass(r) {
  const n = parseInt(r, 8)
  if (n === 255) return 'text-green-500 dark:text-green-400'
  if (n >= 128)  return 'text-amber-500 dark:text-amber-400'
  return 'text-red-500 dark:text-red-400'
}

async function refresh() {
  loading.value = true
  try {
    const [status, src] = await Promise.all([api.status(), api.sources()])
    tracking.value = status.tracking
    activity.value = status.activity
    sources.value  = src
    lastUpdate.value = new Date().toLocaleTimeString('de-DE')
  } catch { /* API Key fehlt */ }
  finally { loading.value = false }
}

let timer
onMounted(() => { refresh(); timer = setInterval(refresh, 10000) })
onUnmounted(() => clearInterval(timer))
</script>
