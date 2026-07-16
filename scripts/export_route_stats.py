import json
import math

from google.cloud import bigquery

client = bigquery.Client(project="delay-flights-502519")  # or set GOOGLE_CLOUD_PROJECT env var

df = client.query("SELECT * FROM flights.route_stats").to_dataframe()


def clean_float(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return float(value)


# Nest for O(1) lookup in the app: data[origin][dest][airline][time_bucket] -> stats
data = {}
for row in df.itertuples():
    (data.setdefault(row.origin, {})
         .setdefault(row.dest, {})
         .setdefault(row.airline, {}))[row.time_bucket] = {
        "flights": int(row.flights),
        "pct_delayed": float(row.pct_delayed),
        "median_delay": clean_float(row.median_delay_when_late),
        "causes": {
            "late_aircraft": clean_float(row.pct_cause_late_aircraft),
            "carrier": clean_float(row.pct_cause_carrier),
            "weather": clean_float(row.pct_cause_weather),
            "nas": clean_float(row.pct_cause_nas),
        },
    }

with open("docs/data.json", "w") as f:
    json.dump(data, f, allow_nan=False)

print(f"{len(df)} rows -> docs/data.json")
