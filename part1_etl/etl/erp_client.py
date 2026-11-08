import asyncio
import logging
from urllib.parse import quote

import httpx

log = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
RETRY_DELAY = 2  # the ERP asks for "retry in 2s"


class ErpError(Exception):
    pass


class ErpClient:
    def __init__(self, base_url: str, user: str, password: str):
        self._http = httpx.AsyncClient(base_url=base_url, timeout=10)
        self._auth = (user, password)
        self._token = None
        self._token_lock = asyncio.Lock()

    async def __aenter__(self):
        await self._login()
        return self

    async def __aexit__(self, *exc):
        await self._http.aclose()

    async def get_locations(self) -> set[str]:
        r = await self._get("/api/v1/locations")
        return {loc["code"] for loc in r.json()["data"]}

    async def get_assets(self) -> list[dict]:
        rows, page = [], 1
        while True:
            r = await self._get("/api/v1/assets", page=page)
            data = r.json()["data"]
            if not data:
                break
            log.info("page=%d rows=%d", page, len(data))
            rows.extend(data)
            page += 1

        total = int(r.headers.get("X-Total-Count", -1))
        if total != len(rows):
            log.warning("row count mismatch read=%d x_total_count=%d", len(rows), total)
        else:
            log.info("assets read=%d x_total_count=%d", len(rows), total)
        return rows

    async def get_readings(self, code: str) -> list[dict]:
        r = await self._get(f"/api/v1/assets/{quote(code, safe='')}/readings")
        return r.json()["data"]

    async def _login(self):
        r = await self._http.post("/auth/token", auth=self._auth)
        r.raise_for_status()
        self._token = r.json()["access_token"]

    async def _refresh_token(self, expired_token):
        # Several workers get 401 at once: only the first one logs in.
        async with self._token_lock:
            if self._token == expired_token:
                await self._login()
                log.info("token refreshed")

    async def _get(self, path: str, **params) -> httpx.Response:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            token = self._token
            try:
                r = await self._http.get(
                    path, params=params, headers={"Authorization": f"Bearer {token}"}
                )
            except httpx.TransportError as e:
                reason = repr(e)
            else:
                if r.status_code == 401:
                    await self._refresh_token(token)
                    continue
                if r.status_code >= 500:
                    reason = f"HTTP {r.status_code}"
                else:
                    r.raise_for_status()
                    body = r.json()
                    # The ERP may answer 200 with an error in the body (rate limit).
                    if "error" not in body:
                        return r
                    reason = body["error"]

            log.warning("retry path=%s attempt=%d reason=%s", path, attempt, reason)
            if attempt < MAX_ATTEMPTS:
                await asyncio.sleep(RETRY_DELAY)

        raise ErpError(f"GET {path} failed after {MAX_ATTEMPTS} attempts")
