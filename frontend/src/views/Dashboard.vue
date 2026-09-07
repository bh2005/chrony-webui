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
      <StatCard label="Referenz-Server"  :value="refName"                       highlight
        hint="Der NTP-Server, gegen den dieser Rechner sich aktuell synchronisiert — von chrony aus allen konfigurierten Quellen als der Beste ausgewählt." />
      <StatCard label="Stratum"          :value="String(tracking.stratum)"      :sub="stratumLabel(tracking.stratum)" :color="stratumColor(tracking.stratum)"
        hint="Entfernung zur Referenzuhr in NTP-Hops. Stratum 1 = direkt an einer Atomuhr/GPS. Je niedriger, desto näher an der Quelle — Werte bis ~5 gelten als sehr genau." />
      <StatCard label="System-Offset"    :value="tracking.system_time"
        hint="Wie weit die Systemuhr laut letzter Messung von der per NTP ermittelten korrekten Zeit abweicht." />
      <StatCard label="Root-Delay"       :value="tracking.root_delay"
        hint="Netzwerklaufzeit (Hin- und Rückweg) von diesem Rechner bis zur Stratum-1-Referenzuhr an der Spitze der Kette." />
      <StatCard label="Letzter Offset"   :value="tracking.last_offset"
        hint="Die bei der letzten Messung/Korrektur festgestellte Zeitabweichung (mit Vorzeichen: + = Uhr ging vor, − = nach)." />
      <StatCard label="RMS Offset"       :value="tracking.rms_offset"
        hint="Root-Mean-Square der letzten Offset-Messungen — ein Stabilitätsmaß, je kleiner desto ruhiger/genauer läuft die Synchronisation." />
      <StatCard label="Frequenz"         :value="tracking.frequency"
        hint="Wie schnell/langsam die lokale Hardware-Uhr im Vergleich zur korrekten Zeit läuft (in ppm) — chrony gleicht das laufend aus." />
      <StatCard label="Leap Status"      :value="tracking.leap_status"
        :color="tracking.leap_status === 'Normal' ? 'green' : 'yellow'"
        hint="Zeigt eine bevorstehende Schaltsekunde an. 'Normal' = keine Schaltsekunde geplant." />
      <StatCard label="NTP-Clients"      :value="String(ntpClients)"
        hint="Wie viele Hosts diesen Server aktuell als NTP-Zeitquelle nutzen (chronyc clients) — die Gegenrichtung zur 'Aktivität' oben, die die eigenen vorgelagerten Quellen zeigt." />
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
        <span><span class="text-green-500 dark:text-green-400 font-mono font-bold">{{ activity.online }}</span> Online
          <HelpHint text="Konfigurierte NTP-Quellen, die aktuell erreichbar sind und Zeitdaten liefern." /></span>
        <span><span class="text-slate-400 font-mono font-bold">{{ activity.offline }}</span> Offline
          <HelpHint text="Bekannte Quellen, die momentan nicht antworten." /></span>
        <span><span class="text-amber-500 dark:text-amber-400 font-mono font-bold">{{ activity.unresolved }}</span> Unresolved
          <HelpHint text="Quellen, deren Hostname noch nicht per DNS aufgelöst werden konnte." /></span>
      </div>
    </div>

    <!-- Verlauf -->
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="flex items-center gap-1 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide">
          Verlauf
          <HelpHint text="System-Offset: Abweichung der Systemuhr über die Zeit. NTP-Anfragen/s: wie viele NTP-Client-Anfragen dieser Server pro Sekunde beantwortet (0, solange kein Client ihn als Zeitquelle nutzt)." />
        </h2>
        <div class="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
          <button v-for="r in ranges" :key="r.minutes" @click="setRange(r.minutes)"
            class="px-2.5 py-1 text-xs font-medium rounded-md transition-colors"
            :class="rangeMinutes === r.minutes
              ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
              : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'">
            {{ r.label }}
          </button>
        </div>
      </div>
      <div v-if="history.length >= 2" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <TrendChart title="System-Offset" :values="offsetSeries" :timestamps="tsSeries" unit=" µs" color="ks" :digits="2" />
        <TrendChart title="NTP-Anfragen/s" :values="reqsSeries" :timestamps="tsSeries" unit="/s" color="green" :digits="1" />
      </div>
      <div v-else class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-6 text-center text-slate-400 dark:text-slate-500 text-sm">
        Noch keine Verlaufsdaten in diesem Zeitraum
      </div>
    </div>

    <!-- Sources Table -->
    <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden shadow-sm">
      <div class="px-4 py-3 border-b border-slate-100 dark:border-slate-700">
        <h2 class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide">NTP-Quellen</h2>
      </div>
      <div v-if="sources.length" class="px-4 pt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400 dark:text-slate-500 border-b border-slate-100 dark:border-slate-700 pb-2">
        <span><span :class="stateClass('*')" class="font-mono text-[10px] font-bold px-1 rounded">^*</span> ausgewählte Referenz</span>
        <span><span :class="stateClass('-')" class="font-mono text-[10px] font-bold px-1 rounded">^-</span> Kandidat, nicht gewählt</span>
        <span><span :class="stateClass('+')" class="font-mono text-[10px] font-bold px-1 rounded">^+</span> kombiniert genutzt</span>
        <span><span :class="stateClass('?')" class="font-mono text-[10px] font-bold px-1 rounded">^?</span> nicht erreichbar/unbrauchbar</span>
      </div>
      <div v-if="sources.length === 0" class="px-4 py-6 text-slate-400 dark:text-slate-500 text-sm text-center">
        Keine Quellen
      </div>
      <table v-else class="w-full text-sm">
        <thead class="text-xs text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-700/40">
          <tr>
            <th class="px-4 py-2 text-left">Status</th>
            <th class="px-4 py-2 text-left">Server</th>
            <th class="px-4 py-2 text-center">
              <span class="inline-flex items-center gap-1">Stratum
                <HelpHint placement="bottom" text="Entfernung dieser Quelle zur Referenzuhr in NTP-Hops — je niedriger, desto näher an der Zeitquelle." /></span>
            </th>
            <th class="px-4 py-2 text-center">
              <span class="inline-flex items-center gap-1">Poll
                <HelpHint placement="bottom" text="Log2 des Abfrageintervalls in Sekunden, z.B. 6 = alle 64 Sekunden." /></span>
            </th>
            <th class="px-4 py-2 text-center">
              <span class="inline-flex items-center gap-1">Reach
                <HelpHint placement="bottom" text="Erreichbarkeits-Register (oktal) der letzten 8 Abfragen — 377 = alle letzten 8 erfolgreich beantwortet." /></span>
            </th>
            <th class="px-4 py-2 text-right">
              <span class="inline-flex items-center gap-1">Last RX
                <HelpHint placement="bottom" text="Sekunden seit der letzten Antwort dieser Quelle." /></span>
            </th>
            <th class="px-4 py-2 text-right">
              <span class="inline-flex items-center gap-1">Offset
                <HelpHint placement="bottom" text="Bei der letzten Abfrage gemessene Zeitabweichung zu dieser Quelle." /></span>
            </th>
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
import TrendChart from '../components/TrendChart.vue'

