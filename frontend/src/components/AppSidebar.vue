<template>
  <aside
    class="flex flex-col bg-ks-700 h-screen flex-shrink-0 transition-all duration-200 overflow-hidden z-40"
    :class="collapsed ? 'w-14' : 'w-56'"
  >
    <!-- Header -->
    <div class="flex items-center gap-2 h-14 px-2 border-b border-white/10 flex-shrink-0">
      <button @click="collapsed = !collapsed"
        class="p-1.5 rounded text-white/60 hover:text-white hover:bg-white/10 transition-colors flex-shrink-0"
        :title="collapsed ? 'Aufklappen' : 'Einklappen'">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
      <div v-show="!collapsed" class="leading-tight min-w-0 overflow-hidden">
        <div class="text-white font-bold text-sm tracking-wide whitespace-nowrap">chrony-webui</div>
        <div class="text-white/40 text-[9px] tracking-widest uppercase whitespace-nowrap">NTP Manager</div>
      </div>
    </div>

    <!-- Nav -->
    <nav class="flex-1 overflow-y-auto overflow-x-hidden py-2 space-y-0.5 px-1.5">
      <NavLink v-for="link in visibleLinks" :key="link.to" :link="link" :collapsed="collapsed" />
    </nav>

    <!-- Uhrzeit & Datum -->
    <div class="border-t border-white/10 px-3 py-2 flex-shrink-0">
      <div v-if="!collapsed" class="text-center">
        <div class="text-white font-mono text-lg font-semibold tracking-widest leading-tight">{{ time }}</div>
        <div class="text-white/40 text-[10px] tracking-wide mt-0.5">{{ date }}</div>
      </div>
      <div v-else class="text-center">
        <div class="text-white/60 font-mono text-xs leading-tight">{{ timeShort }}</div>
      </div>
    </div>

    <!-- Bottom -->
    <div class="border-t border-white/10 px-2 py-2 flex-shrink-0 space-y-1">
      <div class="flex items-center" :class="collapsed ? 'flex-col gap-1' : 'justify-between'">
        <!-- Theme Toggle -->
        <button @click="toggleTheme"
          class="p-1.5 rounded text-white/60 hover:text-white hover:bg-white/10 transition-colors"
          :title="isDark ? 'Light Mode' : 'Dark Mode'">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path v-if="isDark" fill-rule="evenodd" clip-rule="evenodd"
              d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"/>
            <path v-else d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>
          </svg>
        </button>

        <!-- Logout (nur wenn eingeloggt) -->
        <button v-if="loggedIn" @click="doLogout"
          class="p-1.5 rounded text-white/50 hover:text-white hover:bg-white/10 transition-colors"
          title="Abmelden">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
        </button>

        <!-- Login Link (wenn nicht eingeloggt) -->
        <router-link v-else to="/login"
          class="p-1.5 rounded text-white/50 hover:text-white hover:bg-white/10 transition-colors"
          title="Anmelden">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/>
          </svg>
        </router-link>
      </div>

      <!-- Username -->
      <div v-if="!collapsed && loggedIn" class="px-1 pb-0.5">
        <div class="text-white/40 text-[10px] uppercase tracking-wide">{{ adminUser }}</div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import NavLink from './SidebarNavLink.vue'
import { api, clearToken, isLoggedIn } from '../api.js'

const router    = useRouter()
const collapsed = ref(false)
const isDark    = ref(false)
const loggedIn  = ref(isLoggedIn())
const adminUser = ref('admin')
const time      = ref('')
const date      = ref('')
const timeShort = ref('')

const IC = {
  clock:  'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
  cog:    'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065zM15 12a3 3 0 11-6 0 3 3 0 016 0z',
  lock:   'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
}

const allLinks = [
  { to: '/dashboard', label: 'Status',       icon: IC.clock, authRequired: false },
  { to: '/config',    label: 'Konfiguration', icon: IC.cog,   authRequired: true  },
]

const visibleLinks = computed(() =>
  allLinks.filter(l => !l.authRequired || loggedIn.value)
)

function updateClock() {
  const now = new Date()
  time.value      = now.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  timeShort.value = now.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
  date.value      = now.toLocaleDateString('de-DE', { weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric' })
}

function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('chrony_theme', isDark.value ? 'dark' : 'light')
  window.dispatchEvent(new Event('storage'))
}

async function doLogout() {
  try { await api.logout() } catch {}
  clearToken()
  loggedIn.value = false
  router.push('/dashboard')
}

let clockTimer
onMounted(() => {
  isDark.value = localStorage.getItem('chrony_theme') === 'dark'
  loggedIn.value = isLoggedIn()
  updateClock()
  clockTimer = setInterval(updateClock, 1000)

  // Auth-Status aktualisieren wenn sich localStorage ändert
  window.addEventListener('storage', () => { loggedIn.value = isLoggedIn() })
})
onUnmounted(() => clearInterval(clockTimer))
</script>
