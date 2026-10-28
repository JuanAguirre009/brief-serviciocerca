<script setup lang="ts">
import { Layers } from 'lucide-vue-next'
const route = useRoute()
const title = computed(() =>
  route.path.startsWith('/coverage')
    ? 'Consulta de cobertura'
    : route.path.startsWith('/network')
      ? 'Configuración de red'
      : 'Centro de operaciones',
)
</script>
<template>
  <header class="topbar">
    <div class="breadcrumb">
      <span>Operación</span><span aria-hidden="true">/</span>
      <h1>{{ title }}</h1>
    </div>
    <span class="workspace-label"
      ><Layers :size="15" aria-hidden="true" /> ServicioCerca</span
    >
  </header>
</template>
<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 60px;
  padding: 14px 24px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
}
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}
.breadcrumb > span {
  color: var(--text-muted);
  font-size: 0.83rem;
}
h1 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
}
.workspace-label {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--text-secondary);
  font-size: 0.8rem;
}
@media (max-width: 760px) {
  .topbar {
    padding: 12px 16px;
    min-height: 52px;
  }
  .workspace-label {
    display: none;
  }
}
@media (max-width: 420px) {
  .breadcrumb > span {
    display: none;
  }
}
</style>
