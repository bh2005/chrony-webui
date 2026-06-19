<template>
  <div class="bg-white dark:bg-slate-800 border rounded-xl p-4 shadow-sm space-y-1 transition-colors"
    :class="highlight ? 'border-ks-300 dark:border-ks-700' : 'border-slate-200 dark:border-slate-700'">
    <p class="text-xs text-slate-400 dark:text-slate-500 uppercase tracking-wide font-medium">{{ label }}</p>
    <p class="font-mono text-sm font-semibold truncate" :class="valueColor">{{ value || '—' }}</p>
    <p v-if="sub" class="text-xs text-slate-400 dark:text-slate-500 truncate">{{ sub }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label:     String,
  value:     String,
  sub:       String,
  highlight: Boolean,
  color:     String,
})

const valueColor = computed(() => ({
  green:  'text-green-600 dark:text-green-400',
  yellow: 'text-amber-600 dark:text-amber-400',
  red:    'text-red-600 dark:text-red-400',
  gray:   'text-slate-400',
}[props.color] || 'text-slate-800 dark:text-slate-100'))
</script>
