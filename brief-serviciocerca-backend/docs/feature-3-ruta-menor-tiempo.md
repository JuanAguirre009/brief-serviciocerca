# ServicioCerca - Feature 3: Ruta de menor tiempo (Dijkstra)

## 1. Objetivo

El Feature 3 identifica la ruta con **menor tiempo total estimado** entre una base operativa (`BASE`) y una zona de servicio (`ZONE`). El resultado muestra el camino, el tiempo total, los segmentos y una traza del recorrido. La API no inventa tiempos ni calcula tiempos en tiempo real.

## 2. Diferencia entre BFS (Feature 2) y Dijkstra (Feature 3)

| Caracteristica | BFS (Feature 2) | Dijkstra (Feature 3) |
| --- | --- | --- |
| Pregunta | Existe un camino? | Cual camino suma menos minutos? |
| Datos | Conexiones y direcciones | Conexiones, direcciones y pesos |
| Algoritmo | Cola y recorrido por niveles | Cola de prioridad y relajacion de distancias |
| Resultado principal | `covered`, `path`, `traversal_order` | `reachable`, `path`, `segments`, `total_minutes`, `traversal_order` |
| Eleccion | Puede encontrar el camino con menos saltos | Encuentra la ruta de menor suma de pesos positivos |

Ejemplo: si la conexion directa toma 30 minutos, pero la alternativa tiene tres tramos de 5, 7 y 8 minutos, BFS puede escoger la directa por tener un salto; Dijkstra escoge **20 minutos**.

## 3. Significado de `estimated_minutes`

Es un peso entero estrictamente positivo asociado a cada conexion; representa el tiempo estimado para recorrerla. En Feature 3, el costo de una ruta es la suma de sus pesos. No es distancia geometrica ni representa trafico en vivo.

## 4. Lista de adyacencia ponderada

`apps/coverage/algorithms/weighted_graph.py` genera una estructura:

```python
{
    1: [(2, 5), (4, 30)],
    2: [(3, 7)],
    3: [(4, 8)],
}
```

En cada par `(id_destino, minutos)`, el segundo valor es el peso. La estructura se construye con las conexiones persistidas en PostgreSQL.

## 5. Respeto por la direccion de las conexiones

- Conexion dirigida `A -> B`: permite viajar desde A hacia B, no automaticamente desde B hacia A.
- Conexion bidireccional `A <-> B`: el grafo incorpora ambos arcos con el mismo tiempo estimado.
- Los nodos aislados son validos y pueden devolver `reachable: false`.

## 6. Funcionamiento de Dijkstra

`algorithms/dijkstra.py` implementa el algoritmo sin depender de Django. Mantiene distancias conocidas, mapa de padres, cola de prioridad y conjunto de nodos ya asentados. En cada paso procesa el nodo pendiente con menor distancia; al encontrar una alternativa mas barata actualiza la distancia y su padre. Al finalizar reconstruye el camino de menor costo.

Como todos los pesos son positivos, este procedimiento encuentra la ruta minima en minutos. `traversal_order` registra el **orden de asentamiento** de nodos, no el orden de la primera vez que fueron descubiertos.

## 7. Integracion con PostgreSQL

Las conexiones y nodos definidos en Feature 1 residen en PostgreSQL. `shortest_route.py` consulta `CoverageNode` y `Connection`, construye la representacion ponderada y ejecuta Dijkstra. Las consultas de este feature son de solo lectura: no generan conexiones, modelos ni migraciones.

## 8. Responsabilidad de `shortest_route.py`

Este archivo existe antes de la tarea de API. Su funcion `calculate_shortest_route(origin_id, destination_id)`:

1. Busca los nodos por ID y valida que existan.
2. Comprueba que el origen sea `BASE` y el destino sea `ZONE`.
3. Lee las conexiones con sus minutos y direcciones.
4. Invoca `build_weighted_adjacency()` y `dijkstra_shortest_path()`.
5. Convierte IDs a objetos de negocio y genera los segmentos, tiempo total y mensaje.

No modificamos este archivo para implementar el endpoint.

## 9. Endpoint REST y arquitectura

```http
GET /api/coverage/shortest-route/?origin_id=1&destination_id=4
```

```text
Cliente HTTP
   |
   v
GET /api/coverage/shortest-route/
   |
   v
CoverageShortestRouteAPIView (views.py)
   |
   v
ShortestRouteQuerySerializer (serializers.py)
   |
   v
calculate_shortest_route() (shortest_route.py)
   |
   +--> PostgreSQL (nodos y conexiones)
   +--> build_weighted_adjacency() (weighted_graph.py)
   +--> dijkstra_shortest_path() (dijkstra.py)
   |
   v
JSON + HTTP 200 o error de validacion HTTP 400
```

El serializer valida los dos parametros como enteros positivos obligatorios. La vista solo delega y convierte las excepciones `DjangoValidationError` a errores HTTP de DRF.

## 10. Ejemplo de consulta

Red de ejemplo: `Base Norte -> Belen = 30`, o `Base Norte -> Laureles = 5`, `Laureles -> Estadio = 7`, `Estadio -> Belen = 8`.

La ruta elegida por Dijkstra usa la alternativa de **20 minutos**.

## 11. Respuesta cuando existe una ruta

Los identificadores siguientes son ilustrativos; provienen de la base de datos real durante la ejecucion.

