<script setup lang="ts">
import { LayoutDashboard, Network, Radar, Route } from 'lucide-vue-next'
const navigation = [
  { label: 'Resumen', to: '/', icon: LayoutDashboard },
  { label: 'Cobertura', to: '/coverage', icon: Radar },
  { label: 'Red', to: '/network', icon: Network },
]
</script>
<template>
  <aside class="sidebar">
    <NuxtLink to="/" class="brand" aria-label="ServicioCerca, inicio">
      <span class="brand-mark"><Route :size="22" /></span>
      <span class="brand-copy"
        ><strong>ServicioCerca</strong><small>Operations</small></span
      >
    </NuxtLink>
    <div class="sidebar-section">
      <span class="eyebrow section-label">OPERACIÓN</span>
      <nav aria-label="Navegación principal">
        <NuxtLink
          v-for="item in navigation"
          :key="item.to"
          :to="item.to"
          class="navigation-item"
          :title="item.label"
          :aria-label="item.label"
          exact-active-class="navigation-item--active"
        >
          <component
            :is="item.icon"
            :size="19"
            :stroke-width="1.8"
            aria-hidden="true"
          />
          <span>{{ item.label }}</span>
        </NuxtLink>
      </nav>
    </div>
    <div class="engine-panel">
      <Radar :size="18" aria-hidden="true" />
      <div>
        <strong>Motor de cobertura</strong><small>Feature 2</small
        ><span class="engine-status">● BFS disponible</span>
      </div>
    </div>
  </aside>
</template>
<style scoped>
.sidebar {
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  height: 100dvh;
  padding: 24px 16px 18px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 6px 25px;
  text-decoration: none;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border);
}
.brand-mark {
  display: grid;
  place-items: center;
  flex: 0 0 36px;
  height: 36px;
  color: white;
  background: var(--primary);
  border-radius: 10px;
}
.brand-copy {
  display: grid;
  gap: 3px;
}
.brand-copy strong {
  font-size: 1.05rem;
  letter-spacing: -0.03em;
}
.brand-copy small {
  color: var(--text-secondary);
  font-size: 0.76rem;
}
.sidebar-section {
  margin-top: 26px;
}
.section-label {
  margin-left: 12px;
}
nav {
  display: grid;
  gap: 5px;
}
.navigation-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 44px;
  padding: 10px 12px;
  border-radius: 7px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.92rem;
  font-weight: 600;
}
.navigation-item:hover {
  background: var(--border-soft);
}
.navigation-item--active {
  background: var(--bg-selected);
  color: var(--primary-hover);
}
.navigation-item--active::before {
  content: '';
  position: absolute;
  left: -16px;
  width: 3px;
  height: 22px;
  border-radius: 0 3px 3px 0;
  background: var(--primary);
}
.engine-panel {
  display: flex;
  gap: 10px;
  margin-top: auto;
  padding: 14px 10px 0;
  border-top: 1px solid var(--border);
  color: var(--text-secondary);
}
.engine-panel div {
  display: grid;
  gap: 4px;
}
.engine-panel strong {
  font-size: 0.8rem;
  color: var(--text-primary);
}
.engine-panel small,
.engine-status {
  font-size: 0.74rem;
}
.engine-status {
  color: var(--success);
  margin-top: 5px;
}
@media (max-width: 1100px) {
  .sidebar {
    padding-inline: 12px;
    align-items: center;
  }
  .brand {
    padding-inline: 0;
  }
  .brand-copy,
  .section-label,
  .navigation-item span,
  .engine-panel {
    display: none;
  }
  .navigation-item {
    justify-content: center;
    width: 48px;
  }
  .navigation-item--active::before {
    left: -14px;
  }
}
@media (max-width: 760px) {
  .sidebar {
    position: static;
    flex-direction: row;
    height: auto;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
    border-right: 0;
  }
  .brand {
    padding: 0;
    border: 0;
  }
  .sidebar-section {
    margin: 0 0 0 auto;
  }
  nav {
    display: flex;
  }
  .navigation-item {
    width: auto;
    gap: 6px;
    padding: 8px;
    font-size: 0.78rem;
  }
  .navigation-item span {
    display: inline;
  }
  .navigation-item--active::before {
    display: none;
  }
}
</style>
