<template>
  <router-link v-slot="{ href, navigate, isActive }" :to="link.to" custom>
    <a
      :href="href"
      @click="navigate"
      class="flex items-center gap-3 px-2 py-1.5 rounded-lg transition-colors text-sm w-full"
      :class="isActive
        ? 'bg-white/20 text-white font-medium'
        : 'text-white/65 hover:text-white hover:bg-white/10'"
      :title="collapsed ? link.label : undefined"
    >
      <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" :d="link.icon"/>
      </svg>
      <span v-if="!collapsed" class="truncate">{{ link.label }}</span>
    </a>
  </router-link>
</template>

<script setup>
defineProps({
  link:      { type: Object,  required: true },
  collapsed: { type: Boolean, default: false },
})
</script>
