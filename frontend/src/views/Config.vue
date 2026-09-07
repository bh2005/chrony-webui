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
            <input v-model="primary[i]" type="text" placeholder="192.0.2.35"
              class="flex-1 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm font-mono text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 transition-colors" />
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
              class="flex-1 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm font-mono text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 transition-colors" />
            <button @click="fallback.splice(i,1)" class="px-2 text-slate-300 hover:text-red-500 transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <p v-if="fallback.length === 0" class="text-xs text-slate-400 italic">Keine Fallback-Server</p>
        </div>
      </div>

      <hr class="border-slate-100 dark:border-slate-700"/>

      <div>
        <div class="flex items-center justify-between mb-3">
          <div>
            <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Erlaubte Netze (NTP-Server-Zugriff)</h2>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
              <code class="text-ks-600 dark:text-ks-300 font-mono">allow</code> — welche Clients dürfen diesen Server als NTP-Quelle nutzen. Leer = reiner Client-Modus.
            </p>
          </div>
          <button @click="allow.push('')"
            class="text-xs text-ks-600 dark:text-ks-400 hover:text-ks-800 font-medium flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>Hinzufügen
          </button>
        </div>
        <div class="space-y-2">
          <div v-for="(_, i) in allow" :key="'a'+i" class="flex gap-2">
            <input v-model="allow[i]" type="text" placeholder="10.0.0.0/8"
              class="flex-1 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm font-mono text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 transition-colors" />
            <button @click="allow.splice(i,1)" class="px-2 text-slate-300 hover:text-red-500 transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <p v-if="allow.length === 0" class="text-xs text-slate-400 italic">Keine — Server beantwortet keine NTP-Anfragen anderer Hosts</p>
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

    <!-- Tab: Zertifikat -->
    <div v-if="activeTab === 'cert'" class="space-y-4">

      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-5 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">TLS-Zertifikat (ACME · interne step-CA)</h2>
          <button @click="loadCertStatus" class="text-xs text-slate-400 hover:text-slate-600 transition-colors">↻ Aktualisieren</button>
        </div>

        <div v-if="cert" class="space-y-3">
          <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
            <span class="text-slate-400">CA-URL</span>
            <span class="font-mono text-xs break-all text-slate-700 dark:text-slate-300">{{ cert.ca_url }}</span>

            <template v-if="cert.cert_exists">
              <span class="text-slate-400">Domain</span>
              <span class="font-mono text-slate-700 dark:text-slate-200">{{ cert.domain }}</span>

              <span class="text-slate-400">Aussteller</span>
              <span class="font-mono text-xs break-all text-slate-700 dark:text-slate-300">{{ cert.issuer }}</span>

              <span class="text-slate-400">Gültig bis</span>
              <span class="flex items-center gap-2">
                <span class="font-mono text-slate-700 dark:text-slate-200">{{ cert.not_after }}</span>
                <span v-if="cert.days_remaining !== null" :class="certBadgeClass"
                  class="text-xs font-bold px-2 py-0.5 rounded-full">
                  {{ cert.days_remaining >= 0 ? `noch ${cert.days_remaining} Tage` : 'abgelaufen' }}
                </span>
              </span>
            </template>
          </div>

          <p v-if="!cert.cert_exists" class="text-sm text-slate-400 italic">Noch kein Zertifikat ausgestellt.</p>
          <p v-if="!cert.acme_sh_available" class="text-xs text-amber-600 dark:text-amber-400">
            acme.sh wurde auf dem Server nicht gefunden — Setup-Script (01-setup-acme-client.sh) ausführen.
          </p>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-6 shadow-sm space-y-4 max-w-lg">
        <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Zertifikat anfordern / erneuern</h2>

        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5">Domain (CN)</label>
            <input v-model="certDomain" type="text" placeholder="ntp01.corp.k-plus-s.net"
              class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm font-mono text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 transition-colors" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5">Zusätzliche SANs (kommagetrennt, optional)</label>
            <input v-model="certSans" type="text" placeholder="ntp01, ntp01.k-plus-s.com"
              class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm font-mono text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 transition-colors" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5">Account-E-Mail (optional, für Registrierung)</label>
            <input v-model="certEmail" type="text" placeholder="monitoring@k-plus-s.com"
              class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm font-mono text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 transition-colors" />
          </div>
        </div>

        <div class="flex items-center gap-3 pt-1 flex-wrap">
          <button @click="issueCert" :disabled="certBusy || !certDomain.trim()"
            class="bg-ks-600 hover:bg-ks-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors shadow-sm">
            {{ certIssuing ? 'Fordere an…' : 'Zertifikat anfordern' }}
          </button>
          <button @click="renewCert" :disabled="certBusy || !cert?.cert_exists"
            class="bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-slate-700 dark:text-slate-200 text-sm font-medium px-5 py-2 rounded-lg transition-colors">
            {{ certRenewing ? 'Erneuere…' : 'Jetzt erneuern' }}
          </button>
        </div>
        <p v-if="certError" class="text-sm text-red-500">{{ certError }}</p>
        <p v-if="certOk" class="text-sm text-green-500 font-medium">✓ Erfolgreich — Nginx wurde neu geladen</p>
      </div>

      <div v-if="certLog" class="bg-slate-950 text-slate-300 font-mono text-xs p-4 rounded-xl overflow-x-auto whitespace-pre-wrap max-h-64 overflow-y-auto">{{ certLog }}</div>

      <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/40 rounded-xl p-4 text-sm text-amber-700 dark:text-amber-300">
        <strong>Hinweis:</strong> Ausstellung erfolgt per ACME HTTP-01 über das bereits laufende Nginx (Webroot-Modus),
        ohne den Webserver zu stoppen. Voraussetzung ist ein installierter und bei der internen CA registrierter
        <code class="font-mono">acme.sh</code>-Client (siehe <code class="font-mono">Scripts/acme/01-setup-acme-client.sh</code>).
      </div>
    </div>

    <!-- Tab: Zugriffe -->
    <div v-if="activeTab === 'access'" class="space-y-4">

      <!-- NTP-Client-IPs -->
      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden shadow-sm">
        <div class="px-4 py-3 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
          <div>
            <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">NTP-Clients</h2>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">Welche IPs diesen Server per NTP abgefragt haben (<code class="font-mono">chronyc clients</code>)</p>
          </div>
          <div class="flex items-center gap-3">
            <button @click="exportClientsCsv" :disabled="filteredClients.length === 0"
              class="text-xs text-ks-600 dark:text-ks-400 hover:text-ks-800 disabled:opacity-40 disabled:cursor-not-allowed font-medium flex items-center gap-1 transition-colors">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 15V3"/>
              </svg>CSV exportieren
            </button>
            <button @click="loadClients" class="text-xs text-slate-400 hover:text-slate-600 transition-colors">↻ Aktualisieren</button>
          </div>
        </div>
        <div v-if="clients.length" class="px-4 pt-3">
          <input v-model="clientFilter" type="text" placeholder="Filtern nach IP/Hostname…"
            class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 text-sm font-mono text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 transition-colors" />
        </div>
        <div v-if="clients.length === 0" class="px-4 py-6 text-slate-400 dark:text-slate-500 text-sm text-center">
          Keine NTP-Anfragen bisher
        </div>
        <div v-else-if="filteredClients.length === 0" class="px-4 py-6 text-slate-400 dark:text-slate-500 text-sm text-center">
          Kein Client passt zum Filter
        </div>
        <table v-else class="w-full text-sm">
          <thead class="text-xs text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-700/40">
            <tr>
              <th class="px-4 py-2 text-left">IP / Hostname</th>
              <th class="px-4 py-2 text-right">NTP-Anfragen</th>
              <th class="px-4 py-2 text-right">Verworfen</th>
              <th class="px-4 py-2 text-right">Letzte Anfrage</th>
              <th class="px-4 py-2 text-right">Cmd-Anfragen</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
            <tr v-for="c in filteredClients" :key="c.address">
              <td class="px-4 py-2.5 font-mono text-xs text-slate-700 dark:text-slate-200">{{ c.address }}</td>
              <td class="px-4 py-2.5 text-right font-mono text-slate-600 dark:text-slate-300">{{ c.ntp_hits }}</td>
              <td class="px-4 py-2.5 text-right font-mono" :class="c.ntp_drops > 0 ? 'text-amber-500' : 'text-slate-400'">{{ c.ntp_drops }}</td>
              <td class="px-4 py-2.5 text-right font-mono text-xs text-slate-400">{{ c.ntp_last_seconds !== null ? c.ntp_last_seconds + 's' : '—' }}</td>
              <td class="px-4 py-2.5 text-right font-mono text-xs text-slate-400">{{ c.cmd_hits }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Web/API-Zugriffs-Log -->
      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden shadow-sm">
        <div class="px-4 py-3 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
          <div>
            <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Web/API-Zugriffs-Log</h2>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">Letzte {{ accessLog.length }} Requests dieser WebUI (rollierend, geht bei Backend-Neustart verloren)</p>
          </div>
          <div class="flex items-center gap-3">
            <button @click="exportAccessLogCsv" :disabled="filteredAccessLog.length === 0"
              class="text-xs text-ks-600 dark:text-ks-400 hover:text-ks-800 disabled:opacity-40 disabled:cursor-not-allowed font-medium flex items-center gap-1 transition-colors">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 15V3"/>
              </svg>CSV exportieren
            </button>
            <button @click="loadAccessLog" class="text-xs text-slate-400 hover:text-slate-600 transition-colors">↻ Aktualisieren</button>
          </div>
        </div>
        <div v-if="accessLog.length" class="px-4 pt-3">
          <input v-model="logFilter" type="text" placeholder="Filtern nach IP, Methode, Pfad oder Status…"
            class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-1.5 text-sm font-mono text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 transition-colors" />
        </div>
        <div v-if="accessLog.length === 0" class="px-4 py-6 text-slate-400 dark:text-slate-500 text-sm text-center">
          Noch keine Zugriffe protokolliert
        </div>
        <div v-else-if="filteredAccessLog.length === 0" class="px-4 py-6 text-slate-400 dark:text-slate-500 text-sm text-center">
          Kein Eintrag passt zum Filter
        </div>
        <div v-else class="max-h-96 overflow-y-auto">
          <table class="w-full text-sm">
            <thead class="text-xs text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-700/40 sticky top-0">
              <tr>
                <th class="px-4 py-2 text-left">Zeit</th>
                <th class="px-4 py-2 text-left">IP</th>
                <th class="px-4 py-2 text-left">Methode</th>
                <th class="px-4 py-2 text-left">Pfad</th>
                <th class="px-4 py-2 text-right">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
              <tr v-for="(l, i) in filteredAccessLog" :key="i" :class="l.path === '/auth/login' ? 'bg-ks-50 dark:bg-ks-900/10' : ''">
                <td class="px-4 py-2 font-mono text-xs text-slate-400">{{ formatTime(l.ts) }}</td>
                <td class="px-4 py-2 font-mono text-xs text-slate-700 dark:text-slate-200">{{ l.ip }}</td>
                <td class="px-4 py-2 font-mono text-xs text-slate-500">{{ l.method }}</td>
                <td class="px-4 py-2 font-mono text-xs text-slate-600 dark:text-slate-300">{{ l.path }}</td>
                <td class="px-4 py-2 text-right font-mono text-xs" :class="l.status >= 400 ? 'text-red-500' : 'text-green-600 dark:text-green-400'">{{ l.status }}</td>
              </tr>
            </tbody>
          </table>
        </div>
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
              class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 transition-colors" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5">Neues Passwort</label>
            <input v-model="pwNew" type="password" autocomplete="new-password"
              class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 transition-colors" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5">Neues Passwort wiederholen</label>
            <input v-model="pwConfirm" type="password" autocomplete="new-password"
              class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:border-ks-500 transition-colors"
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
import { ref, computed, onMounted } from 'vue'
import { api } from '../api.js'

const activeTab = ref('servers')
const tabs = [
  { id: 'servers',   label: 'Server' },
  { id: 'raw',       label: 'chrony.conf' },
  { id: 'services',  label: 'Dienste' },
  { id: 'cert',      label: 'Zertifikat' },
  { id: 'access',    label: 'Zugriffe' },
  { id: 'account',   label: 'Konto' },
]

// --- Server Tab ---
const primary      = ref([])
const fallback     = ref([])
const allow        = ref([])
const savingServers = ref(false)
const serversSaved  = ref(false)
const serversError  = ref('')

async function loadServers() {
  serversError.value = ''
  try {
    const cfg = await api.getConfig()
    primary.value  = cfg.primary.map(s => s.address)
    fallback.value = cfg.fallback.map(s => s.address)
    allow.value    = cfg.allow || []
  } catch { serversError.value = 'Laden fehlgeschlagen' }
}

async function saveServers() {
  serversError.value = ''; serversSaved.value = false; savingServers.value = true
  try {
    await api.putConfig({
      primary:  primary.value.map(s => s.trim()).filter(Boolean),
      fallback: fallback.value.map(s => s.trim()).filter(Boolean),
      allow:    allow.value.map(s => s.trim()).filter(Boolean),
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

// --- Zertifikat Tab ---
const cert          = ref(null)
const certDomain    = ref('')
const certSans      = ref('')
const certEmail     = ref('')
const certIssuing   = ref(false)
const certRenewing  = ref(false)
const certOk        = ref(false)
const certError     = ref('')
const certLog       = ref('')
const certBusy      = computed(() => certIssuing.value || certRenewing.value)

const certBadgeClass = computed(() => {
  const d = cert.value?.days_remaining
  if (d === null || d === undefined) return ''
  if (d < 0)  return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  if (d <= 7) return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  if (d <= 30) return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
  return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
})

async function loadCertStatus() {
  try {
    cert.value = await api.certStatus()
    if (cert.value?.domain) certDomain.value = cert.value.domain
  } catch { cert.value = null }
}

async function issueCert() {
  certError.value = ''; certOk.value = false; certLog.value = ''; certIssuing.value = true
  try {
    const r = await api.certIssue({
      domain: certDomain.value.trim(),
      sans:   certSans.value.split(',').map(s => s.trim()).filter(Boolean),
      email:  certEmail.value.trim() || null,
    })
    certOk.value = true
    certLog.value = r.log || ''
    await loadCertStatus()
  } catch (e) {
    certError.value = e.response?.data?.detail || 'Zertifikat-Anforderung fehlgeschlagen'
    certLog.value = e.response?.data?.detail || ''
  } finally { certIssuing.value = false }
}

async function renewCert() {
  certError.value = ''; certOk.value = false; certLog.value = ''; certRenewing.value = true
  try {
    const r = await api.certRenew()
    certOk.value = true
    certLog.value = r.log || ''
    await loadCertStatus()
  } catch (e) {
    certError.value = e.response?.data?.detail || 'Erneuerung fehlgeschlagen'
    certLog.value = e.response?.data?.detail || ''
  } finally { certRenewing.value = false }
}

// --- Zugriffe Tab ---
const clients      = ref([])
const clientFilter = ref('')
const accessLog    = ref([])
const logFilter    = ref('')

const filteredClients = computed(() => {
  const q = clientFilter.value.trim().toLowerCase()
  if (!q) return clients.value
  return clients.value.filter(c => c.address.toLowerCase().includes(q))
})

const filteredAccessLog = computed(() => {
  const q = logFilter.value.trim().toLowerCase()
  if (!q) return accessLog.value
  return accessLog.value.filter(l =>
    l.ip.toLowerCase().includes(q) ||
    l.method.toLowerCase().includes(q) ||
    l.path.toLowerCase().includes(q) ||
    String(l.status).includes(q)
  )
})

async function loadClients() {
  try { clients.value = await api.clients() } catch { clients.value = [] }
}

function csvCell(v) {
  if (v === null || v === undefined) return ''
  const s = String(v)
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}

function downloadCsv(filename, rows) {
  const csv = rows.map(row => row.map(csvCell).join(',')).join('\r\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename
  document.body.appendChild(a); a.click(); a.remove()
  URL.revokeObjectURL(url)
}

function exportClientsCsv() {
  const header = ['IP/Hostname', 'NTP-Anfragen', 'NTP-Verworfen', 'Letzte-Anfrage-s', 'Cmd-Anfragen', 'Cmd-Verworfen', 'Letzte-Cmd-Anfrage-s']
  const rows = filteredClients.value.map(c => [
    c.address, c.ntp_hits, c.ntp_drops, c.ntp_last_seconds, c.cmd_hits, c.cmd_drops, c.cmd_last_seconds,
  ])
  const ts = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')
  downloadCsv(`chrony-ntp-clients_${ts}.csv`, [header, ...rows])
}
async function loadAccessLog() {
  try { accessLog.value = await api.accessLog() } catch { accessLog.value = [] }
}
function exportAccessLogCsv() {
  const header = ['Zeit', 'IP', 'Methode', 'Pfad', 'Status']
  const rows = filteredAccessLog.value.map(l => [formatTime(l.ts), l.ip, l.method, l.path, l.status])
  const ts = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')
  downloadCsv(`chrony-access-log_${ts}.csv`, [header, ...rows])
}
function formatTime(ts) {
  return new Date(ts * 1000).toLocaleString('de-DE')
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
  loadCertStatus()
  loadClients()
  loadAccessLog()
})
</script>
