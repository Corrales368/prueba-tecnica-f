# Technical test: Python developer, integrations

One folder per part of the test:

| Folder | Part |
|---|---|
| [part1_etl/](part1_etl/) | Part 1: async ETL that pulls assets from an intentionally unreliable ERP (a local mock) and loads them into Postgres without duplicates |
| [part2_transform_registry/](part2_transform_registry/) | Part 2: review of code running in production |

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
