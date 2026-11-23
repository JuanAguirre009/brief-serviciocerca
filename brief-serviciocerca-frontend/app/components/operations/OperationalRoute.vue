<script setup lang="ts">
import { ArrowDown, MapPin } from 'lucide-vue-next'

import type { RouteSegment } from '~/types/coverage'


interface Props {
  segments: RouteSegment[]
}

const props = defineProps<Props>()


const hasSegments = computed(() => props.segments.length > 0)


const originNode = computed(() => {
  return props.segments[0]?.origin ?? null
})


const destinationNode = computed(() => {
  return props.segments[props.segments.length - 1]?.destination ?? null
})
</script>


<template>
  <section
    v-if="hasSegments"
    class="operational-route"
    aria-label="Recorrido operacional"
  >
    <div class="operational-route__endpoint operational-route__endpoint--origin">
      <span class="operational-route__label">Salida</span>

      <strong class="operational-route__name">
        <MapPin :size="16" aria-hidden="true" />

        {{ originNode?.name }}
      </strong>

      <small class="operational-route__code">{{ originNode?.code }}</small>
    </div>

    <ol class="operational-route__segments">
      <li
        v-for="(segment, index) in segments"
        :key="`${index}-${segment.origin.id}-${segment.destination.id}`"
        class="operational-route__segment"
      >
        <div class="operational-route__arrow">
          <ArrowDown :size="16" aria-hidden="true" />

          <span class="operational-route__minutes">
            {{ segment.estimated_minutes }} min
          </span>
        </div>

        <div
          v-if="index < segments.length - 1"
          class="operational-route__stop"
        >
          <strong class="operational-route__name">
            {{ segment.destination.name }}
          </strong>

          <small class="operational-route__code">
            {{ segment.destination.code }}
          </small>
        </div>
      </li>
    </ol>

    <div class="operational-route__endpoint operational-route__endpoint--destination">
      <span class="operational-route__label">Destino</span>

      <strong class="operational-route__name">
        <MapPin :size="16" aria-hidden="true" />

        {{ destinationNode?.name }}
      </strong>

      <small class="operational-route__code">{{ destinationNode?.code }}</small>
    </div>
  </section>

  <div
    v-else
    class="operational-route__empty"
  >
    <p>No hay un recorrido para mostrar.</p>
  </div>
</template>


<style scoped>
.operational-route {
  display: grid;
  gap: 4px;
}

.operational-route__endpoint {
  display: grid;
  gap: 4px;
  padding: 16px;
  border-radius: var(--radius);
  background: var(--bg-surface-soft);
}

.operational-route__endpoint--origin {
  border-left: 4px solid var(--primary);
}

.operational-route__endpoint--destination {
  border-left: 4px solid var(--success);
}

.operational-route__label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.operational-route__name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.05rem;
  color: var(--text-primary);
  overflow-wrap: anywhere;
}

.operational-route__name svg {
  flex-shrink: 0;
  color: var(--primary);
}

.operational-route__endpoint--destination .operational-route__name svg {
  color: var(--success);
}

.operational-route__code {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.operational-route__segments {
  display: grid;
  gap: 4px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.operational-route__segment {
  display: grid;
  gap: 10px;
  padding: 8px 0 8px 16px;
}

.operational-route__arrow {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
}

.operational-route__arrow svg {
  flex-shrink: 0;
  color: var(--primary);
}

.operational-route__minutes {
  padding: 3px 8px;
  border-radius: 5px;
  background: var(--primary-soft);
  color: var(--primary-hover);
}

.operational-route__stop {
  display: grid;
  gap: 3px;
  padding-left: 26px;
}

.operational-route__empty {
  display: grid;
  place-items: center;
  min-height: 160px;
  padding: 24px;
  border-radius: var(--radius);
  background: var(--bg-surface-soft);
  color: var(--text-secondary);
  text-align: center;
}

.operational-route__empty p {
  margin: 0;
}

@media (max-width: 600px) {
  .operational-route__segment {
    padding-left: 8px;
  }

  .operational-route__stop {
    padding-left: 18px;
  }
}
</style>
