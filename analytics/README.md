# VEYTRA analytics (Member 5)

Traffic density from camera sightings. This folder does **not** include detection, tracking, verification, GIS layers, or a UI.

Input is the controlled sample CSV. PostgreSQL/PostGIS is not used yet.

## Layout

```
analytics/
├── config.py          # 5min / 15min / 1h windows
├── io.py              # load sample CSV
├── density.py         # density calculations
├── data/
│   └── sample_vehicle_events.csv
├── tests/
│   └── test_density.py
└── README.md
```

## Sample input

Each row in `data/sample_vehicle_events.csv` is one camera sighting:

`event_id`, `vehicle_id`, `plate_number`, `camera_id`, `timestamp`, `latitude`, `longitude`, `direction`, `road_segment_id`, `road_name`, `speed_kmh`, `trajectory_id`

Density uses `vehicle_id`, `camera_id`, `road_segment_id`, `road_name`, and `timestamp`.

## Density metrics

- **unique_vehicles**: distinct `vehicle_id` values in the group
- **sightings**: row count in the group

A vehicle seen twice at the same camera in the same window counts as 1 unique vehicle and 2 sightings.

Time windows are half-open `[start, end)` and follow the timezone on the event timestamps (sample data is IST, `+05:30`):

| `--window` | Bin size |
|---|---|
| `5min` | 5 minutes |
| `15min` | 15 minutes |
| `1h` | 1 hour |

## Install

From the repository root:

```bash
pip install pandas numpy pytest
```

## Run

```bash
python -m analytics.density --window 15min
```

Other windows:

```bash
python -m analytics.density --window 5min
python -m analytics.density --window 1h
```

Optional custom CSV:

```bash
python -m analytics.density --window 15min --csv path/to/events.csv
```

Output is JSON with keys `window`, `by_camera`, `by_segment`, `by_time`, `by_camera_time`, `by_segment_time`.

## Test

```bash
pytest analytics/tests/test_density.py -q
```
