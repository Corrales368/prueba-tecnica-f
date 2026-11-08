#!/usr/bin/env python3
"""
Mock de ERP para la prueba tecnica de integraciones ETL.

Sin dependencias: python3 mock_erp.py  ->  http://localhost:8099
Datos 100% ficticios y deterministas. No contiene informacion de clientes reales.

Endpoints
---------
POST /auth/token                      Basic auth -> {"access_token", "expires_in"}
GET  /api/v1/locations                catalogo de ubicaciones validas
GET  /api/v1/assets?page=N            activos, paginado (20 por pagina)
GET  /api/v1/assets/{code}/readings   lecturas de medidor del activo
"""
import base64
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

PORT = 8099
USER, PASSWORD = "candidato", "prueba2026"
TOKEN_TTL = 20        # segundos
TOKEN_MAX_CALLS = 25

_tokens = {}          # token -> [emitido_en, llamadas_usadas]
_page3_served = set() # tokens a los que ya se les entrego la pagina 3

LOCATIONS = ["LOC-A", "LOC-B", "LOC-C", "LOC-D", "LOC-E"]

LONG_NAME = (
    "Compresor de tornillo rotativo refrigerado por aceite de la linea de envasado norte"
)


def _asset(i):
    """Genera el activo i (1..54) de forma determinista."""
    code = f"EQ-{i:03d}"
    if i == 12:
        code = "EQ-012/A"
    elif i == 31:
        code = "EQ-031/B"
    elif i == 45:
        code = "EQ-045/C"

    name = f"Equipo {i:03d}" if i % 13 else LONG_NAME
    status = ["1", "0", "Activo", "Inactivo", None, "1"][i % 6]
    cost = ["1.234,56", 1234.56, None, "890,10", 45000.0, "12.500,00"][i % 6]
    loc = LOCATIONS[i % 5]
    if i in (23, 41):
        loc = "LOC-Z"  # ubicacion que no existe en el catalogo
    installed = (
        f"2026-0{(i % 8) + 1}-1{i % 9}T0{i % 9}:30:00-05:00"
        if i % 3
        else f"1{i % 9}/0{(i % 8) + 1}/2026"
    )
    return {
        "code": code,
        "name": name,
        "status": status,
        "acquisition_cost": cost,
        "parent_location": loc,
        "installed_at": installed,
        "updated_at": f"2026-08-{10 + (i % 15):02d}T12:00:00-05:00",
    }


def _page(n):
    """Paginas 1..4. La 4 repite 3 activos ya entregados, con datos mas frescos."""
    if n in (1, 2, 3):
        rows = [_asset(i) for i in range((n - 1) * 20 + 1, n * 20 + 1)]
        return rows[:14] if n == 3 else rows
    if n == 4:
        dups = []
        for i in (7, 19, 33):
            d = _asset(i)
            d["updated_at"] = "2026-08-24T09:00:00-05:00"
            d["status"] = "0"
            dups.append(d)
        return dups
    return []


def _readings(code):
    seed = sum(ord(c) for c in code)
    out = []
    for meter in ("MED-01", "MED-02")[: 1 + seed % 2]:
        for k in range(2 + seed % 3):
            out.append(
                {
                    "meter": meter,
                    "value": round(100 + seed * 0.7 + k * 13.5, 2),
                    "read_at": f"2026-08-{12 + k:02d}T0{(seed + k) % 9}:15:00-05:00",
                }
            )
    return out


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  {self.command} {self.path} -> {args[1] if len(args) > 1 else ''}")

    def _send(self, code, payload, headers=None):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _token(self):
        raw = self.headers.get("Authorization", "")
        if not raw.startswith("Bearer "):
            return None
        tk = raw[7:]
        st = _tokens.get(tk)
        if st is None or time.time() - st[0] > TOKEN_TTL or st[1] >= TOKEN_MAX_CALLS:
            return None
        st[1] += 1
        return tk

    def do_POST(self):
        if urlparse(self.path).path != "/auth/token":
            return self._send(404, {"error": "not found"})
        raw = self.headers.get("Authorization", "")
        ok = False
        if raw.startswith("Basic "):
            try:
                u, _, p = base64.b64decode(raw[6:]).decode().partition(":")
                ok = (u, p) == (USER, PASSWORD)
            except Exception:
                ok = False
        if not ok:
            return self._send(401, {"error": "invalid credentials"})
        tk = f"tk-{int(time.time() * 1000000)}"
        _tokens[tk] = [time.time(), 0]
        self._send(200, {"access_token": tk, "expires_in": TOKEN_TTL})

    def do_GET(self):
        u = urlparse(self.path)
        path, qs = u.path, parse_qs(u.query)
        tk = self._token()
        if tk is None:
            return self._send(401, {"error": "token expired or missing"})

        if path == "/api/v1/locations":
            return self._send(200, {"data": [{"code": c} for c in LOCATIONS]})

        if path == "/api/v1/assets":
            n = int(qs.get("page", ["1"])[0])
            if n == 3 and tk not in _page3_served:
                _page3_served.add(tk)
                return self._send(
                    200, {"error": "rate limit exceeded, retry in 2s", "data": []}
                )
            rows = _page(n)
            return self._send(
                200,
                {"data": rows, "page": n, "page_size": 20},
                {"X-Total-Count": "57"},
            )

        if path.startswith("/api/v1/assets/") and path.endswith("/readings"):
            raw = path[len("/api/v1/assets/") : -len("/readings")]
            if "/" in raw:
                return self._send(404, {"error": "asset not found"})
            code = unquote(raw)
            time.sleep(0.35)  # el ERP es lento a proposito
            known = {_asset(i)["code"] for i in range(1, 55)}
            if code not in known:
                return self._send(404, {"error": "asset not found"})
            return self._send(200, {"data": _readings(code)})

        self._send(404, {"error": "not found"})


if __name__ == "__main__":
    print(f"Mock ERP escuchando en http://localhost:{PORT}")
    print(f"  usuario: {USER} / password: {PASSWORD}   (Basic auth en /auth/token)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
