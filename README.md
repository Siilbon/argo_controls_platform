# Argo Controls Platform

A React frontend backed by a Flask REST API for sharing Python utilities. Flask exposes every feature as JSON under `/api/` and, in production, also serves the built React app.

## Project Structure

```
├── acp_app/
│   ├── api/                  REST API blueprints (JSON responses for React)
│   ├── services/             Business logic — no HTTP awareness
│   ├── data/
│   │   └── raw/              Source CSVs, exports and XLS files for seeding the database (gitignored)
│   ├── commands.py           Flask CLI commands (init-db, init-team, etc.)
│   ├── frontend.py           Serves the built React app from frontend/dist
│   ├── models.py             SQLAlchemy ORM models
│   └── __init__.py           App factory
├── frontend/                 React + Vite + Tailwind app (see frontend/README.md)
├── instance/                 SQLite database lives here (gitignored)
├── tests/
├── .env.example              Template for environment variables
├── app.py                    Entry point
├── config.py                 Flask configuration classes
├── dev.sh                    Developer workflow script
├── requirements.txt
└── web.config                wfastcgi config for IIS
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Database status and dataset ages; `?aspen=1` also tests Aspen. 503 when something is down. Shown on the Status page |
| GET | `/api/datasets` | Row count and last load time for each dataset |
| GET | `/api/me` | Signed-in user from Windows Authentication |
| GET | `/api/team` | Team members list |
| GET | `/api/aspen/<table>/<term>?col=NAME` | Aspen definition search; `table` is `analog`, `discrete`, `iogetdef` or `iogethistdef` |
| GET | `/api/aspen/trend?tags=A,B&hours=8` | Interpolated history for trending (or `start`/`end` instead of `hours`) |
| GET | `/api/aspen/nodeid?tags=A,B&field=IP_INPUT_VALUE&raw=1` | OPC UA node IDs IT uses to read IP21 through IoTHub; `raw=0` for the ns=2 IDs |
| GET | `/api/aspen/status` | Aspen IO status |
| GET | `/api/intellution/<term>?col=tag` | Intellution tag search |
| GET | `/api/deltav/<term>?col=name` | DeltaV module search |
| GET | `/api/deltav-io/<term>?col=tag` | DeltaV IO channel and DST search |
| POST | `/api/gcc/eos` | EOS code → plain English |
| GET | `/api/ttparser/<name>/<seq>` | Truthtable lookup |

## First-Time Setup

1. Create and fill in your local environment file:
   ```bash
   cp .env.example .env.local
   # edit .env.local with your values
   ```

2. Clone [mfgkit](https://github.com/Siilbon/mfgkit) next to this project. It holds the Aspen, Intellution, and DeltaV parsers, and `requirements.txt` installs it in editable mode from `../mfgkit`:
   ```
   <parent folder>/
   ├── argo_controls_platform/
   └── mfgkit/
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Create the tables and load every dataset in one go:
   ```bash
   ./dev.sh flask init-all
   ```
   It runs `init-db` and then each load below. A load that fails (usually missing files) is reported and skipped, the rest still run, and the command exits with an error listing what failed.

5. Or run the steps one at a time:
   ```bash
   ./dev.sh flask init-db           # create database tables
   ./dev.sh flask init-intellution  # requires files in acp_app/data/raw/intellution/
   ./dev.sh flask init-deltav       # requires MODT.TXT, ANT.TXT, DT.TXT in acp_app/data/raw/deltav/Argo01/ and Argo02/
   ./dev.sh flask init-deltav-io    # requires .fhx exports in acp_app/data/raw/deltav/Argo01/ and Argo02/
   ./dev.sh flask init-team         # requires files in acp_app/data/raw/team/
   ./dev.sh flask init-ttparser     # requires files in acp_app/data/raw/gcc/
   ```

6. Start the Flask dev server on port 5001 (the React dev server proxies `/api` there):
   ```bash
   ./dev.sh flask run --debug --port 5001
   ```

7. In a second terminal, install frontend dependencies and start the React dev server:
   ```bash
   cd frontend
   npm install      # first time only
   npm run dev
   ```
   Open http://localhost:5173.

