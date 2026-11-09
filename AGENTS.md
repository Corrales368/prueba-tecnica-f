# AGENTS.md

Context for an AI agent (or a person) who has to run this project without its author:
start the ERP mock, run the full process, and tell a correct result from an incorrect one.
Part 2's tests are covered too.

## What this repo is

Technical test for a Python integrations role, one folder per part:

```
REPORT.md / REPORT.pdf       the report (in Spanish): Part 1 data problems, Parts 2 and 3,
                             AI usage. The PDF is an export of REPORT.md, which is the source
part1_etl/                   Part 1: async ETL, ERP (mock) -> Postgres. Runs with Docker.
  compose.yaml               services: db (Postgres), mock (ERP), etl (runs on demand)
  etl/                       the ETL (Python package)
    erp_client.py            extract: token refresh, retries, pagination, readings
    schema.py                transform: validation rules (single place), latest reading
                             per meter, normalization, hash
    storage.py               load: Postgres tables and upserts
    pipeline.py              work queue with N workers, run summary
    __main__.py              entry point: python -m etl
  mock/                      ERP mock provided with the test (mock_erp_2.py, unmodified)
                             + server.py, which runs it inside Docker
  tests/                     pytest (transformation rules)
  verify.py                  checks the database: prints RESULT: CORRECT / INCORRECT
  evidence/                  logs of two consecutive runs + database dump
part2_transform_registry/    Part 2: review of code running in production
  transform_registry_2.py    the original, as delivered (unmodified)
  transform_registry.py      the hotfix: no eval, only registered operations
  tests/                     pytest: same outputs as the original, attacks rejected
  compose.yaml               one service, tests
part3_architecture_review/   Part 3: the review itself is in REPORT.md
  diagram.md / diagram.png   the proposal with the review's comments marked (Mermaid + export)
```

## Part 1

### Prerequisites

- Docker with Compose v2 or later (`docker compose version`), with the Docker daemon running.
- Free ports on 127.0.0.1: **8099** (mock) and **5433** (Postgres). They can be changed in `.env`.
- Nothing else: Python runs inside the containers.

### Run it

Every Part 1 command runs from the `part1_etl/` folder:

```
cd part1_etl
```

If your shell does not keep the working folder between commands, run them from the
repository root as `docker compose --project-directory part1_etl ...` instead
(it also reads `part1_etl/.env`).

1. Create the config (fictitious local values). Skip this step if `.env` already exists.
   - PowerShell or cmd: `copy .env.example .env`
   - bash/zsh (Linux, macOS, Git Bash): `cp .env.example .env`
2. Start from a clean database. **This deletes the database volume of this Compose project.**
   The project name is the folder name (`part1_etl`), so any other copy of this repo on the
   same machine, running or stopped, shares that volume. To check whether one exists:
   `docker volume ls --filter name=part1_etl_pgdata`. On a fresh checkout, any volume it
   lists belongs to another copy: see "Two copies on one machine" below first.
   ```
   docker compose down -v
   ```
3. Start Postgres and the ERP mock and wait until both are healthy:
   ```
   docker compose up -d --wait
   ```
4. Run 1 (`--build` makes sure the image matches the current code):
   ```
   docker compose run --rm --build etl
   ```
5. Run 2, right after:
   ```
   docker compose run --rm etl
   ```
6. Verify:
   ```
   docker compose run --rm etl python verify.py
   ```

The first time, Docker downloads the Postgres and Python images and installs the ETL
dependencies (1 to 3 minutes). After that, each run takes about 5 seconds and ends with
four `summary` lines.

### What a correct result looks like

| summary field | Run 1 | Run 2 |
|---|---|---|
| read / unique / duplicates | 57 / 54 / 3 | 57 / 54 / 3 |
| transformed | 34 | 34 |
| inserted / updated / unchanged | 34 / 0 / 0 | **0 / 0 / 34** |
| rejected | 20 | 20 |
| reasons_by_field | acquisition_cost 9, status 9, parent_location 2 | same |
| failed | 0 | 0 |
| warnings_by_field | installed_at 18, name 2 | same |
| exit code | 0 | 0 |

Run 1 shows inserted=34 only when it starts from a clean database (step 2).

`verify.py` must print 13 lines starting with `OK` and end with `RESULT: CORRECT`
(exit code 0). It needs at least two runs, because it checks that the last one changed nothing.

### What an incorrect result looks like

- `verify.py` prints any `FAIL` line, ends with `RESULT: INCORRECT`, or exits with 1.
- A summary shows `failed` greater than 0, or a run ends with `ERROR etl run aborted` (exit code 1).
- Run 2 shows `inserted` or `updated` greater than 0: the process is not idempotent.
- Any number differs from the table above.

### Expected noise: these lines are NOT errors

The mock simulates a real, unreliable ERP. Every correct run logs these lines:

