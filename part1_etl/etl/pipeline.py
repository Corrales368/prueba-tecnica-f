import asyncio
import logging
import time
from collections import Counter
from datetime import datetime, timezone

import httpx
from pydantic import ValidationError

from etl import config
from etl.erp_client import ErpClient, ErpError
from etl.schema import latest_readings, normalize, validate
from etl.storage import Storage

log = logging.getLogger(__name__)

OLDEST = datetime.min.replace(tzinfo=timezone.utc)


async def run() -> dict:
    started_at = datetime.now(timezone.utc)
    t0 = time.monotonic()

    async with (
        ErpClient(config.ERP_BASE_URL, config.ERP_USER, config.ERP_PASSWORD) as erp,
        Storage(config.DATABASE_URL, pool_size=config.WORKERS) as db,
    ):
        locations = await erp.get_locations()
        rows = await erp.get_assets()
        unique = deduplicate(rows)

        queue = asyncio.Queue()
        for row in unique:
            queue.put_nowait(row)

        batch = Batch(erp, db, locations)
        workers = [asyncio.create_task(batch.worker(queue)) for _ in range(config.WORKERS)]
        await queue.join()
        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

        summary = {
            "read": len(rows),
            "unique": len(unique),
            "duplicates": len(rows) - len(unique),
            "transformed": batch.transformed,
            "loaded": dict(batch.loaded),
            "rejected": batch.rejected,
            "reasons_by_field": dict(batch.reasons_by_field),
            "failed": batch.failed,
            "warnings_by_field": dict(batch.warnings_by_field),
            "seconds": round(time.monotonic() - t0, 2),
        }
        run_id = await db.save_run(started_at, summary)

    log.info("summary run_id=%s read=%d unique=%d duplicates=%d",
             run_id, summary["read"], summary["unique"], summary["duplicates"])
    log.info("summary transformed=%d inserted=%d updated=%d unchanged=%d",
             summary["transformed"], batch.loaded["inserted"], batch.loaded["updated"],
             batch.loaded["unchanged"])
    log.info("summary rejected=%d reasons_by_field=%s",
             summary["rejected"], summary["reasons_by_field"])
    log.info("summary failed=%d warnings_by_field=%s seconds=%s",
             summary["failed"], summary["warnings_by_field"], summary["seconds"])
    return summary


def deduplicate(rows: list) -> list:
    # One row per code: the newest updated_at wins; on a tie, the later row.
    latest, without_code = {}, []
    for row in rows:
        code = _code(row)
        if code is None:
            without_code.append(row)
            continue
        kept = latest.get(code)
        if kept is None:
            latest[code] = row
            continue
        newer, older = (row, kept) if _updated_at(row) >= _updated_at(kept) else (kept, row)
        latest[code] = newer
        log.info("duplicate code=%s kept_updated_at=%s discarded_updated_at=%s",
                 code, newer.get("updated_at"), older.get("updated_at"))
    return list(latest.values()) + without_code


class Batch:
    def __init__(self, erp: ErpClient, db: Storage, locations: set[str]):
        self.erp, self.db, self.locations = erp, db, locations
        self.transformed = self.rejected = self.failed = 0
        self.loaded = Counter({"inserted": 0, "updated": 0, "unchanged": 0})
        self.reasons_by_field = Counter()
        self.warnings_by_field = Counter()

    async def worker(self, queue: asyncio.Queue):
        while True:
            row = await queue.get()
            try:
                await self.process(row)
            except Exception:
                # One broken row must not stop the batch.
                self.failed += 1
                log.exception("failed code=%s", _code(row))
            finally:
                queue.task_done()

    async def process(self, row):
        # a. validation
        erp_asset, reasons = validate(row, self.locations)
        if reasons:
            await self.reject(row, reasons)
            return

        # b. enrichment
        try:
            readings = latest_readings(await self.erp.get_readings(erp_asset.code))
        except (ErpError, httpx.HTTPError, ValidationError) as e:
            await self.reject(row, [f"readings: {e}"])
            return

        # c. normalization + hash
        asset = normalize(erp_asset, readings)
        self.transformed += 1
        for w in asset.warnings:
            self.warnings_by_field[w.split(":")[0]] += 1
            log.warning("warning code=%s %s", asset.code, w)

        # d. persistence
        result = await self.db.save_asset(asset)
        self.loaded[result] += 1
        log.info("asset code=%s result=%s", asset.code, result)

    async def reject(self, row, reasons: list[str]):
        self.rejected += 1
        for r in reasons:
            self.reasons_by_field[r.split(":")[0]] += 1

        code = _code(row)
        if code is None:
            log.error("rejected without code (not stored) reasons=%s raw=%s", reasons, row)
            return
        await self.db.save_rejected(code, reasons, row)
        log.info("rejected code=%s reasons=%s", code, reasons)


def _code(row):
    code = row.get("code") if isinstance(row, dict) else None
    return code if isinstance(code, str) and code else None


def _updated_at(row) -> datetime:
    try:
        value = datetime.fromisoformat(row["updated_at"])
    except (KeyError, TypeError, ValueError):
        return OLDEST
    return value if value.tzinfo else OLDEST
