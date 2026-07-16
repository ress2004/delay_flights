import json
from google.cloud import bigquery

client = bigquery.Client(project="delay-flights-502519")

df = client.query("SELECT * FROM flights.route_stats").to_dataframe()
print(len(df))
print(df.head())