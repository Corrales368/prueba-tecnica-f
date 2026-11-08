import argparse
import asyncio
import logging
import sys

from etl.pipeline import run


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m etl", description="Runs the ERP -> Postgres ETL once.")
    parser.add_argument("--log-file", help="also write the log to this file, e.g. evidence/run1.log")
    args = parser.parse_args()

    handlers = [logging.StreamHandler()]
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file, mode="w", encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=handlers,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    try:
        summary = asyncio.run(run())
    except Exception:
        logging.getLogger("etl").exception("run aborted")
        return 1
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
