<template>
  <div class="bg-gray-900 border rounded-xl p-4 space-y-1"
    :class="highlight ? 'border-brand-700/50' : 'border-gray-800'">
    <p class="text-xs text-gray-500 uppercase tracking-wide">{{ label }}</p>
    <p class="font-mono text-sm font-semibold truncate" :class="valueColor">{{ value || '—' }}</p>
    <p v-if="sub" class="text-xs text-gray-500 truncate">{{ sub }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label:     String,
  value:     String,
  sub:       String,
  highlight: Boolean,
  color:     String,   // 'green' | 'yellow' | 'red' | 'gray'
})

const valueColor = computed(() => ({
  green:  'text-green-400',
  yellow: 'text-yellow-400',
  red:    'text-red-400',
  gray:   'text-gray-400',
}[props.color] || 'text-gray-100'))
</script>
