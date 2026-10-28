import json
import os
import sys
from datetime import datetime
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django

django.setup()

from apps.coverage.models import CoverageNode


API_BASE = os.getenv(
    "ACCEPTANCE_API_BASE",
    "http://127.0.0.1:8000/api/coverage",
).rstrip("/")


passed = 0
failed = 0
created_codes = []


class TeeOutput:
    def __init__(
        self,
        *streams,
    ):
        self.streams = streams

    def write(
        self,
        data,
    ):
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


def request(
    method,
    path,
    payload=None,
    query=None,
):
    url = (
        f"{API_BASE}/"
        f"{path.lstrip('/')}"
    )

    if query:
        url = (
            f"{url}?"
            f"{urllib.parse.urlencode(query)}"
        )

    data = None

    headers = {
        "Accept": "application/json",
    }

    if payload is not None:
        data = json.dumps(
            payload
        ).encode("utf-8")

        headers[
            "Content-Type"
        ] = "application/json"

    req = urllib.request.Request(
        url=url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(
            req,
            timeout=10,
        ) as response:

            body = response.read().decode(
                "utf-8"
            )

            return (
                response.status,
                (
                    json.loads(body)
                    if body
                    else None
                ),
            )

    except urllib.error.HTTPError as exc:
        body = exc.read().decode(
            "utf-8"
        )

        try:
            parsed = (
                json.loads(body)
                if body
                else None
            )
        except json.JSONDecodeError:
            parsed = body

        return (
            exc.code,
            parsed,
        )


def print_result(
    name,
    success,
    detail="",
):
    global passed
    global failed

    status_text = (
        "PASS"
        if success
        else "FAIL"
    )

    print(
        f"[{status_text}] {name}"
    )

    if detail:
        print(
            f"       {detail}"
        )

    if success:
        passed += 1
    else:
        failed += 1


def expect_status(
    name,
    actual,
    expected,
    body=None,
):
    success = (
        actual == expected
    )

    detail = (
        f"Esperado: {expected} | "
        f"Recibido: {actual}"
    )

    if (
        not success
        and body is not None
    ):
        detail += (
            f" | Respuesta: {body}"
        )

    print_result(
        name,
        success,
        detail,
    )

    return success


def create_node(
    *,
    code,
    name,
    node_type,
):
    status_code, body = request(
        "POST",
        "nodes/",
        {
            "code": code,
            "name": name,
            "type": node_type,
        },
    )

    if status_code == 201:
        created_codes.append(
            code
        )

    return (
        status_code,
        body,
    )


def create_connection(
    *,
    origin_id,
    destination_id,
    minutes,
    bidirectional=False,
):
    return request(
        "POST",
        "connections/",
        {
            "origin_id": origin_id,
            "destination_id": (
                destination_id
            ),
            "estimated_minutes": minutes,
            "is_bidirectional": (
                bidirectional
            ),
        },
    )


def cleanup():
    if not created_codes:
        return

    deleted = (
        CoverageNode.objects
        .filter(
            code__in=created_codes
        )
        .delete()
    )

    print()
    print(
        "Limpieza de datos "
        f"de aceptación: {deleted[0]} "
        "registro(s) eliminado(s)."
    )


def main():
    print(
        "=" * 72
    )

    print(
        "SERVICIOCERCA - "
        "ACEPTACION FEATURE 2"
    )

    print(
        "=" * 72
    )

    print(
        f"API: {API_BASE}"
    )

    print()

    unique = datetime.now().strftime(
        "%Y%m%d%H%M%S%f"
    )

    base_code = (
        f"BASE-ACC2-{unique}"
    )

    zone_a_code = (
        f"ZONE-ACC2-A-{unique}"
    )

    zone_b_code = (
        f"ZONE-ACC2-B-{unique}"
    )

    isolated_code = (
        f"ZONE-ACC2-I-{unique}"
    )

    reverse_base_code = (
        f"BASE-ACC2-R-{unique}"
    )

    reverse_zone_code = (
        f"ZONE-ACC2-R-{unique}"
    )

    # --------------------------------------------------------
    # Datos de prueba
    # --------------------------------------------------------

    status_code, base = create_node(
        code=base_code,
        name="Base Acceptance Feature 2",
        node_type="BASE",
    )

    if not expect_status(
        "SETUP-01 Crear base principal",
        status_code,
        201,
        base,
    ):
        return

    status_code, zone_a = create_node(
        code=zone_a_code,
        name="Zona Acceptance A",
        node_type="ZONE",
    )

    if not expect_status(
        "SETUP-02 Crear zona A",
        status_code,
        201,
        zone_a,
    ):
        return

    status_code, zone_b = create_node(
        code=zone_b_code,
        name="Zona Acceptance B",
        node_type="ZONE",
    )

    if not expect_status(
        "SETUP-03 Crear zona B",
        status_code,
        201,
        zone_b,
    ):
        return

    status_code, isolated = create_node(
        code=isolated_code,
        name="Zona Acceptance Aislada",
        node_type="ZONE",
    )

    if not expect_status(
        "SETUP-04 Crear zona aislada",
        status_code,
        201,
        isolated,
    ):
        return

    status_code, reverse_base = (
        create_node(
            code=reverse_base_code,
            name="Base Acceptance Reversa",
            node_type="BASE",
        )
    )

    if not expect_status(
        "SETUP-05 Crear base reversa",
        status_code,
        201,
        reverse_base,
    ):
        return

    status_code, reverse_zone = (
        create_node(
            code=reverse_zone_code,
            name="Zona Acceptance Reversa",
            node_type="ZONE",
        )
    )

    if not expect_status(
        "SETUP-06 Crear zona reversa",
        status_code,
        201,
        reverse_zone,
    ):
        return

    status_code, body = (
        create_connection(
            origin_id=base["id"],
            destination_id=zone_a["id"],
            minutes=15,
        )
    )

    expect_status(
        "SETUP-07 Crear conexión base -> zona A",
        status_code,
        201,
        body,
    )

    status_code, body = (
        create_connection(
            origin_id=zone_a["id"],
            destination_id=zone_b["id"],
            minutes=10,
        )
    )

    expect_status(
        "SETUP-08 Crear conexión zona A -> zona B",
        status_code,
        201,
        body,
    )

    status_code, body = (
        create_connection(
            origin_id=reverse_zone["id"],
            destination_id=reverse_base["id"],
            minutes=5,
        )
    )

    expect_status(
        "SETUP-09 Crear conexión reversa",
        status_code,
        201,
        body,
    )

    # --------------------------------------------------------
    # AC2-01
    # Cobertura existente
    # --------------------------------------------------------

    status_code, body = request(
        "GET",
        "reachability/",
        query={
            "origin_id": base["id"],
            "destination_id": (
                zone_b["id"]
            ),
        },
    )

    status_ok = expect_status(
        "AC2-01 Consultar cobertura existente",
        status_code,
        200,
        body,
    )

    if status_ok:
        correct = (
            body["covered"] is True
            and body["mode"] == "check"
        )

        print_result(
            "AC2-02 Confirmar resultado cubierto",
            correct,
            body.get(
                "message",
                "",
            ),
        )

        path_codes = [
            node["code"]
            for node in body["path"]
        ]

        print_result(
            "AC2-03 Validar camino encontrado",
            path_codes
            == [
                base_code,
                zone_a_code,
                zone_b_code,
            ],
            (
                " -> ".join(
                    path_codes
                )
            ),
        )

        trace_codes = [
            node["code"]
            for node
            in body[
                "traversal_order"
            ]
        ]

        print_result(
            "AC2-04 Validar traza BFS",
            trace_codes
            == [
                base_code,
                zone_a_code,
                zone_b_code,
            ],
            (
                " -> ".join(
                    trace_codes
                )
            ),
        )

    # --------------------------------------------------------
    # AC2-05
    # Alcance completo
    # --------------------------------------------------------

    status_code, body = request(
        "GET",
        "reachability/",
        query={
            "origin_id": base["id"],
        },
    )

    status_ok = expect_status(
        "AC2-05 Listar alcance de una base",
        status_code,
        200,
        body,
    )

    if status_ok:
        reachable_codes = {
            node["code"]
            for node
            in body[
                "reachable_nodes"
            ]
        }

        print_result(
            "AC2-06 Validar zonas alcanzables",
            reachable_codes
            == {
                zone_a_code,
                zone_b_code,
            },
            (
                f"Zonas: "
                f"{sorted(reachable_codes)}"
            ),
        )

    # --------------------------------------------------------
    # AC2-07
    # Red desconectada / zona sin conexión
    # --------------------------------------------------------

    status_code, body = request(
        "GET",
        "reachability/",
        query={
            "origin_id": base["id"],
            "destination_id": (
                isolated["id"]
            ),
        },
    )

    status_ok = expect_status(
        "AC2-07 Consultar zona desconectada",
        status_code,
        200,
        body,
    )

    if status_ok:
        print_result(
            "AC2-08 Zona desconectada sin cobertura",
            (
                body["covered"]
                is False
                and body["path"] == []
            ),
            body.get(
                "message",
                "",
            ),
        )

    # --------------------------------------------------------
    # AC2-09
    # Origen inexistente
    # --------------------------------------------------------

    status_code, body = request(
        "GET",
        "reachability/",
        query={
            "origin_id": 999999999,
        },
    )

    expect_status(
        "AC2-09 Rechazar origen inexistente",
        status_code,
        400,
        body,
    )

    # --------------------------------------------------------
    # AC2-10
    # Respetar dirección
    # --------------------------------------------------------

    status_code, body = request(
        "GET",
        "reachability/",
        query={
            "origin_id": (
                reverse_base["id"]
            ),
            "destination_id": (
                reverse_zone["id"]
            ),
        },
    )

    status_ok = expect_status(
        "AC2-10 Consultar sentido inverso",
        status_code,
        200,
        body,
    )

    if status_ok:
        print_result(
            "AC2-11 Respetar direccionalidad",
            body["covered"] is False,
            (
                "La conexión existe "
                "únicamente zona -> base."
            ),
        )

    # --------------------------------------------------------
    # AC2-12
    # Origen debe ser BASE
    # --------------------------------------------------------

    status_code, body = request(
        "GET",
        "reachability/",
        query={
            "origin_id": zone_a["id"],
            "destination_id": (
                zone_b["id"]
            ),
        },
    )

    expect_status(
        "AC2-12 Rechazar ZONE como origen",
        status_code,
        400,
        body,
    )


def print_summary():
    print()

    print(
        "=" * 72
    )

    print(
        "RESULTADO"
    )

    print(
        "=" * 72
    )

    print(
        f"Pruebas aprobadas: {passed}"
    )

    print(
        f"Pruebas fallidas:  {failed}"
    )

    print()

    if failed == 0:
        print(
            "FEATURE 2: "
            "ACEPTACION EXITOSA"
        )
    else:
        print(
            "FEATURE 2: "
            "ACEPTACION FALLIDA"
        )


if __name__ == "__main__":
    backend_dir = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    evidence_dir = (
        backend_dir
        / "evidence"
        / "acceptance"
    )

    evidence_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    report_path = (
        evidence_dir
        / (
            "feature2_acceptance_"
            f"{timestamp}.txt"
        )
    )

    original_stdout = sys.stdout

    with report_path.open(
        "w",
        encoding="utf-8",
    ) as report_file:

        sys.stdout = TeeOutput(
            original_stdout,
            report_file,
        )

        try:
            print(
                "Archivo de evidencia: "
                f"{report_path}"
            )

            print()

            try:
                main()
            except Exception as exc:
                global_failed = (
                    globals()["failed"]
                )

                globals()["failed"] = (
                    global_failed + 1
                )

                print_result(
                    "ERROR NO CONTROLADO",
                    False,
                    repr(exc),
                )

            finally:
                cleanup()
                print_summary()

        finally:
            sys.stdout = (
                original_stdout
            )

    print(
        f"Evidencia generada: "
        f"{report_path}"
    )

    sys.exit(
        0
        if failed == 0
        else 1
    )
