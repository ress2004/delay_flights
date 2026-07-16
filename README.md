# Delay Flights

A lookup tool that answers "why is my flight late?" using US DOT / BTS on-time
performance data for 2025 (6.9M+ domestic flights), aggregated in BigQuery.

Pick an origin, destination, airline, and departure time window to see the
odds a flight departs 15+ minutes late, the typical delay length, and a
breakdown of delay causes (late aircraft, carrier, weather, airspace/ATC).

## How it works

1. Flight data is aggregated into route-level stats in BigQuery
   (`flights.route_stats`).
2. `main.py` / `main.ipynb` query that table and export the results to
   `app/data.json`, nested as `data[origin][dest][airline][time_bucket]`.
3. `app/index.html` is a static, dependency-free page that fetches
   `data.json` and renders the lookup UI.

## Running the app

The app is static and only needs a local server (browsers block `fetch` on
`file://`):

```
cd app
python -m http.server
```

Then open http://localhost:8000.

## Regenerating the data

Requires access to the `delay-flights-502519` BigQuery project (or set
`GOOGLE_CLOUD_PROJECT` to your own).

```
pip install -r requirements.txt
python main.py
```

## Data notes

- Delay = departure 15+ minutes behind schedule (US DOT definition).
- Origin/destination/airline/time-bucket combinations with fewer than 100
  flights are excluded.
- Not affiliated with any airline.