const tracking   = ref(null)
const activity   = ref({})
const ntpClients = ref(0)
const sources    = ref([])
const history    = ref([])
const loading    = ref(false)
const lastUpdate = ref('—')

const offsetSeries = computed(() => history.value.map(h => h.offset_us))
const reqsSeries   = computed(() => history.value.map(h => h.ntp_reqs_per_sec))
const tsSeries     = computed(() => history.value.map(h => h.ts))

const ranges = [
  { label: '15 Min', minutes: 15 },
  { label: '1 Std',  minutes: 60 },
  { label: '6 Std',  minutes: 360 },
  { label: '24 Std', minutes: 1440 },
]
const rangeMinutes = ref(60)
function setRange(minutes) {
  rangeMinutes.value = minutes
  refresh()
}

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
    const [status, src, hist] = await Promise.all([api.status(), api.sources(), api.history(rangeMinutes.value)])
    tracking.value = status.tracking
    activity.value = status.activity
    ntpClients.value = status.ntp_clients ?? 0
    sources.value  = src
    history.value  = hist
    lastUpdate.value = new Date().toLocaleTimeString('de-DE')
  } catch { /* API Key fehlt */ }
  finally { loading.value = false }
}

let timer
onMounted(() => { refresh(); timer = setInterval(refresh, 10000) })
onUnmounted(() => clearInterval(timer))
</script>
