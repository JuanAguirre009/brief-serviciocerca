# Coverage

Módulo responsable de representar y configurar la red operativa de

cobertura de ServicioCerca.

## Modelo del grafo

La red se representa mediante nodos y conexiones.

### Nodos

Un `CoverageNode` representa una ubicación operativa.

Existen dos tipos:

- `BASE`: base desde la que operan los técnicos.

- `ZONE`: zona donde puede prestarse un servicio.

Los técnicos no son nodos del grafo.

Un técnico representa un recurso operativo asociado a una base.

Esta decisión permite que el grafo responda preguntas relacionadas con

conectividad entre ubicaciones sin mezclar recursos humanos con lugares.

## Técnicos

Un `Technician` pertenece a una `BASE`.

La disponibilidad se representa inicialmente mediante:

`is_available`

No se modelan turnos, ubicación en tiempo real ni asignación automática,

ya que no hacen parte del alcance inicial.

## Conexiones

Una `Connection` representa una arista entre dos nodos.

Ejemplo:

```text

BASE-NORTE -> ZONA-001
 