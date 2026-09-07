<template>
  <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-4 shadow-sm">
    <div class="flex items-center justify-between mb-2 gap-3">
      <h2 class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide">{{ title }}</h2>
      <div class="flex items-baseline gap-2 text-right">
        <span v-if="points.length" class="text-xs font-mono text-slate-400 dark:text-slate-500">
          min {{ fmt(minValue) }} · max {{ fmt(maxValue) }}
        </span>
        <span class="text-sm font-mono font-bold text-slate-700 dark:text-slate-200">{{ lastLabel }}</span>
      </div>
    </div>

    <svg v-if="points.length >= 2" :viewBox="`0 0 ${width} ${height}`" class="w-full" :height="height" preserveAspectRatio="none">
      <polygon :points="areaPoints" :fill="strokeColor" opacity="0.12" />
      <polyline :points="linePoints" fill="none" :stroke="strokeColor" stroke-width="2"
        stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
    </svg>
    <div v-else class="h-[60px] flex items-center justify-center text-xs text-slate-400 dark:text-slate-500 italic">
      Sammle Daten…
    </div>

    <!-- Zeitraum (Start/Ende der angezeigten Daten) -->
    <div class="flex justify-between text-xs text-slate-400 dark:text-slate-500 mt-1 font-mono">
      <span>{{ startTimeLabel }}</span>
      <span>{{ endTimeLabel }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title:      { type: String, required: true },
  values:     { type: Array,  required: true },   // Array<number|null>
  timestamps: { type: Array,  default: () => [] }, // Array<number> (Unix-Sekunden), parallel zu values
  unit:       { type: String, default: '' },
  color:      { type: String, default: 'ks' },    // 'ks' | 'green' | 'amber'
  digits:     { type: Number, default: 1 },
})

const width  = 300
const height = 60

const palette = { ks: '#0284c7', green: '#22c55e', amber: '#f59e0b' }
const strokeColor = computed(() => palette[props.color] || palette.ks)

// Nur gültige (nicht-null) Werte für Skalierung/Linie verwenden, Zeitstempel parallel mitführen
const entries = computed(() =>
  props.values
    .map((v, i) => ({ v, ts: props.timestamps[i] }))
    .filter(e => e.v !== null && e.v !== undefined)
)
const points = computed(() => entries.value.map(e => e.v))

const bounds = computed(() => {
  if (points.value.length === 0) return { min: 0, max: 1 }
  let min = Math.min(...points.value)
  let max = Math.max(...points.value)
  if (min === max) { min -= 1; max += 1 }        // flache Linie vermeiden
  const pad = (max - min) * 0.15
  return { min: min - pad, max: max + pad }
})

function coords() {
  const n = points.value.length
  if (n < 2) return []
  const { min, max } = bounds.value
  const span = max - min || 1
  return points.value.map((v, i) => {
    const x = (i / (n - 1)) * width
    const y = height - ((v - min) / span) * height
    return { x, y, v }
  })
}

const linePoints = computed(() => coords().map(({ x, y }) => `${x},${y}`).join(' '))
const areaPoints  = computed(() => {
  const c = coords()
  if (c.length < 2) return ''
  return `0,${height} ` + c.map(({ x, y }) => `${x},${y}`).join(' ') + ` ${width},${height}`
})

const minValue = computed(() => points.value.length ? Math.min(...points.value) : null)
const maxValue = computed(() => points.value.length ? Math.max(...points.value) : null)

function fmt(v) {
  return v === null || v === undefined ? '—' : `${v.toFixed(props.digits)}${props.unit}`
}
const lastLabel = computed(() => {
  const last = points.value[points.value.length - 1]
  return last === undefined ? '—' : fmt(last)
})

function timeLabel(ts) {
  if (!ts) return ''
  return new Date(ts * 1000).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
}
const startTimeLabel = computed(() => timeLabel(entries.value[0]?.ts))
const endTimeLabel   = computed(() => timeLabel(entries.value[entries.value.length - 1]?.ts))
</script>
