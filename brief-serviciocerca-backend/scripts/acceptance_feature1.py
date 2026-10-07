import json
import os
import sys
import time
import urllib.error
import urllib.request


API_BASE = os.getenv(
    "ACCEPTANCE_API_BASE",
    "http://127.0.0.1:8000/api/coverage",
).rstrip("/")


passed = 0
failed = 0


def print_result(name, success, detail=""):
    global passed, failed

    status = "PASS" if success else "FAIL"

    print(f"[{status}] {name}")

    if detail:
        print(f"       {detail}")

    if success:
        passed += 1
    else:
        failed += 1


def request(method, path, payload=None):
    url = f"{API_BASE}/{path.lstrip('/')}"

    data = None
    headers = {
        "Accept": "application/json",
    }

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url=url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")

            return (
                response.status,
                json.loads(body) if body else None,
            )

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")

        try:
            parsed = json.loads(body) if body else None
        except json.JSONDecodeError:
            parsed = body

        return exc.code, parsed


def expect_status(name, actual, expected, body=None):
    success = actual == expected

    detail = f"Esperado: {expected} | Recibido: {actual}"

    if not success and body is not None:
        detail += f" | Respuesta: {body}"

    print_result(
        name,
        success,
        detail,
    )

    return success


def main():
    print("=" * 70)
    print("SERVICIOCERCA - SCRIPT DE ACEPTACION FEATURE 1")
    print("=" * 70)
    print(f"API: {API_BASE}")
    print()

    unique = str(int(time.time()))

    base_code = f"BASE-ACC-{unique}"
    zone_code = f"ZONE-ACC-{unique}"
    technician_code = f"TEC-ACC-{unique}"

    # ============================================================
    # AC-01 - Consultar red
    # ============================================================

    status, network = request(
        "GET",
        "network/",
    )

    if not expect_status(
        "AC-01 Consultar la red configurada",
        status,
        200,
        network,
    ):
        print()
        print(
            "No fue posible consultar la API. "
            "Verifica que Django este ejecutandose."
        )
        sys.exit(1)

    # ============================================================
    # AC-02 - Registrar BASE
    # ============================================================

    status, base = request(
        "POST",
        "nodes/",
        {
            "code": base_code,
            "name": "Base Aceptacion",
            "type": "BASE",
        },
    )

    if not expect_status(
        "AC-02 Registrar una base valida",
        status,
        201,
        base,
    ):
        finish()
        return

    base_id = base["id"]

    # ============================================================
    # AC-03 - Registrar ZONE
    # ============================================================

    status, zone = request(
        "POST",
        "nodes/",
        {
            "code": zone_code,
            "name": "Zona Aceptacion",
            "type": "ZONE",
        },
    )

    if not expect_status(
        "AC-03 Registrar una zona valida",
        status,
        201,
        zone,
    ):
        finish()
        return

    zone_id = zone["id"]

    # ============================================================
    # AC-04 - Registrar tecnico
    # ============================================================

    status, technician = request(
        "POST",
        "technicians/",
        {
            "code": technician_code,
            "name": "Tecnico Aceptacion",
            "base_id": base_id,
            "is_available": True,
        },
    )

    expect_status(
        "AC-04 Registrar tecnico asociado a una BASE",
        status,
        201,
        technician,
    )

    # ============================================================
    # AC-05 - Registrar conexion bidireccional
    # ============================================================

    status, connection = request(
        "POST",
        "connections/",
        {
            "origin_id": base_id,
            "destination_id": zone_id,
            "estimated_minutes": 15,
            "is_bidirectional": True,
        },
    )

    expect_status(
        "AC-05 Registrar conexion valida con peso positivo",
        status,
        201,
        connection,
    )

    if status == 201:
        correct_direction = (
            connection["is_bidirectional"] is True
            and connection["estimated_minutes"] == 15
        )

        print_result(
            "AC-06 Conservar peso y bidireccionalidad",
            correct_direction,
            (
                "Conexion bidireccional de 15 minutos"
                if correct_direction
                else f"Respuesta inesperada: {connection}"
            ),
        )

    # ============================================================
    # AC-07 - Rechazar identificador duplicado
    # ============================================================

    status, body = request(
        "POST",
        "nodes/",
        {
            "code": base_code,
            "name": "Base Duplicada",
            "type": "BASE",
        },
    )

    expect_status(
        "AC-07 Rechazar identificador duplicado",
        status,
        400,
        body,
    )

    # ============================================================
    # AC-08 - Rechazar peso cero
    # ============================================================

    status, body = request(
        "POST",
        "connections/",
        {
            "origin_id": zone_id,
            "destination_id": base_id,
            "estimated_minutes": 0,
            "is_bidirectional": False,
        },
    )

    expect_status(
        "AC-08 Rechazar peso igual a cero",
        status,
        400,
        body,
    )

    # ============================================================
    # AC-09 - Rechazar auto-conexion
    # ============================================================

    status, body = request(
        "POST",
        "connections/",
        {
            "origin_id": base_id,
            "destination_id": base_id,
            "estimated_minutes": 10,
            "is_bidirectional": False,
        },
    )

    expect_status(
        "AC-09 Rechazar conexion de un nodo consigo mismo",
        status,
        400,
        body,
    )

    # ============================================================
    # AC-10 - Rechazar tecnico asociado a ZONE
    # ============================================================

    status, body = request(
        "POST",
        "technicians/",
        {
            "code": f"TEC-ZONE-{unique}",
            "name": "Tecnico Zona Invalido",
            "base_id": zone_id,
            "is_available": True,
        },
    )

    expect_status(
        "AC-10 Rechazar tecnico asociado a una ZONE",
        status,
        400,
        body,
    )

    # ============================================================
    # AC-11 - Verificar persistencia en red completa
    # ============================================================

    status, network = request(
        "GET",
        "network/",
    )

    if expect_status(
        "AC-11 Consultar red despues de los registros",
        status,
        200,
        network,
    ):
        node_codes = {
            node["code"]
            for node in network["nodes"]
        }

        technician_codes = {
            item["code"]
            for item in network["technicians"]
        }

        connection_exists = any(
            item["origin"]["id"] == base_id
            and item["destination"]["id"] == zone_id
            and item["estimated_minutes"] == 15
            and item["is_bidirectional"] is True
            for item in network["connections"]
        )

        persisted = (
            base_code in node_codes
            and zone_code in node_codes
            and technician_code in technician_codes
            and connection_exists
        )

        print_result(
            "AC-12 Verificar entidades en la red consultada",
            persisted,
            (
                "Base, zona, tecnico y conexion encontrados"
                if persisted
                else "No se encontraron todos los registros creados"
            ),
        )

    finish()


def finish():
    print()
    print("=" * 70)
    print("RESULTADO")
    print("=" * 70)
    print(f"Pruebas aprobadas: {passed}")
    print(f"Pruebas fallidas:  {failed}")

    if failed == 0:
        print()
        print("FEATURE 1: ACEPTACION EXITOSA")
        sys.exit(0)

    print()
    print("FEATURE 1: ACEPTACION FALLIDA")
    sys.exit(1)


if __name__ == "__main__":
    main()