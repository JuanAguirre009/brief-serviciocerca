# ServicioCerca — Feature 2: Consulta de cobertura

## 1. Objetivo

Feature 2 permite determinar si una zona de servicio puede alcanzarse
desde una base operacional.

También permite consultar todas las zonas alcanzables desde una base.

En esta feature, cobertura significa existencia de al menos un camino
válido dentro del grafo respetando la dirección de las conexiones.

El costo de las conexiones no interviene en esta decisión.

---

## 2. Algoritmo utilizado

Se utiliza Breadth-First Search (BFS), implementado directamente por
el equipo.

BFS explora el grafo por niveles utilizando una cola.

Para cada consulta se mantiene:

- conjunto de nodos visitados;
- orden real de descubrimiento;
- relación padre-hijo para reconstruir el camino encontrado.

---

## 3. Justificación de BFS

Feature 2 busca determinar alcance y no optimización de costo.

BFS permite:

- determinar si existe un camino;
- obtener todos los nodos alcanzables desde un origen;
- evitar ciclos mediante control de visitados;
- producir una traza legible del recorrido;
- reconstruir un camino encontrado.

Los pesos `estimated_minutes` no se utilizan en Feature 2.

La optimización basada en costos pertenece a Feature 3.

---

## 4. Direccionalidad

Las conexiones respetan las reglas definidas en Feature 1.

Una conexión:

```text
A → B
```

permite recorrer A hacia B.

No permite automáticamente:

```text
B → A
```

Una conexión bidireccional:

```text
A ↔ B
```

permite recorrer ambos sentidos.

---

## 5. Arquitectura

El flujo de una consulta es:

```text
Frontend
   ↓
GET /api/coverage/reachability/
   ↓
CoverageReachabilityAPIView
   ↓
reachability.py
   ↓
build_adjacency()
   ↓
bfs_reachability()
   ↓
PostgreSQL
```

Las responsabilidades están separadas:

### algorithms/graph.py

Construye la lista de adyacencia respetando la dirección de las
conexiones.

### algorithms/bfs.py

Implementa BFS y devuelve:

```text
reachable
visited
path
```

### reachability.py

Convierte los datos almacenados en la base en una consulta de
cobertura y transforma los IDs del algoritmo en información de
negocio.

### views.py

Recibe solicitudes HTTP, valida los parámetros y delega la operación a
la capa de negocio.

---

## 6. Endpoint

```http
GET /api/coverage/reachability/
```

### Consultar una zona

```http
GET /api/coverage/reachability/?origin_id=1&destination_id=5
```

Devuelve:

- estado de cobertura;
- origen;
- destino;
- camino encontrado;
- traza BFS;
- cantidad de nodos visitados;
- mensaje legible.

### Consultar alcance completo

```http
GET /api/coverage/reachability/?origin_id=1
```

Devuelve:

- base consultada;
- cantidad de zonas alcanzables;
- zonas alcanzables;
- orden de recorrido BFS;
- mensaje legible.

---

## 7. Casos sin cobertura

Una zona que no puede alcanzarse produce una respuesta válida.

Ejemplo:

```json
{
  "covered": false,
  "path": [],
  "message": "La zona solicitada no es alcanzable desde la base."
}
```

La API responde HTTP 200 porque la consulta fue procesada
correctamente y el resultado de negocio es que no existe cobertura.

---

## 8. Errores

Se manejan explícitamente casos como:

- origen inexistente;
- destino inexistente;
- origen que no corresponde a una BASE;
- destino que no corresponde a una ZONE;
- parámetros inválidos;
- zona sin conexiones;
- red desconectada.

---

## 9. Traza BFS

Feature 2 conserva el orden real en el que BFS descubre los nodos.

Ejemplo:

```text
Base Norte
   ↓
Laureles
   ↓
Estadio
   ↓
Belén
```

La respuesta incluye esta información mediante:

```json
{
  "traversal_order": []
}
```

Esto permite demostrar el funcionamiento del algoritmo y posteriormente
representarlo visualmente en el frontend.

---

## 10. Pruebas

Las pruebas de la aplicación se ejecutan desde Docker:

```bash
docker compose exec web python manage.py test apps.coverage
```

Las pruebas específicas de la API de cobertura:

```bash
docker compose exec web python manage.py test apps.coverage.tests.test_reachability_views
```

---

## 11. Pruebas de aceptación

El script de aceptación es:

```text
scripts/acceptance_feature2.py
```

Se ejecuta desde Docker:

```bash
docker compose exec web python scripts/acceptance_feature2.py
```

Genera evidencia automáticamente en:

```text
evidence/acceptance/
```

La aceptación valida:

- cobertura existente;
- camino encontrado;
- traza BFS;
- listado de zonas alcanzables;
- zona desconectada;
- origen inexistente;
- respeto por la direccionalidad;
- validación del tipo de nodo.

Una ejecución correcta finaliza con:

```text
FEATURE 2: ACEPTACION EXITOSA
```

---

## 12. Alcance de Feature 2

Feature 2 resuelve alcance.

No calcula:

- menor tiempo;
- menor costo;
- mejor alternativa;
- ruta óptima basada en pesos.

Estas responsabilidades corresponden al Feature 3.
