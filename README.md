# Book the flight that actually leaves on time

**Try it:** https://ress2004.github.io/delay_flights/

A few months ago I sat on the floor of Hanoi airport for 8 hours waiting for a delayed flight, with no idea why it was late. This project is my revenge. I pulled every US domestic flight from 2025 (6.9 million of them, from the US Department of Transportation) into BigQuery and went looking for answers.

## What I found

About 21.7% of US flights left 15+ minutes late in 2025. When a flight runs late, the median delay is around half an hour. The average is 73.6 minutes, but that number is misleading because a small number of catastrophic multi-hour delays drag it up. This is why I report medians in the tool.

The surprising part was the causes. I assumed weather. Weather is 6.4% of delay minutes. The biggest cause, at 39.2%, is "late aircraft": the plane assigned to your flight showed up late from wherever it was before. Add regular airline operational problems (32.4%) and more than 70% of delay minutes are the airline's own machinery, not storms or bad luck.

So I dug into the late aircraft thing, because it sounded circular. Flights are late because the plane was late? Using tail numbers (the ID of the physical aircraft), I reconstructed each plane's day and linked every flight to that same plane's previous flight. The numbers came out steeper than I expected:

| The aircraft's previous flight | Chance this flight departs late |
|---|---|
| First flight of the day | 13.5% |
| Arrived on time | 12.9% |
| Arrived 15-60 min late | 66.3% |
| Arrived 60+ min late | 82.5% |

A plane that lands an hour late is 6.4x more likely to leave late than one that arrived on time. And the delay grows: planes that arrive 60+ minutes late depart, on average, 90 minutes late. Turnaround buffers absorb small delays fine (notice that flights after an on-time arrival are actually slightly safer than the first flights of the morning) and then collapse completely past a threshold.

The practical conclusion is boring: fly in the morning. Delays pile up through the day as late planes infect their next flights, so morning departures fly on planes that haven't inherited anything yet.

## The tool

I turned the route-level stats into a small site. You pick origin, destination, airline, and a time window, and it shows the historical delay odds, the typical delay length, where the delay minutes come from on that route, and whether a different time, airport, or airline would meaningfully improve your odds. It only suggests an alternative when it beats your pick by at least 5 percentage points.

## How it's built

```
raw CSVs -> Cloud Storage -> BigQuery (all transforms in SQL) -> Python export -> static page on GitHub Pages
```

All the analysis is SQL, in the `sql/` folder, numbered in order. A short Python script (`scripts/`) exports pre-computed aggregates to a JSON file, and the site (`app/`) is a single static page that reads it. There's no backend on purpose: 2025 is over, the data won't change, so there's nothing a server would add except hosting costs and ways to break.

Some decisions I'd defend in an interview:

- The raw BTS files load into BigQuery as all-STRING columns, untouched. BTS ships timestamps like `1/1/2025 12:00:00 AM` and a trailing comma on every row, and I learned this the hard way when the first load failed on 100% of rows. Typing happens in the transform layer with PARSE_TIMESTAMP and SAFE_CAST, so the raw layer always matches the source files.
- The cascade analysis partitions by aircraft and calendar day, so each plane's first flight of the day is a natural control group. The tradeoff: overnight rotations that cross midnight don't get linked. I know, and I accepted the leak.
- Flights within a day are ordered by full scheduled departure time, not hour, to avoid tie-breaking bugs when a plane has two flights in the same hour.
- Route stats need at least 100 flights in 2025 to appear in the tool. Below that, the percentages get too noisy to show people.
- BTS only attributes causes for flights arriving 15+ minutes late, so cause percentages describe attributed delay minutes.

## Data

[BTS Reporting Carrier On-Time Performance](https://www.transtats.bts.gov/), all 12 months of 2025, downloaded one month at a time (the site has no yearly download, sorry). Raw CSVs aren't in this repo since they're a few GB; the field list and load settings are documented in `sql/`.

## What's next

Delay deltas in the recommendations ("morning: 19%, that's 23 points better"), and a Tel Aviv version. No free historical delay data exists for TLV, so I'm collecting it myself with a scheduled scraper. Come back in a few months.

---

Built with BigQuery, Python, and Claude as pair-programmer. Every query is in the repo, and I can explain every one of them.
