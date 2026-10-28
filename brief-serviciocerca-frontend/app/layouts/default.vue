<script setup lang="ts">
import AppHeader from '~/components/layout/AppHeader.vue'
import AppSidebar from '~/components/layout/AppSidebar.vue'
</script>
<template>
  <div class="app-shell">
    <a href="#workspace" class="skip-link">Saltar al contenido</a>
    <AppSidebar />
    <div class="app-workspace">
      <AppHeader />
      <main id="workspace" class="app-content" tabindex="-1"><slot /></main>
    </div>
  </div>
</template>
<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 244px minmax(0, 1fr);
  min-height: 100dvh;
}
.app-workspace {
  min-width: 0;
}
.app-content {
  padding: 24px;
}
.skip-link {
  position: fixed;
  top: -80px;
  left: 16px;
  z-index: 100;
  padding: 12px;
  background: var(--bg-surface);
}
.skip-link:focus {
  top: 12px;
}
@media (max-width: 1100px) {
  .app-shell {
    grid-template-columns: 76px minmax(0, 1fr);
  }
}
@media (max-width: 760px) {
  .app-shell {
    display: block;
  }
  .app-content {
    padding: 16px;
  }
}
</style>
