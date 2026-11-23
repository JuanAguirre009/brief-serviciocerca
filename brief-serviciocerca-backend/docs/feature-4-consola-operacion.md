# ServicioCerca — Feature 4: Consola de operación demostrable

## 1. Objetivo

El Feature 4 integra las funcionalidades desarrolladas en las primeras tres entregas y ofrece una consola enfocada en la toma de decisiones operativas.

Su objetivo es que el operador pueda identificar:

1. A qué zona debe desplazarse.
2. Cuánto tiempo estimado requiere el recorrido.
3. Qué zonas debe atravesar para llegar a su destino.

## 2. Funcionalidades integradas

### Feature 1 — Red de cobertura

Permite registrar bases, zonas, técnicos y conexiones.

Cada conexión contiene un tiempo estimado y una propiedad que establece si puede recorrerse en ambos sentidos.

### Feature 2 — Consulta de cobertura

Utiliza BFS para determinar si un destino es alcanzable desde una base.

BFS permite encontrar un camino con menor cantidad de conexiones, pero no garantiza el recorrido con menor tiempo.

### Feature 3 — Ruta de menor tiempo

Utiliza Dijkstra para obtener el camino cuya suma de minutos es mínima.

Trabaja con tiempos estimados estrictamente positivos.

### Feature 4 — Consola de operación

Integra la información de los tres features anteriores.

La interfaz está dividida en resultado rápido y análisis profundo.

## 3. Resultado rápido

Es la sección principal.

Presenta:

- Base de origen.
- Zona de destino.
- Tiempo total estimado.
- Recorrido ordenado.
- Minutos de cada conexión.

El tiempo y el destino deben ser los elementos más importantes de la respuesta.

El operador no necesita interpretar el grafo para conocer el recorrido recomendado.

## 4. Análisis profundo

Es una sección opcional que se encuentra cerrada inicialmente.

Incluye:

- Representación visual del grafo.
- Resaltado del recorrido Dijkstra.
- Exploración de los nodos procesados.
- Consulta de cobertura BFS.
- Comparación técnica entre BFS y Dijkstra.

Este análisis no modifica el resultado rápido, que siempre corresponde a la recomendación de Dijkstra.

## 5. Arquitectura

Backend:

- Django 6.
- Django REST Framework.
- PostgreSQL.
- Servicios de cobertura.
- Algoritmos BFS y Dijkstra.

Frontend:

- Nuxt 4.
- Vue 3.
- TypeScript.
- Vue Flow.

Los algoritmos están implementados en el backend.

El frontend consume los resultados mediante HTTP y no calcula por sí mismo rutas alternativas.

## 6. Endpoints utilizados

Obtener la red:

GET /api/coverage/network/

Consultar cobertura:

GET /api/coverage/reachability/?origin_id=1&destination_id=5

Consultar ruta óptima:

GET /api/coverage/shortest-route/?origin_id=1&destination_id=5

Los identificadores anteriores son ilustrativos.

## 7. Ejemplo de optimización

Escenario de prueba:

Base Norte → Belén: 30 minutos.

Ruta alternativa:

Base Norte → Laureles: 5 minutos.

Laureles → Estadio: 7 minutos.

Estadio → Belén: 8 minutos.

Tiempo total alternativo: 20 minutos.

BFS puede seleccionar la conexión directa porque tiene un solo tramo.

Dijkstra selecciona la alternativa de 20 minutos porque minimiza la suma de los tiempos.

Este escenario se utiliza en las pruebas de aceptación. No se debe afirmar que corresponde necesariamente a los datos cargados en la aplicación durante una demostración.

## 8. Escenarios de error

### Zona inexistente

La API debe devolver HTTP 400 con un error de validación.

### Red desconectada

La API puede devolver HTTP 200 con `reachable: false`, sin segmentos y con `total_minutes: null`.

### Peso inválido

Las conexiones deben tener minutos enteros estrictamente positivos.

Los valores cero, negativos o no numéricos deben rechazarse.

### Dirección no permitida

Una conexión unidireccional no puede recorrerse automáticamente en sentido inverso.

## 9. Pruebas de aceptación

Script:

scripts/acceptance_feature4.py

Ejecutar dentro del contenedor Docker web:

docker compose exec web python scripts/acceptance_feature4.py

El script realiza consultas HTTP reales y crea registros temporales.

Genera evidencia en:

evidence/acceptance/feature4_acceptance_*.txt

Cada verificación se registra con PASS o FAIL.

La aceptación se considera exitosa únicamente cuando no existen verificaciones fallidas y la limpieza de los datos temporales es correcta.

## 10. Validación del frontend

Las pruebas de aceptación del backend no sustituyen las verificaciones visuales.

Es necesario comprobar manualmente:

- Prioridad visual del tiempo y destino.
- Orden correcto de las zonas.
- Análisis profundo cerrado inicialmente.
- Grafo disponible al abrir el análisis.
- Resaltado de recorridos.
- Consulta complementaria BFS.
- Estados de error.
- Adaptación a diferentes tamaños de pantalla.
- Acceso a la consola desde la navegación.

Los resultados deben registrarse en el documento de verificaciones visuales.

## 11. Limitaciones

ServicioCerca utiliza datos sintéticos y tiempos estimados.

No utiliza tráfico en tiempo real, GPS, navegación geográfica ni asignación automática de técnicos.

El grafo representa relaciones operativas configuradas por el usuario.

El resultado de Dijkstra corresponde al tiempo total mínimo según los pesos positivos registrados en la red.

## 12. Conclusión

El Feature 4 transforma las funcionalidades de grafos en una herramienta de consulta operacional.

El operador obtiene primero una recomendación comprensible, mientras que la representación gráfica y la explicación técnica quedan disponibles para un análisis adicional.

Esta organización responde a la corrección docente de priorizar el valor empresarial sobre la visualización del algoritmo.
