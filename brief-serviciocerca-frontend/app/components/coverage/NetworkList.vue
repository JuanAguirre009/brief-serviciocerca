<script setup lang="ts">
import type { CoverageNetwork } from '~/types/coverage'


defineProps<{
  network: CoverageNetwork
}>()
</script>


<template>
  <section class="card network">
    <div class="section-header">
      <div>
        <h2>Red actual</h2>

        <p>
          Configuración operativa registrada.
        </p>
      </div>
    </div>

    <div class="network-grid">
      <div class="network-column">
        <h3>Nodos</h3>

        <div
          v-if="!network.nodes.length"
          class="empty-state"
        >
          <p class="empty">
            No hay nodos registrados.
          </p>

          <p class="hint">
            Usa el formulario de la izquierda para registrar bases y zonas.
          </p>
        </div>

        <ul v-else>
          <li
            v-for="node in network.nodes"
            :key="node.id"
          >
            <strong>{{ node.code }}</strong>

            — {{ node.name }}

            <span
              class="tag"
              :class="node.type.toLowerCase()"
            >
              {{ node.type === 'BASE' ? 'Base' : 'Zona' }}
            </span>
          </li>
        </ul>
      </div>


      <div class="network-column">
        <h3>Técnicos</h3>

        <div
          v-if="!network.technicians.length"
          class="empty-state"
        >
          <p class="empty">
            No hay técnicos registrados.
          </p>

          <p class="hint">
            Registra técnicos asociados a una base.
          </p>
        </div>

        <ul v-else>
          <li
            v-for="technician in network.technicians"
            :key="technician.id"
          >
            <strong>
              {{ technician.code }}
            </strong>

            — {{ technician.name }}

            <br>

            Base:
            {{ technician.base.code }}

            <span
              class="tag"
              :class="technician.is_available ? 'available' : 'unavailable'"
            >
              {{
                technician.is_available
                  ? 'Disponible'
                  : 'No disponible'
              }}
            </span>
          </li>
        </ul>
      </div>


      <div class="network-column">
        <h3>Conexiones</h3>

        <div
          v-if="!network.connections.length"
          class="empty-state"
        >
          <p class="empty">
            No hay conexiones registradas.
          </p>

          <p class="hint">
            Conecta nodos para definir rutas operativas.
          </p>
        </div>

        <ul v-else>
          <li
            v-for="connection in network.connections"
            :key="connection.id"
          >
            <strong>
              {{ connection.origin.code }}
            </strong>

            {{
              connection.is_bidirectional
                ? ' ↔ '
                : ' → '
            }}

            <strong>
              {{ connection.destination.code }}
            </strong>

            —

            {{ connection.estimated_minutes }} min
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>


<style scoped>
.network-column {
  min-width: 0;
}

.empty-state {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.tag.base {
  background: #111827;
  color: white;
}

.tag.zone {
  background: #3b82f6;
  color: white;
}

.tag.available {
  background: #d1fae5;
  color: #065f46;
}

.tag.unavailable {
  background: #fee2e2;
  color: #991b1b;
}
</style>
