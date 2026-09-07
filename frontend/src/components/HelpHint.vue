<template>
  <span class="group relative inline-flex align-middle" tabindex="0">
    <svg class="w-3.5 h-3.5 text-slate-300 dark:text-slate-600 group-hover:text-slate-500 dark:group-hover:text-slate-400 group-focus:text-slate-500 cursor-help transition-colors outline-none"
      viewBox="0 0 20 20" fill="none" stroke="currentColor">
      <circle cx="10" cy="10" r="8.25" stroke-width="1.5"/>
      <line x1="10" y1="9" x2="10" y2="14.2" stroke-width="1.5" stroke-linecap="round"/>
      <circle cx="10" cy="6.3" r="0.9" fill="currentColor" stroke="none"/>
    </svg>
    <span class="pointer-events-none absolute z-20 hidden group-hover:block group-focus:block
                 left-1/2 -translate-x-1/2 w-56 normal-case font-normal leading-snug
                 rounded-lg bg-slate-800 dark:bg-slate-700 text-white text-[11px] px-2.5 py-1.5 shadow-lg"
      :class="placement === 'bottom' ? 'top-full mt-1.5' : 'bottom-full mb-1.5'">
      {{ text }}
    </span>
  </span>
</template>

<script setup>
defineProps({
  text:      { type: String, required: true },
  // 'top' (Standard) für frei stehende Elemente; 'bottom' für Tabellen-Header,
  // damit das Tooltip nicht vom `overflow-hidden` der Karte nach oben abgeschnitten wird.
  placement: { type: String, default: 'top' },
})
</script>
