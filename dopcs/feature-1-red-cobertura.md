# ServicioCerca — Feature 1: Red de Cobertura

## 1. Descripción del proyecto

ServicioCerca es un sistema pensado para apoyar la operación de una empresa
que coordina técnicos de mantenimiento en diferentes zonas de una ciudad.

Cuando se recibe una solicitud de servicio, la empresa necesita identificar
qué zonas pueden ser atendidas desde una base y, posteriormente, determinar
alternativas de atención.

El objetivo general del proyecto es organizar la información de bases,
zonas, técnicos y conexiones para representar la operación mediante una red
que posteriormente pueda utilizarse para consultar cobertura y calcular
alternativas de atención.

---

## 2. Usuarios principales

### Coordinador de operaciones

Es responsable de configurar la información necesaria para construir la red
de cobertura.

Puede registrar:

- bases;
- zonas;
- técnicos;
- conexiones entre ubicaciones.

### Operador de atención

En funcionalidades posteriores podrá consultar:

- si una zona tiene cobertura;
- qué ubicaciones pueden alcanzarse desde una base;
- cuál es una alternativa de atención;
- cuál es una ruta de menor costo.

---

# 3. Feature 1 — Red de Cobertura

## Objetivo

El Feature 1 tiene como objetivo construir y configurar la red de cobertura
sobre la cual trabajarán las siguientes funcionalidades del proyecto.

Antes de realizar búsquedas de cobertura o calcular rutas, el sistema debe
conocer:

- qué ubicaciones existen;
- qué técnicos pertenecen a cada base;
- qué conexiones existen entre las ubicaciones;
- cuánto cuesta recorrer cada conexión;
- en qué dirección puede recorrerse cada conexión.

Por esta razón, Feature 1 se concentra en registrar, validar y consultar la
estructura de la red.

---

# 4. Modelo del grafo

ServicioCerca representa la red de cobertura mediante un grafo.

## Nodos

Los nodos representan ubicaciones dentro de la operación.

Existen dos tipos de nodos:

### BASE

Representa una ubicación desde donde operan los técnicos.

Ejemplo:

```text
BASE-NORTE
Base Norte