| Log line | Why it is fine |
|---|---|
| `WARNING ... retry path=/api/v1/assets attempt=1 reason=rate limit exceeded, retry in 2s` (usually 1) | Page 3 answers HTTP 200 with an error body once per token; the client waits and retries |
| `INFO ... token refreshed` (usually 1) | Tokens die after 25 calls or 20 seconds; the client gets a new one and repeats the call |
| `INFO ... duplicate code=...` (EQ-007, EQ-019, EQ-033) | Page 4 repeats 3 assets with a newer `updated_at`; the newest version is kept |
| `INFO ... rejected code=... reasons=[...]` (20 lines) | Null status, null cost or unknown location (LOC-Z): stored in `rejected_assets` with the reason; the batch goes on |
| `WARNING ... installed_at: no timezone, assumed -05:00` (18 lines) | Dates like `13/04/2026` come without time zone; every other date of this ERP is -05:00 |
| `WARNING ... name: truncated from 83 to 50 chars` (2 lines) | The contract allows 50 characters; the truncation is recorded |
| `WARNING: Running pip as the 'root' user ...` (only while building the image) | pip's advice for regular machines; inside the container it does not matter |

The number of retry and `token refreshed` lines depends on timing: any number is fine as
long as the summary matches. Judge the result with `verify.py` and the tables above, not by
the absence of WARNING lines.

### Inspect the database

- One query, no terminal needed (works for agents):
  `docker compose exec -T db psql -U etl -d etl -c "SELECT count(*) FROM assets"`
- Interactive console: `docker compose exec db psql -U etl -d etl`
- Any client: host `localhost`, port `DB_HOST_PORT` from `.env` (5433), database `etl`,
  user `etl`, password `POSTGRES_PASSWORD` from `.env`.
- Tables: `assets`, `asset_readings`, `rejected_assets`, `runs` (one row per run with its summary).

### Troubleshooting

| Symptom | Fix |
|---|---|
| `missing .env (copy .env.example to .env)` or `env file ... not found` | Do step 1 (from `part1_etl/`) |
| `no configuration file provided: not found` | You are not in `part1_etl/` |
| `port is already allocated` (8099 or 5433) | Another program uses the port: change `MOCK_HOST_PORT` or `DB_HOST_PORT` in `.env`. The ETL does not use these host ports |
| `password authentication failed for user "etl"` | The database volume was created with another password: `docker compose down -v`, then step 3 |
| `Cannot connect to the Docker daemon` / `failed to connect to the docker API` | Start Docker Desktop or the Docker service |

### Two copies on one machine

Copies of this repo whose folder has the same name (`part1_etl`) share one Compose project:
containers, database volume, network and ETL image (`--build` in one copy replaces the
other's image). To isolate one copy, edit its `.env` before step 2: change the two ports,
which are already there, and add the project name. All of those names then derive from
`part1_etl_check`:

```
COMPOSE_PROJECT_NAME=part1_etl_check
MOCK_HOST_PORT=18099
DB_HOST_PORT=15433
```

### Other commands

- Tests: `docker compose run --rm etl pytest` (correct: `28 passed`, exit code 0)
- Regenerate the evidence in `evidence/`:
  ```
  docker compose down -v
  docker compose up -d --wait
  docker compose run --rm --build etl python -m etl --log-file evidence/run1.log
  docker compose run --rm etl python -m etl --log-file evidence/run2.log
  docker compose exec -T db pg_dump -U etl -d etl --no-owner -f /tmp/dump.sql
  docker compose cp db:/tmp/dump.sql evidence/dump.sql
  ```
- Stop, keeping the data: `docker compose down`
- Remove this project's containers, database volume, network and ETL image
  (same warning as step 2 if another copy exists):
  `docker compose --profile etl down -v --rmi local`.
  It keeps `.env`, the base images (`postgres:17-alpine`, `python:3.12-slim`) and
  Docker's build cache.

## Part 2

No `.env` and no ports needed. Every Part 2 command runs from the repository root:

```
docker compose --project-directory part2_transform_registry run --rm --build tests
```

Correct: the last line contains `35 passed` (exit code 0). Any `failed` or `error` is incorrect.

Optional, to see the fix by hand (after the command above, which builds the image):

```
docker compose --project-directory part2_transform_registry run --rm tests python transform_registry.py suma 1 2
docker compose --project-directory part2_transform_registry run --rm tests python transform_registry_2.py "os.getcwd()" 1 2
docker compose --project-directory part2_transform_registry run --rm tests python transform_registry.py "os.getcwd()" 1 2
```

Expected, in order: `3.0`; `/app` (the original ran the code it was sent); and a traceback ending
in `OperationNotAllowed: operation not allowed: 'os.getcwd()'`, exit code 1 (the fix rejects it).

If another copy of this repo exists on the same machine, both share the image
`part2_transform_registry-tests`: add `-p part2_transform_registry_check` right after
`docker compose` in every Part 2 command.

Remove the image when done: `docker image rm part2_transform_registry-tests`
(`part2_transform_registry_check-tests` if you used `-p`).

## Part 3

Nothing to run: the review is the "Punto 3" section of `REPORT.md`, and
`part3_architecture_review/diagram.md` draws the proposal with the review's codes (a1, b2...).

## Rules for agents

- Do not modify `part1_etl/mock/mock_erp_2.py` or `part2_transform_registry/transform_registry_2.py`:
  they are the original material of the test.
- Do not edit files in `part1_etl/evidence/` by hand; regenerate them with the commands above.
- Do not edit `REPORT.pdf` or `part3_architecture_review/diagram.png` by hand: they are exports of
  `REPORT.md` and `diagram.md`.
