<script setup lang="ts">
import {
  Clock3,
  GitBranch,
  LayoutDashboard,
  Network,
  Radar,
  Route,
} from 'lucide-vue-next'

const navigation = [
  {
    label: 'Consola de operación',
    to: '/operations',
    icon: Route,
    primary: true,
  },
  {
    label: 'Resumen',
    to: '/',
    icon: LayoutDashboard,
    primary: false,
  },
  {
    label: 'Cobertura',
    to: '/coverage',
    icon: Radar,
    primary: false,
  },
  {
    label: 'Rutas óptimas',
    to: '/routes',
    icon: GitBranch,
    primary: false,
  },
  {
    label: 'Red',
    to: '/network',
    icon: Network,
    primary: false,
  },
]
</script>

<template>
  <aside class="sidebar">
    <NuxtLink
      to="/"
      class="brand"
      aria-label="ServicioCerca, inicio"
    >
      <span class="brand-mark">
        <Route :size="22" aria-hidden="true" />
      </span>

      <span class="brand-copy">
        <strong>ServicioCerca</strong>
        <small>Operations</small>
      </span>
    </NuxtLink>

    <div class="sidebar-section">
      <span class="eyebrow section-label">
        NAVEGACIÓN
      </span>

      <nav aria-label="Navegación principal">
        <NuxtLink
          v-for="item in navigation"
          :key="item.to"
          :to="item.to"
          class="navigation-item"
          :class="{
            'navigation-item--primary': item.primary,
          }"
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
      <Clock3 :size="18" aria-hidden="true" />

      <div>
        <strong>Planificación por tiempo</strong>
        <small>Dijkstra + BFS</small>
        <span class="engine-status">
          Tiempos estimados de la red
        </span>
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
  min-width: 0;
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
  width: 36px;
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
  min-width: 0;
  margin-top: 26px;
}

.section-label {
  margin-left: 12px;
}

nav {
  display: grid;
  gap: 6px;
}

.navigation-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 44px;
  padding: 10px 12px;
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  transition:
    background-color 150ms ease,
    color 150ms ease;
}

.navigation-item:hover {
  background: var(--border-soft);
}

.navigation-item--primary {
  margin-bottom: 8px;
  background: var(--primary-soft);
  color: var(--primary-hover);
  border-color: var(--bg-selected);
  font-weight: 700;
}

.navigation-item--primary:hover {
  background: var(--bg-selected);
}

.navigation-item--active,
.navigation-item.navigation-item--active {
  background: var(--bg-selected);
  color: var(--primary-hover);
  border-color: var(--bg-selected);
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

.engine-panel > svg {
  flex-shrink: 0;
  color: var(--primary);
}

.engine-panel > div {
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
    align-items: center;
    height: auto;
    padding: 10px 12px;
    gap: 10px;
    border-right: 0;
    border-bottom: 1px solid var(--border);
  }

  .brand {
    flex-shrink: 0;
    padding: 0;
    border: 0;
  }

  .sidebar-section {
    flex: 1;
    min-width: 0;
    margin: 0;
  }

  nav {
    display: flex;
    gap: 4px;
    overflow-x: auto;
    padding: 3px 2px;
    scrollbar-width: thin;
  }

  .navigation-item {
    flex: 0 0 auto;
    flex-direction: column;
    justify-content: center;
    gap: 4px;
    width: 94px;
    min-height: 52px;
    padding: 6px 5px;
    font-size: 0.72rem;
    text-align: center;
  }

  .navigation-item span {
    display: block;
  }

  .navigation-item--primary {
    margin-bottom: 0;
  }

  .navigation-item--active::before {
    display: none;
  }
}

@media (max-width: 600px) {
  .navigation-item {
    width: 82px;
    font-size: 0.68rem;
  }

  .brand-mark {
    flex-basis: 34px;
    width: 34px;
    height: 34px;
  }
}
</style>