## Running the Frontend

The React app lives in `frontend/` and requires Node.js. During development, run **both** servers:

| Terminal | Command | URL |
|----------|---------|-----|
| 1 (project root) | `./dev.sh flask run --debug --port 5001` | http://localhost:5001 |
| 2 (`frontend/`) | `npm run dev` | http://localhost:5173 |

Vite forwards any request starting with `/api` to `http://localhost:5001` (configured in `frontend/vite.config.js`), so frontend code calls relative paths like `fetch('/api/team')`. If Flask runs on a different port, API calls from the frontend will fail.

See [frontend/README.md](frontend/README.md) for the other npm scripts.

## Deploying

In production there is one server: Flask serves both `/api/` and the built React app.

1. Build the frontend (needs Node.js on the build machine only, not the server):
   ```bash
   cd frontend
   npm ci
   npm run build     # writes frontend/dist/
   ```
2. Copy the project (including `frontend/dist/`, but not `node_modules/` or `.venv/`) and `mfgkit/` to the server, and install the Python requirements there.
3. Set the production environment variables: `DATABASE_URL`, `SECRET_KEY` and `ASPEN_SERVER` (see [Environment Variables](#environment-variables)). `web.config` already sets `FLASK_CONFIG=production` and `LOG_FILE`; keep secrets out of it. `CORS_ORIGINS` isn't needed because the frontend and API share an origin.
4. Turn on Windows Authentication in IIS. Install the **Windows Authentication** role service, then unlock the two authentication sections once per server; the commands are in `web.config`. Without the unlock, IIS answers every request with error 500.19.
5. Update the Python paths in `web.config`, load the database with the `init-*` commands below, and point IIS at `app.app`.
6. Check it: open the site, confirm your name shows in the top right, then open the **Status** page to see the database, Aspen connection and data ages at a glance.

### Sign-in and limits

- **Sign-in:** IIS signs people in with their domain account, so the app stores no passwords. In production the API answers `401 Sign-in required` to any request without a user, so a server where Windows Authentication isn't working serves no data. Set `REQUIRE_AUTH=false` only for testing.
- **Aspen:** searches stop at `ASPEN_SEARCH_MAX_ROWS` (the Aspen server itself stops there), and Aspen searches and trends are limited to `ASPEN_RATE_LIMIT` per user. The limit is counted per server process, so with several IIS worker processes it's approximate.
- **Monitoring:** `/api/health` returns 503 when the database, or Aspen with `?aspen=1`, is unreachable. It also lists each dataset's row count and last load time, which the search pages show as "Data loaded ..." and flag once data is over 30 days old.
- **Headers:** every response carries `X-Content-Type-Options`, `X-Frame-Options` and `Referrer-Policy` headers.

### Page URLs

Every page has its own URL, so the back button, bookmarks and shared links work, and Flask answers any non-API path with the React app:

| URL | Page |
|-----|------|
| `/search/deltav_io?q=WMCP05&col=controller` | A search (`intellution`, `deltav`, `deltav_io`, `aspen`) |
| `/search/aspen?table=analog&q=FT21&col=NAME` | Aspen search on one table |
| `/trend?tags=FT21001,TT21002&range=24&stacked=1` | A trend (`range` is hours, or `custom` with `start` and `end`) |
| `/gcc?eos=21` | GCC tools with an EOS type filled in |
| `/status` | System status: database, Aspen connection, signed-in user, and each dataset's rows, age and reload command |

`index.html` is sent with `Cache-Control: no-cache` so browsers pick up a new deploy; the hashed files in `dist/assets/` can be cached. Plotly is split into its own file and only downloads when someone opens a trend.

## CLI Commands

All commands are run via `dev.sh` to ensure the environment is loaded:

| Command | Description |
|---------|-------------|
| `./dev.sh flask init-all` | Create tables and run every load below, continuing past failures |
| `./dev.sh flask init-db` | Create all database tables |
| `./dev.sh flask init-intellution` | Load Intellution tag data |
| `./dev.sh flask init-deltav` | Load DeltaV module data |
| `./dev.sh flask init-deltav-io` | Load DeltaV IO channels and DSTs from FHX exports |
| `./dev.sh flask init-team` | Load team and unit data |
| `./dev.sh flask init-ttparser` | Load GCC Truthtable data |
| `./dev.sh flask run --debug --port 5001` | Start Flask dev server |

## Data File Schemas

### `acp_app/data/raw/team/team.csv`

One row per person. Multiple units for one person are separated by `|`.

| Column | Type | Description |
|--------|------|-------------|
| `name` | string | Full name |
| `role` | string | Job title |
| `email` | string | Email address (can be blank) |
| `linkedin` | string | Full LinkedIn URL (can be blank) |
| `active` | boolean | `true` to show, `false` to hide |
| `units` | string | Plant areas, pipe-separated: `Unit1\|Unit2` |

Example:
```csv
name,role,email,linkedin,active,units
John Doe,Controls Engineer,John@company.com,,true,Unit1|Unit2
Jane Doesnt,Controls Engineer,,,true,Utilities
```

### `acp_app/data/raw/intellution/`

iFIX tag database exports, one CSV per node: `WETMILL.csv`, `DEXTROSE.csv`, `REFINERY.csv`, `UTILITY.csv`. The file name becomes the `database` column, and the file's last-modified time becomes `uploaded` — copy exports in a way that keeps that time.

### `acp_app/data/raw/deltav/`

One subfolder per DeltaV system, `Argo01/` and `Argo02/`, each holding the flat-file tables from that system's download, copied as-is:

| File | Contents |
|------|----------|
| `MODT.TXT` | Modules: name, description, displays, area id, controller id |
| `ANT.TXT` | Plant areas (joined to modules by area id) |
| `DT.TXT` | Devices/controllers (joined to modules by controller id) |

The folder name becomes the `system` column, and each `MODT.TXT`'s last-modified time becomes the `uploaded` column. A system whose folder has no `MODT.TXT` is skipped.

`init-deltav-io` reads every `.fhx` file in the same `Argo01/` and `Argo02/` folders. Export the control network from DeltaV Explorer (right-click **Control Network** → **Export**) so the file includes every controller's IO cards and CHARMs. Classic cards, remote IO, wireless gateways and CHARMs are loaded; DeviceNet and serial IO are not. If a channel appears in more than one export, the copy from the newest file wins, and each file's last-modified time becomes `uploaded`.

Each channel gets a `status` to make spares easy to find:

| Status | Meaning |
|--------|---------|
| `Spare` | Disabled with no DST or DeltaV's default location DST (e.g. `WMCP04C12CH07`), or an empty CHARM slot |
| `Disabled` | Has a real DST but is disabled, so it may be reclaimable |
| `No DST` | Enabled but has no real DST; worth checking |
| `Assigned` | Enabled with a real DST |

## Environment Variables

See `.env.example` for a full template. Key variables:

| Variable | Description |
|----------|-------------|
| `FLASK_APP` | Entry point (`app.py`) |
| `FLASK_CONFIG` | `development`, `testing`, or `production` (the default) |
| `SECRET_KEY` | Random secret string |
| `DEV_DATABASE_URL` | Dev DB — `sqlite:///data.sqlite` for local SQLite |
| `DATABASE_URL` | Production DB URL |
| `ASPEN_SERVER` | Aspen server hostname |
| `CORS_ORIGINS` | Allowed origins for the API, comma-separated; defaults to `http://localhost:5173` in development and none otherwise |
| `FRONTEND_DIST` | Folder of the built React app (default: `frontend/dist`) |
| `REQUIRE_AUTH` | Refuse API requests without a Windows Authentication user (default: on in production, off otherwise) |
| `LOG_FILE` | Rotating log file for warnings and errors; its folder is created if needed |
| `ASPEN_TIMEOUT` | Seconds before an Aspen query gives up (default: `60`) |
| `ASPEN_SEARCH_MAX_ROWS` | Most rows an Aspen definition search returns (default: `5000`) |
| `ASPEN_RATE_LIMIT` | Aspen searches and trends allowed per user (default: `30 per minute`) |