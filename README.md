# Technical test: Python developer, integrations

One folder per part of the test:

| Folder | Part |
|---|---|
| [part1_etl/](part1_etl/) | Part 1: async ETL that pulls assets from an intentionally unreliable ERP (a local mock) and loads them into Postgres without duplicates |
| [part2_transform_registry/](part2_transform_registry/) | Part 2: review of code running in production |
| [part3_architecture_review/](part3_architecture_review/) | Part 3: diagram of the architecture review (the review itself is in the report) |
| [REPORT.md](REPORT.md) / [REPORT.pdf](REPORT.pdf) | The report, in Spanish: Part 1 data problems, Parts 2 and 3, AI usage |

## Part 1 quick start

Requires Docker with Compose.

```
cd part1_etl
copy .env.example .env                          # bash/zsh: cp .env.example .env
docker compose up -d --wait                     # Postgres + ERP mock
docker compose run --rm --build etl             # run 1
docker compose run --rm etl                     # run 2
docker compose run --rm etl python verify.py    # must end with RESULT: CORRECT
```

This quick start reuses the database if one already exists. For a clean start, the
expected numbers of each run and troubleshooting, follow [AGENTS.md](AGENTS.md).
Evidence of two consecutive runs and the database dump: [part1_etl/evidence/](part1_etl/evidence/).

## Part 2 quick start

```
cd part2_transform_registry
docker compose run --rm --build tests            # must end with 35 passed
```
