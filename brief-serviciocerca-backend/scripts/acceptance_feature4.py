"""ServicioCerca Feature 4 - HTTP acceptance with isolated fixture and TXT evidence.

Run: docker compose exec web python scripts/acceptance_feature4.py
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from apps.coverage.models import Connection, CoverageNode  # noqa: E402
from django.db.models import Q  # noqa: E402

API_BASE = os.getenv(
    "ACCEPTANCE_API_BASE", "http://127.0.0.1:8000/api/coverage"
).rstrip("/")
passed = 0
failed = 0
sequence = 0
nodes_created = []  # exact (pk, code)
connections_created = []  # exact (pk, origin_id, destination_id)


class Tee:
    def __init__(self, *outputs):
        self.outputs = outputs

    def write(self, value):
        for output in self.outputs:
            output.write(value)
            output.flush()

    def flush(self):
        for output in self.outputs:
            output.flush()


def parse_json(value):
    try:
        return json.loads(value) if value else None
    except json.JSONDecodeError:
        return value


def http(method, endpoint, payload=None, query=None):
    url = f"{API_BASE}/{endpoint.lstrip('/')}"
    if query is not None:
        url += "?" + urllib.parse.urlencode(query)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.status, parse_json(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, parse_json(exc.read().decode("utf-8"))


def check(label, condition, detail=""):
    global passed, failed, sequence
    sequence += 1
    success = bool(condition)
    passed += int(success)
    failed += int(not success)
    result = "PASS" if success else "FAIL"
    print(f"[{result}] AC4-{sequence:02d} {label}" + (f" | {detail}" if detail else ""))
    return success


def required(label, condition, detail=""):
    if not check(label, condition, detail):
        raise RuntimeError(f"No se pudo preparar el escenario: {label}")


def codes(items):
    if not isinstance(items, list) or not all(isinstance(x, dict) for x in items):
        return None
    return [x.get("code") for x in items]


def create_node(code, name, kind):
    status, data = http("POST", "nodes/", {"code": code, "name": name, "type": kind})
    if status == 201 and isinstance(data, dict) and isinstance(data.get("id"), int):
        nodes_created.append((data["id"], data.get("code", code)))
    required(
        f"Crear {name}",
        status == 201 and isinstance(data, dict)
        and isinstance(data.get("id"), int)
        and data.get("code") == code and data.get("type") == kind,
        f"HTTP {status}",
    )
    return data


def create_connection(origin, destination, minutes, bidirectional=False):
    payload = {
        "origin_id": origin["id"],
        "destination_id": destination["id"],
        "estimated_minutes": minutes,
        "is_bidirectional": bidirectional,
    }
    status, data = http("POST", "connections/", payload)
    if status == 201 and isinstance(data, dict) and isinstance(data.get("id"), int):
        connections_created.append((data["id"], origin["id"], destination["id"]))
    required(
        f"Crear conexion {origin['name']} -> {destination['name']}",
        status == 201 and isinstance(data, dict)
        and isinstance(data.get("id"), int)
        and data.get("estimated_minutes") == minutes
        and data.get("is_bidirectional") is bidirectional,
        f"HTTP {status}",
    )


def route(origin, destination):
    return http("GET", "shortest-route/", query={
        "origin_id": origin["id"], "destination_id": destination["id"]
    })


def coverage(origin, destination):
    return http("GET", "reachability/", query={
        "origin_id": origin["id"], "destination_id": destination["id"]
    })


def expect_error(endpoint, query, field, label):
    status, data = http("GET", endpoint, query=query)
    check(label, status == 400 and isinstance(data, dict) and field in data,
          f"HTTP {status}; {str(data)[:170]}")


def run_cases():
    print("SERVICIOCERCA - ACEPTACION FEATURE 4")
    print(f"API: {API_BASE}\n")
    status, before = http("GET", "network/")
    required("API de red disponible", status == 200 and isinstance(before, dict)
             and all(isinstance(before.get(k), list) for k in ("nodes", "connections", "technicians")))

    suffix = uuid4().hex[:12].upper()
    code = lambda tag: f"F4-{tag}-{suffix}"
    base = create_node(code("BN"), "Base Norte F4", "BASE")
    laureles = create_node(code("LA"), "Laureles F4", "ZONE")
    estadio = create_node(code("ES"), "Estadio F4", "ZONE")
    belen = create_node(code("BE"), "Belen F4", "ZONE")
    isolated = create_node(code("IS"), "Zona aislada F4", "ZONE")
    base2 = create_node(code("BS"), "Base Sur F4", "BASE")
    reverse = create_node(code("RE"), "Zona reversa F4", "ZONE")
    both = create_node(code("BI"), "Zona bidireccional F4", "ZONE")

    create_connection(base, belen, 30)
    create_connection(base, laureles, 5)
    create_connection(laureles, estadio, 7)
    create_connection(estadio, belen, 8)
    create_connection(reverse, base2, 4)
    create_connection(both, base2, 6, True)

    status, network = http("GET", "network/")
    known_ids = {n[0] for n in nodes_created}
    check("Red contiene los nodos de esta prueba", status == 200
          and isinstance(network, dict) and known_ids.issubset({n.get("id") for n in network.get("nodes", [])}))

    status, optimum = route(base, belen)
    required("Consulta Dijkstra HTTP 200", status == 200 and isinstance(optimum, dict))
    check("Destino alcanzable", optimum.get("reachable") is True)
    check("Modo de consulta correcto", optimum.get("mode") == "shortest_route")
    check("Tiempo minimo real: 20 y no 30", optimum.get("total_minutes") == 20)
    check("Camino ordenado para el operador", codes(optimum.get("path")) ==
          [base["code"], laureles["code"], estadio["code"], belen["code"]])
    segments = optimum.get("segments")
    durations = [s.get("estimated_minutes") for s in segments] if isinstance(segments, list) else None
    check("Minutos correctos por tramo", durations == [5, 7, 8])
    check("Tiempo total equivale a la suma de tramos", durations is not None
          and all(isinstance(n, int) for n in durations)
          and sum(durations) == optimum.get("total_minutes"))
    check("Tramos incluyen origen y destino correctos", isinstance(segments, list)
          and [(s["origin"]["code"], s["destination"]["code"]) for s in segments] ==
          [(base["code"], laureles["code"]),
           (laureles["code"], estadio["code"]),
           (estadio["code"], belen["code"])])
    check("Origen y destino del resultado correctos", optimum.get("origin", {}).get("id") == base["id"]
          and optimum.get("destination", {}).get("id") == belen["id"])
    trace = optimum.get("traversal_order")
    check("Traza Dijkstra consistente", isinstance(trace, list)
          and optimum.get("visited_count") == len(trace) and len(trace) > 0)

    bfs_status, bfs = coverage(base, belen)
    required("Consulta BFS HTTP 200", bfs_status == 200 and isinstance(bfs, dict))
    check("BFS confirma cobertura", bfs.get("mode") == "check" and bfs.get("covered") is True)
    check("BFS selecciona conexion directa de un tramo", codes(bfs.get("path")) == [base["code"], belen["code"]])
    check("El menor numero de tramos no es el menor tiempo", optimum.get("total_minutes") == 20 and
          len(bfs.get("path", [])) == 2 and any(c["estimated_minutes"] == 30 and
          c["origin"]["id"] == base["id"] and c["destination"]["id"] == belen["id"]
          for c in network.get("connections", [])))

    status, no_route = route(base, isolated)
    check("Red desconectada devuelve HTTP 200", status == 200 and isinstance(no_route, dict))
    check("Sin ruta no inventa tiempo ni recorrido", isinstance(no_route, dict)
          and no_route.get("reachable") is False and no_route.get("total_minutes", "missing") is None
          and no_route.get("path") == [] and no_route.get("segments") == [])
    status, no_bfs = coverage(base, isolated)
    check("BFS tambien identifica la zona desconectada", status == 200
          and isinstance(no_bfs, dict) and no_bfs.get("covered") is False and no_bfs.get("path") == [])

    missing_id = max(999999999, *(n[0] for n in nodes_created)) + 1000000
    expect_error("shortest-route/", {"origin_id": base["id"], "destination_id": missing_id},
                 "destination", "Zona inexistente produce error de validacion")
    expect_error("shortest-route/", {"origin_id": missing_id, "destination_id": belen["id"]},
                 "origin", "Base inexistente produce error de validacion")
    expect_error("shortest-route/", {"origin_id": laureles["id"], "destination_id": belen["id"]},
                 "origin", "Origen debe ser BASE")
    expect_error("shortest-route/", {"origin_id": base["id"], "destination_id": base2["id"]},
                 "destination", "Destino debe ser ZONE")
    expect_error("shortest-route/", {"destination_id": belen["id"]},
                 "origin_id", "Parametro origin_id obligatorio")
    expect_error("shortest-route/", {"origin_id": "ABC", "destination_id": belen["id"]},
                 "origin_id", "Identificador no numerico rechazado")

    for minutes in (0, -5, "ABC"):
        status, response = http("POST", "connections/", {
            "origin_id": base["id"], "destination_id": isolated["id"],
            "estimated_minutes": minutes, "is_bidirectional": False,
        })
        check(f"Peso invalido {minutes!r} rechazado", status == 400
              and isinstance(response, dict) and "estimated_minutes" in response,
              f"HTTP {status}")
    check("Pesos invalidos no generan conexiones", not Connection.objects.filter(
          origin_id=base["id"], destination_id=isolated["id"]).exists())

    status, reverse_route = route(base2, reverse)
    check("Conexion dirigida no permite regreso", status == 200 and isinstance(reverse_route, dict)
          and reverse_route.get("reachable") is False)
    status, bidir_route = route(base2, both)
    check("Conexion bidireccional permite regreso", status == 200 and isinstance(bidir_route, dict)
          and bidir_route.get("reachable") is True and bidir_route.get("total_minutes") == 6)

    after_status, after = http("GET", "network/")
    check("Consultas no modifican la red", after_status == 200 and network == after)


def cleanup():
    print("\nLIMPIEZA CONTROLADA")
    for pk, origin_id, destination_id in reversed(connections_created):
        qs = Connection.objects.filter(pk=pk, origin_id=origin_id, destination_id=destination_id)
        existed = qs.exists()
        qs.delete()
        check(f"Eliminar conexion temporal {pk}", existed and not Connection.objects.filter(pk=pk).exists())
    for pk, code in reversed(nodes_created):
        foreign_links = Connection.objects.filter(Q(origin_id=pk) | Q(destination_id=pk)).exists()
        if foreign_links:
            check(f"Nodo {code}: no borrar conexiones ajenas", False,
                  "Existen conexiones no registradas en esta ejecucion")
            continue
        qs = CoverageNode.objects.filter(pk=pk, code=code)
        existed = qs.exists()
        qs.delete()
        check(f"Eliminar nodo temporal {code}", existed and not CoverageNode.objects.filter(pk=pk).exists())


def main():
    global failed
    output_dir = ROOT / "evidence" / "acceptance"
    output_dir.mkdir(parents=True, exist_ok=True)
    name = f"feature4_acceptance_{datetime.now():%Y%m%d_%H%M%S}_{uuid4().hex[:5]}.txt"
    path = output_dir / name
    console = sys.stdout
    with path.open("w", encoding="utf-8") as file:
        with redirect_stdout(Tee(console, file)):
            print(f"Archivo: {path}\n")
            try:
                run_cases()
            except Exception as exc:
                check("Error no controlado", False, repr(exc))
            finally:
                try:
                    cleanup()
                except Exception as exc:
                    check("Error en limpieza", False, repr(exc))
                print(f"\nPruebas aprobadas: {passed}")
                print(f"Pruebas fallidas: {failed}")
                print("FEATURE 4: ACEPTACION EXITOSA" if failed == 0
                      else "FEATURE 4: ACEPTACION FALLIDA")
    print(f"Evidencia: {path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
