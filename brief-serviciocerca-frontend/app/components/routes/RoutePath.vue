<script setup lang="ts">
import { ArrowRight } from 'lucide-vue-next'
import type { RouteNode } from '~/types/coverage'
defineProps<{ nodes: RouteNode[]; label: string }>()
</script>

<template>
  <ol class="route-path" :aria-label="label">
    <li v-for="(node, index) in nodes" :key="`${index}-${node.id}`">
      <ArrowRight v-if="index" :size="13" aria-hidden="true" />
      <span :title="node.code">{{ node.name }}</span>
    </li>
  </ol>
</template>

<style scoped>
.route-path {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}
li {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  max-width: 100%;
}
li svg {
  flex-shrink: 0;
  color: var(--text-muted);
}
li span {
  padding: 5px 8px;
  border-radius: 5px;
  color: var(--primary-hover);
  background: var(--primary-soft);
  font-size: 0.8rem;
  overflow-wrap: anywhere;
}
</style>
