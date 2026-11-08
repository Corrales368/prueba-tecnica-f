"""Usage: docker compose run --rm etl python verify.py (after two ETL runs). Exit 0 = CORRECT."""
import sys
from collections import Counter
from datetime import timezone

import psycopg

from etl import config

results = []


def check(label, actual, expected):
    ok = actual == expected
    results.append(ok)
    line = f"{'OK  ' if ok else 'FAIL'} {label}: {actual!r}"
    print(line if ok else f"{line} (expected {expected!r})")


def utc(value):
    return value.astimezone(timezone.utc).isoformat()


def main() -> int:
    try:
        conn = psycopg.connect(config.DATABASE_URL)
    except psycopg.Error as e:
        print(f"FAIL cannot connect to the database: {e}")
        return 1

    with conn:
        def all_rows(sql, *params):
            return conn.execute(sql, params).fetchall()

        def one(sql, *params):
            return conn.execute(sql, params).fetchone()[0]

        try:
            one("SELECT 1 FROM runs LIMIT 1")
        except psycopg.errors.UndefinedTable:
            print("FAIL tables not found: run the ETL first (docker compose run --rm etl)")
            return 1

        # Expected values come from the mock's data (asset i = 1..54): status None when
        # i % 6 == 4 (9), cost None when i % 6 == 2 (9), LOC-Z for i = 23 and 41 (2).
        check("assets", one("SELECT count(*) FROM assets"), 34)
        check("asset_readings", one("SELECT count(*) FROM asset_readings"), 49)
        check("rejected_assets", one("SELECT count(*) FROM rejected_assets"), 20)

        rejected = all_rows("SELECT code, reasons FROM rejected_assets ORDER BY code")
        by_field = Counter(r.split(":")[0] for _, reasons in rejected for r in reasons)
        check("rejection reasons by field", dict(sorted(by_field.items())),
              {"acquisition_cost": 9, "parent_location": 2, "status": 9})
        check("rejected for unknown location",
              [code for code, reasons in rejected
               if any(r.startswith("parent_location") for r in reasons)],
              ["EQ-023", "EQ-041"])

        check("codes with '/' loaded with readings",
              [r[0] for r in all_rows(
                  "SELECT DISTINCT a.code FROM assets a JOIN asset_readings r USING (code)"
                  " WHERE a.code LIKE '%%/%%' ORDER BY a.code")],
              ["EQ-012/A", "EQ-031/B", "EQ-045/C"])

        check("truncated names (code, length)",
              all_rows("SELECT code, length(name) FROM assets"
                       " WHERE warnings::text LIKE '%%name: truncated%%' ORDER BY code"),
              [("EQ-013", 50), ("EQ-039", 50)])

        check("EQ-003 installed_at (came as '13/04/2026')",
              utc(one("SELECT installed_at FROM assets WHERE code = 'EQ-003'")),
              "2026-04-13T05:00:00+00:00")

        check("EQ-005 cost (came as '12.500,00')",
              one("SELECT cost::text FROM assets WHERE code = 'EQ-005'"), "12500.00")

        check("assets without readings",
              one("SELECT count(*) FROM assets a WHERE NOT EXISTS"
                  " (SELECT 1 FROM asset_readings r WHERE r.code = a.code)"), 0)
        check("EQ-012/A latest reading (meter, value, read_at)",
              [(m, v, utc(t)) for m, v, t in all_rows(
                  "SELECT meter, value::text, read_at FROM asset_readings"
                  " WHERE code = 'EQ-012/A' ORDER BY meter")],
              [("MED-01", "444.8", "2026-08-14T11:15:00+00:00")])

        check("runs recorded (>= 2)", one("SELECT count(*) FROM runs") >= 2, True)
        last = one("SELECT summary FROM runs ORDER BY id DESC LIMIT 1")
        check("last run (inserted, updated, unchanged, failed)",
              (last["loaded"]["inserted"], last["loaded"]["updated"],
               last["loaded"]["unchanged"], last["failed"]),
              (0, 0, 34, 0))

    failed = results.count(False)
    print(f"\nRESULT: {'CORRECT' if not failed else f'INCORRECT ({failed} checks failed)'}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
