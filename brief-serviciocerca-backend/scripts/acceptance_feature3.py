"""Feature 3 live HTTP acceptance with isolated test data and TXT evidence.

Run inside Docker's web container while Django's HTTP server is available:
    docker compose exec web python scripts/acceptance_feature3.py
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

# Direct execution via 'python scripts/...' must be able to import config.
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from apps.coverage.models import CoverageNode  # noqa: E402

API_BASE = os.getenv(
    "ACCEPTANCE_API_BASE", "http://127.0.0.1:8000/api/coverage"
).rstrip("/")

passed = 0
failed = 0
created_nodes = []  # Exact (primary key, unique code) pairs for this execution.


class TeeOutput:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


def request(method, path, payload=None, query=None):
    url = f"{API_BASE}/{path.lstrip('/')}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
    body_bytes = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        url, data=body_bytes, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            text = response.read().decode("utf-8")
            return response.status, _parse_json(text)
    except urllib.error.HTTPError as exc:
        return exc.code, _parse_json(exc.read().decode("utf-8"))


def _parse_json(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def record(case, condition, detail=""):
    global passed, failed
    outcome = "PASS" if condition else "FAIL"
    print(f"[{outcome}] {case}" + (f" | {detail}" if detail else ""))
    if condition:
        passed += 1
    else:
        failed += 1
    return condition


def require(case, condition, detail=""):
    if not record(case, condition, detail):
        raise RuntimeError(f"Setup prerequisite failed: {case}")


def status_and_body(case, status_code, body, expected=200):
    return record(
        case,
        status_code == expected,
        f"HTTP {status_code}; expected {expected}; body: {str(body)[:200] if status_code != expected else 'OK'}",
    )


def create_node(code, name, node_type, case):
    status_code, body = request(
        "POST", "nodes/", {"code": code, "name": name, "type": node_type}
    )
    # Track only successfully created rows, never delete pre-existing codes.
    if status_code == 201 and isinstance(body, dict) and isinstance(body.get("id"), int):
        created_nodes.append((body["id"], code))
    require(
        case,
        status_code == 201
        and isinstance(body, dict)
        and isinstance(body.get("id"), int)
        and body.get("code") == code
        and body.get("type") == node_type,
        f"HTTP {status_code} | {str(body)[:180]}",
    )
    return body


def create_connection(origin, destination, minutes, case, bidirectional=False):
    status_code, body = request(
        "POST", "connections/",
        {
            "origin_id": origin["id"],
            "destination_id": destination["id"],
            "estimated_minutes": minutes,
            "is_bidirectional": bidirectional,
        },
    )
    require(
        case,
        status_code == 201
        and isinstance(body, dict)
        and body.get("estimated_minutes") == minutes
        and body.get("is_bidirectional") is bidirectional,
        f"HTTP {status_code} | {str(body)[:180]}",
    )


def route(origin, destination):
    return request(
        "GET", "shortest-route/",
        query={"origin_id": origin["id"], "destination_id": destination["id"]},
    )


def codes(nodes):
    return [node.get("code") for node in nodes] if isinstance(nodes, list) else None


def check_error(case, params, field):
    status_code, body = request("GET", "shortest-route/", query=params)
    record(
        case,
        status_code == 400 and isinstance(body, dict) and field in body,
        f"HTTP {status_code}; expected validation field {field}; body: {str(body)[:180]}",
    )


def main():
    print("=" * 72)
    print("SERVICIOCERCA - ACEPTACION FEATURE 3")
    print("=" * 72)
    print(f"API: {API_BASE}")
    print()

    unique = datetime.now().strftime("%Y%m%d%H%M%S") + uuid4().hex[:8]
    ids = {
        "base": f"F3-BN-{unique}",
        "a": f"F3-ZA-{unique}",
        "b": f"F3-ZB-{unique}",
        "dest": f"F3-ZD-{unique}",
        "isolated": f"F3-ZI-{unique}",
        "base2": f"F3-BS-{unique}",
        "reverse": f"F3-ZR-{unique}",
        "bidir": f"F3-ZX-{unique}",
    }

    base = create_node(ids["base"], "Base Norte", "BASE", "SETUP-01 Crear base principal")
    a = create_node(ids["a"], "Laureles", "ZONE", "SETUP-02 Crear zona A")
    b = create_node(ids["b"], "Estadio", "ZONE", "SETUP-03 Crear zona B")
    dest = create_node(ids["dest"], "Belen", "ZONE", "SETUP-04 Crear zona destino")
    isolated = create_node(ids["isolated"], "Aislada", "ZONE", "SETUP-05 Crear zona aislada")
    base2 = create_node(ids["base2"], "Base Sur", "BASE", "SETUP-06 Crear base secundaria")
    reverse = create_node(ids["reverse"], "Reversa", "ZONE", "SETUP-07 Crear zona inversa")
    bidir = create_node(ids["bidir"], "Bidireccional", "ZONE", "SETUP-08 Crear zona bidireccional")

    create_connection(base, dest, 30, "SETUP-09 Conexion directa de 30")
    create_connection(base, a, 5, "SETUP-10 Conexion base a zona A de 5")
    create_connection(a, b, 7, "SETUP-11 Conexion zona A a B de 7")
    create_connection(b, dest, 8, "SETUP-12 Conexion zona B a destino de 8")
    create_connection(reverse, base2, 4, "SETUP-13 Conexion inversa")
    create_connection(bidir, base2, 6, "SETUP-14 Conexion bidireccional", True)

    # A read-only check against the full network endpoint.
    status_before, network_before = request("GET", "network/")
    status_and_body("AC3-01 Obtener red antes de consultas", status_before, network_before)

    http_status, data = route(base, dest)
    status_ok = status_and_body("AC3-02 Endpoint devuelve HTTP 200", http_status, data)
    if status_ok and isinstance(data, dict):
        record("AC3-03 Modo shortest_route", data.get("mode") == "shortest_route")
        record("AC3-04 Destino alcanzable", data.get("reachable") is True)
        record("AC3-05 Ruta optima usa 20 y no 30", data.get("total_minutes") == 20)
        record("AC3-06 Orden completo de nodos", codes(data.get("path")) == [ids["base"], ids["a"], ids["b"], ids["dest"]])
        segments = data.get("segments")
        minutes = [s.get("estimated_minutes") for s in segments] if isinstance(segments, list) else None
        record("AC3-07 Minutos por segmento", minutes == [5, 7, 8], str(minutes))
        record("AC3-08 Suma segmentos equivale al total", minutes is not None and sum(minutes) == data.get("total_minutes"))
        record("AC3-09 Traza Dijkstra", codes(data.get("traversal_order")) == [ids["base"], ids["a"], ids["b"], ids["dest"]])
        trace = data.get("traversal_order")
        record("AC3-10 Contador de visitados", isinstance(trace, list) and data.get("visited_count") == len(trace) == 4)
        record("AC3-11 Origen y destino correctos", isinstance(data.get("origin"), dict) and isinstance(data.get("destination"), dict) and data["origin"].get("code") == ids["base"] and data["destination"].get("code") == ids["dest"])
    else:
        record("AC3-03 Respuesta JSON de ruta", False, str(data)[:200])

    no_status, no_data = route(base, isolated)
    status_and_body("AC3-12 Sin ruta devuelve HTTP 200", no_status, no_data)
    record(
        "AC3-13 Destino desconectado sin tiempo ni segmentos",
        isinstance(no_data, dict)
        and no_data.get("mode") == "shortest_route"
        and no_data.get("reachable") is False
        and no_data.get("path") == []
        and no_data.get("segments") == []
        and no_data.get("total_minutes", "missing") is None,
    )

    nonexistent_id = max(999999999, *(item["id"] for item in (base, a, b, dest, base2))) + 1000000
    check_error("AC3-14 Origen inexistente", {"origin_id": nonexistent_id, "destination_id": dest["id"]}, "origin")
    check_error("AC3-15 Destino inexistente", {"origin_id": base["id"], "destination_id": nonexistent_id}, "destination")
    check_error("AC3-16 Origen debe ser BASE", {"origin_id": a["id"], "destination_id": dest["id"]}, "origin")
    check_error("AC3-17 Destino debe ser ZONE", {"origin_id": base["id"], "destination_id": base2["id"]}, "destination")
    check_error("AC3-18 Falta origin_id", {"destination_id": dest["id"]}, "origin_id")
    check_error("AC3-19 Falta destination_id", {"origin_id": base["id"]}, "destination_id")
    check_error("AC3-20 origin_id no numerico", {"origin_id": "ABC", "destination_id": dest["id"]}, "origin_id")
    check_error("AC3-21 destination_id no numerico", {"origin_id": base["id"], "destination_id": "ABC"}, "destination_id")
    check_error("AC3-22 origin_id cero", {"origin_id": 0, "destination_id": dest["id"]}, "origin_id")
    check_error("AC3-23 destination_id negativo", {"origin_id": base["id"], "destination_id": -1}, "destination_id")

    reverse_status, reverse_body = route(base2, reverse)
    record("AC3-24 Respetar sentido inverso", reverse_status == 200 and isinstance(reverse_body, dict) and reverse_body.get("reachable") is False and reverse_body.get("path") == [] and reverse_body.get("total_minutes") is None)

    both_status, both_body = route(base2, bidir)
    record("AC3-25 Conexion bidireccional", both_status == 200 and isinstance(both_body, dict) and both_body.get("reachable") is True and both_body.get("total_minutes") == 6 and codes(both_body.get("path")) == [ids["base2"], ids["bidir"]])

    bfs_status, bfs_body = request("GET", "reachability/", query={"origin_id": base["id"], "destination_id": dest["id"]})
    record("AC3-26 Feature 2 BFS sigue funcionando", bfs_status == 200 and isinstance(bfs_body, dict) and bfs_body.get("mode") == "check" and bfs_body.get("covered") is True and codes(bfs_body.get("path")) == [ids["base"], ids["dest"]])

    status_after, network_after = request("GET", "network/")
    record("AC3-27 Consultas no alteran la red", status_before == status_after == 200 and network_before == network_after)


def cleanup():
    """Delete only exact IDs + unique codes successfully created in this run."""
    for node_id, code in reversed(created_nodes):
        qs = CoverageNode.objects.filter(pk=node_id, code=code)
        existed = qs.exists()
        deleted_count = qs.delete()[0] if existed else 0
        record(
            f"CLEANUP nodo {code}",
            existed and deleted_count > 0 and not CoverageNode.objects.filter(pk=node_id, code=code).exists(),
            f"Registros eliminados (incluye cascadas): {deleted_count}",
        )
    if not created_nodes:
        print("Limpieza: no se crearon nodos confirmados en esta ejecucion.")


def summary():
    print()
    print("=" * 72)
    print("RESULTADO")
    print("=" * 72)
    print(f"Pruebas aprobadas: {passed}")
    print(f"Pruebas fallidas:  {failed}")
    print()
    print("FEATURE 3: ACEPTACION EXITOSA" if failed == 0 else "FEATURE 3: ACEPTACION FALLIDA")


def run():
    global failed
    evidence_dir = BACKEND_DIR / "evidence" / "acceptance"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = evidence_dir / f"feature3_acceptance_{timestamp}.txt"
    console = sys.stdout

    with path.open("w", encoding="utf-8") as report:
        with redirect_stdout(TeeOutput(console, report)):
            print(f"Archivo de evidencia: {path}")
            try:
                main()
            except Exception as exc:
                record("ERROR NO CONTROLADO", False, repr(exc))
            finally:
                try:
                    cleanup()
                except Exception as exc:
                    record("ERROR DE LIMPIEZA", False, repr(exc))
                summary()

    print(f"Evidencia generada: {path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run())
