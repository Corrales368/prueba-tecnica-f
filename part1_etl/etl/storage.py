from datetime import datetime

from psycopg.types.json import Jsonb
from psycopg_pool import AsyncConnectionPool

from etl.schema import Asset

SCHEMA = """
CREATE TABLE IF NOT EXISTS assets (
    code          TEXT PRIMARY KEY,
    name          VARCHAR(50)    NOT NULL,
    active        BOOLEAN        NOT NULL,
    cost          NUMERIC(12, 2) NOT NULL,
    location      TEXT           NOT NULL,
    installed_at  TIMESTAMPTZ    NOT NULL,
    record_hash   CHAR(64)       NOT NULL,
    warnings      JSONB          NOT NULL,
    created_at    TIMESTAMPTZ    NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ    NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS asset_readings (
    code     TEXT        NOT NULL REFERENCES assets (code) ON DELETE CASCADE,
    meter    TEXT        NOT NULL,
    value    NUMERIC     NOT NULL,
    read_at  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (code, meter)
);

CREATE TABLE IF NOT EXISTS rejected_assets (
    code         TEXT PRIMARY KEY,
    reasons      JSONB       NOT NULL,
    raw          JSONB       NOT NULL,
    rejected_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS runs (
    id           SERIAL PRIMARY KEY,
    started_at   TIMESTAMPTZ NOT NULL,
    finished_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    summary      JSONB       NOT NULL
);
"""

# Updates only if the hash changed. xmax = 0 means the row came from an INSERT.
UPSERT_ASSET = """
INSERT INTO assets (code, name, active, cost, location, installed_at, record_hash, warnings)
VALUES (%(code)s, %(name)s, %(active)s, %(cost)s, %(location)s, %(installed_at)s,
        %(record_hash)s, %(warnings)s)
ON CONFLICT (code) DO UPDATE SET
    name         = EXCLUDED.name,
    active       = EXCLUDED.active,
    cost         = EXCLUDED.cost,
    location     = EXCLUDED.location,
    installed_at = EXCLUDED.installed_at,
    record_hash  = EXCLUDED.record_hash,
    warnings     = EXCLUDED.warnings,
    updated_at   = now()
WHERE assets.record_hash <> EXCLUDED.record_hash
RETURNING (xmax = 0) AS inserted
"""

UPSERT_REJECTED = """
INSERT INTO rejected_assets (code, reasons, raw)
VALUES (%s, %s, %s)
ON CONFLICT (code) DO UPDATE SET
    reasons     = EXCLUDED.reasons,
    raw         = EXCLUDED.raw,
    rejected_at = now()
"""


class Storage:
    def __init__(self, conninfo: str, pool_size: int):
        self._pool = AsyncConnectionPool(conninfo, min_size=1, max_size=pool_size, open=False)

    async def __aenter__(self):
        await self._pool.open()
        async with self._pool.connection() as conn:
            await conn.execute(SCHEMA)
        return self

    async def __aexit__(self, *exc):
        await self._pool.close()

    async def save_asset(self, asset: Asset) -> str:
        async with self._pool.connection() as conn, conn.transaction():
            cur = await conn.execute(UPSERT_ASSET, {
                "code": asset.code,
                "name": asset.name,
                "active": asset.active,
                "cost": asset.cost,
                "location": asset.location,
                "installed_at": asset.installed_at,
                "record_hash": asset.record_hash,
                "warnings": Jsonb(asset.warnings),
            })
            row = await cur.fetchone()

            if row is None:
                result = "unchanged"
            else:
                result = "inserted" if row[0] else "updated"
                await conn.execute("DELETE FROM asset_readings WHERE code = %s", (asset.code,))
                for r in asset.readings:
                    await conn.execute(
                        "INSERT INTO asset_readings (code, meter, value, read_at)"
                        " VALUES (%s, %s, %s, %s)",
                        (asset.code, r.meter, r.value, r.read_at),
                    )

            # If it was rejected in an earlier run, it no longer is.
            await conn.execute("DELETE FROM rejected_assets WHERE code = %s", (asset.code,))
            return result

    async def save_rejected(self, code: str, reasons: list[str], raw: dict) -> None:
        async with self._pool.connection() as conn:
            await conn.execute(UPSERT_REJECTED, (code, Jsonb(reasons), Jsonb(raw)))

    async def save_run(self, started_at: datetime, summary: dict) -> int:
        async with self._pool.connection() as conn:
            cur = await conn.execute(
                "INSERT INTO runs (started_at, summary) VALUES (%s, %s) RETURNING id",
                (started_at, Jsonb(summary)),
            )
            return (await cur.fetchone())[0]