```json
{
  "mode": "shortest_route",
  "reachable": true,
  "origin": {"id": 1, "code": "BASE-NORTE", "name": "Base Norte", "type": "BASE"},
  "destination": {"id": 4, "code": "ZONE-BELEN", "name": "Belen", "type": "ZONE"},
  "path": [
    {"id": 1, "code": "BASE-NORTE", "name": "Base Norte", "type": "BASE"},
    {"id": 2, "code": "ZONE-LAURELES", "name": "Laureles", "type": "ZONE"},
    {"id": 3, "code": "ZONE-ESTADIO", "name": "Estadio", "type": "ZONE"},
    {"id": 4, "code": "ZONE-BELEN", "name": "Belen", "type": "ZONE"}
  ],
  "segments": [
    {"origin": {"id": 1, "code": "BASE-NORTE", "name": "Base Norte", "type": "BASE"}, "destination": {"id": 2, "code": "ZONE-LAURELES", "name": "Laureles", "type": "ZONE"}, "estimated_minutes": 5},
    {"origin": {"id": 2, "code": "ZONE-LAURELES", "name": "Laureles", "type": "ZONE"}, "destination": {"id": 3, "code": "ZONE-ESTADIO", "name": "Estadio", "type": "ZONE"}, "estimated_minutes": 7},
    {"origin": {"id": 3, "code": "ZONE-ESTADIO", "name": "Estadio", "type": "ZONE"}, "destination": {"id": 4, "code": "ZONE-BELEN", "name": "Belen", "type": "ZONE"}, "estimated_minutes": 8}
  ],
  "total_minutes": 20,
  "traversal_order": [
    {"id": 1, "code": "BASE-NORTE", "name": "Base Norte", "type": "BASE"},
    {"id": 2, "code": "ZONE-LAURELES", "name": "Laureles", "type": "ZONE"},
    {"id": 3, "code": "ZONE-ESTADIO", "name": "Estadio", "type": "ZONE"},
    {"id": 4, "code": "ZONE-BELEN", "name": "Belen", "type": "ZONE"}
  ],
  "visited_count": 4,
  "message": "La ruta de menor tiempo desde Base Norte hasta Belen tarda 20 minuto(s)."
}
```

## 12. Respuesta sin ruta

Una zona desconectada no es error de parametros. El endpoint responde HTTP 200 y, entre otros campos, devuelve:

```json
{
  "mode": "shortest_route",
  "reachable": false,
  "path": [],
  "segments": [],
  "total_minutes": null
}
```

El resultado real incluye tambien `origin`, `destination`, `traversal_order`, `visited_count` y `message`.

## 13. Errores de validacion

La API responde **HTTP 400** cuando falta `origin_id` o `destination_id`, cuando no son enteros positivos, cuando el nodo no existe, cuando el origen no es `BASE` o cuando el destino no es `ZONE`. No debe confundirse un dato invalido con una ruta desconectada.

## 14. Significado de los principales campos

- `path`: secuencia ordenada de nodos que conforman la ruta optima, vacia si no hay ruta.
- `segments`: pares origen-destino de la ruta elegida con su `estimated_minutes`.
- `total_minutes`: suma de los tiempos de `segments`; `null` si no existe ruta.
- `traversal_order`: orden real de nodos asentados por Dijkstra durante la consulta.
- `visited_count`: numero de nodos en `traversal_order`.
- `reachable`: indica si existe una ruta desde la base hasta la zona.

## 15. Pruebas automatizadas y aceptacion

Ejecutar desde `brief-serviciocerca-backend` con Docker levantado:

```powershell
docker compose up -d --build
docker compose exec web python manage.py test apps.coverage.tests.test_shortest_route_views
docker compose exec web python manage.py test apps.coverage
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
docker compose exec web python scripts/acceptance_feature3.py
```

El script de aceptacion usa HTTP real y permite configurar el servidor con `ACCEPTANCE_API_BASE`; la URL por defecto dentro del contenedor `web` es `http://127.0.0.1:8000/api/coverage`.

## 16. Interpretacion del TXT y limpieza

El script crea datos con codigos unicos por ejecucion, valida HTTP, camino optimo, segmentos, traza, direccion, casos sin ruta y regresion de Feature 2. Al terminar elimina solamente los nodos de esa ejecucion y sus conexiones dependientes. Registra `PASS` o `FAIL` para cada verificacion en:

```text
evidence/acceptance/feature3_acceptance_YYYYMMDD_HHMMSS.txt
```

El resultado valido es:

```text
Pruebas fallidas:  0
FEATURE 3: ACEPTACION EXITOSA
```

Si alguna validacion o la limpieza falla, el script marca `ACEPTACION FALLIDA`, conserva el TXT y finaliza con codigo distinto de cero. No debe informarse exito sin haber ejecutado estas comprobaciones.

## 17. Limitaciones

Feature 3 utiliza minutos estimados almacenados; no calcula trafico en tiempo real, distancia cartografica, disponibilidad de tecnicos ni eventos externos. La visualizacion en Vue Flow puede consumir los resultados en una fase posterior.

## Resumen breve para la exposicion

"Para el Feature 3 expusimos una consulta REST que recibe una base y una zona. Primero se validan los IDs; luego la logica existente consulta PostgreSQL, convierte conexiones dirigidas en un grafo ponderado y usa Dijkstra para escoger el camino con menor suma de minutos. En nuestro ejemplo, una conexion directa tarda 30 minutos, mientras otra ruta tarda 5 + 7 + 8, por eso la API devuelve 20. La respuesta incluye camino, segmentos, tiempo y traza. Agregamos pruebas HTTP y un script de aceptacion que genera evidencia y borra unicamente sus datos de prueba."
