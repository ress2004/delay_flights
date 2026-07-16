# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A lookup tool answering "why is my flight late?" using US DOT/BTS on-time
performance data for 2025 (6.9M+ US domestic flights). It has two halves:

1. **Data export** (`scripts/main.py`, `scripts/main.ipynb`) — queries a
   pre-aggregated BigQuery table (`flights.route_stats` in project
   `delay-flights-502519`) and writes the results to `docs/data.json`.
2. **Static frontend** (`docs/index.html`) — a single dependency-free HTML
   file that fetches `data.json` and renders a departure-board-style UI for
   route/airline/time-window delay risk. `docs/` (not `app/`) is deliberate:
   it's the folder name GitHub Pages can serve directly from `main` with no
   Actions workflow.

There is no build step, backend server, or test suite — the app is static
HTML/CSS/JS, and the data pipeline is a short Python script.

## Commands

Install export-script dependencies:
```
pip install -r requirements.txt
```

Regenerate `docs/data.json` from BigQuery (requires GCP credentials with
access to `delay-flights-502519`, or set `GOOGLE_CLOUD_PROJECT` to a project
with an equivalent `flights.route_stats` table):
```
python scripts/main.py
```

Serve the frontend locally (plain `file://` won't work — `fetch('data.json')`
requires an HTTP origin, and the server's working directory must be `docs/`
since the fetch path is relative):
```
cd docs
python -m http.server
```

## Architecture notes

- **`scripts/main.py` is currently just a query/print smoke test**, not the
  actual exporter. The real export logic — nesting BigQuery rows into the
  JSON shape the frontend expects — lives commented-out inside
  `scripts/main.ipynb` (intended path: `scripts/export_route_stats.py`, not
  yet extracted). When asked to regenerate or modify the export pipeline,
  look there first rather than assuming `main.py` is authoritative.
- **`data.json` shape**: `data[origin][dest][airline][time_bucket] -> stats`,
  where `time_bucket` is one of `morning` (5–11), `afternoon` (12–16),
  `evening` (17–20), `night` (21–4). Each stats object has `flights`,
  `pct_delayed`, `median_delay` (nullable), and `causes` (`late_aircraft`,
  `carrier`, `weather`, `nas` — all optional/nullable percentages that may
  not sum to 100 or may be entirely absent for low-volume combinations).
  `docs/index.html`'s JS (`render()`, `findAlternative()`, etc.) depends on
  this exact nesting and key set.
- **Delay definition**: departure 15+ minutes behind schedule (US DOT
  standard). Combinations with fewer than 100 flights are excluded from the
  dataset upstream in BigQuery.
- **Frontend is entirely self-contained**: no framework, no bundler, all
  logic inline in `docs/index.html`'s `<script>` block. Airline code→name
  mapping (`AIRLINES`) and time-bucket labels (`BUCKET_NAMES`) are hardcoded
  there and must be kept in sync with whatever airline/bucket values appear
  in `data.json`.
