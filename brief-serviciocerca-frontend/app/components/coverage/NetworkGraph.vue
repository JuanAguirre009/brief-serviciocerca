<script setup lang="ts">
import CoverageGraph from './CoverageGraph.vue'
import type { CoverageNetwork } from '~/types/coverage'
defineProps<{ network: CoverageNetwork }>()
</script>
<template>
  <div class="network-graph">
    <ClientOnly><CoverageGraph :network="network" /></ClientOnly>
  </div>
</template>
<style scoped>
.network-graph {
  height: 480px;
  min-width: 0;
}
</style>
