<script setup lang="ts">
import type {
  CoverageNetwork,
} from '~/types/coverage'


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
      <div>
        <h3>Nodos</h3>

        <p
          v-if="!network.nodes.length"
          class="empty"
        >
          No hay nodos registrados.
        </p>

        <ul v-else>
          <li
            v-for="node in network.nodes"
            :key="node.id"
          >
            <strong>{{ node.code }}</strong>

            — {{ node.name }}

            <span class="tag">
              {{ node.type }}
            </span>
          </li>
        </ul>
      </div>


      <div>
        <h3>Técnicos</h3>

        <p
          v-if="!network.technicians.length"
          class="empty"
        >
          No hay técnicos registrados.
        </p>

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


      <div>
        <h3>Conexiones</h3>

        <p
          v-if="!network.connections.length"
          class="empty"
        >
          No hay conexiones registradas.
        </p>

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