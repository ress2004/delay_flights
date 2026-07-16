"""Verify docs/airports.json has an entry for every airport code in docs/data.json.

Run: python scripts/check_airports.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "docs" / "data.json"
AIRPORTS_PATH = ROOT / "docs" / "airports.json"


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    airports = json.loads(AIRPORTS_PATH.read_text(encoding="utf-8"))

    codes = set(data.keys())
    for origin in data:
        codes |= set(data[origin].keys())

    missing = sorted(c for c in codes if c not in airports)
    null_entries = sorted(
        c for c in codes
        if c in airports and (airports[c].get("city") is None or airports[c].get("name") is None)
    )
    unused = sorted(set(airports.keys()) - codes)

    print(f"Codes referenced in data.json: {len(codes)}")
    print(f"Codes missing from airports.json: {len(missing)}")
    if missing:
        print(f"  {missing}")
    print(f"Codes present but with null city/name: {len(null_entries)}")
    if null_entries:
        print(f"  {null_entries}")
    print(f"Entries in airports.json not referenced by data.json: {len(unused)}")
    if unused:
        print(f"  {unused}")

    if missing:
        raise SystemExit(1)
    print("OK: every code in data.json has an airports.json entry.")


if __name__ == "__main__":
    main()
