# Intervals.icu API Reference

Use this reference to make direct API calls via `curl` in the Bash tool. No MCP server needed.

## Authentication

All Intervals.icu API calls use HTTP Basic auth:
- Username: `API_KEY`
- Password: the value of `$INTERVALS_API_KEY`

```bash
curl -s -u "API_KEY:$INTERVALS_API_KEY" "https://intervals.icu/api/v1/..."
```

The athlete ID is in `$INTERVALS_ATHLETE_ID`.

**Always check** that both env vars are set before making calls. If either is missing, tell the athlete to run `/setup`.

Env vars are loaded from the `.env` file in the project root (by the MCP server and by `switchback.sh`). They can also be set in the shell environment, which takes precedence over `.env`.

## Response Filtering

API responses can be large. Use `jq` to extract only the fields you need to avoid blowing up the context window.

### Useful field sets

**Activity (list view):** id, name, type, start_date_local, distance, moving_time, elapsed_time, avg_hr, max_hr, total_elevation_gain, icu_training_load, icu_intensity, icu_efficiency_factor, average_speed, description, pace, icu_average_watts, calories

**Activity (detail view):** all of the above plus icu_intervals, icu_laps, icu_hr_zones, icu_pace_zones, icu_power_zones, icu_groups

**Athlete profile:** id, name, sex, birthday, weight, city, country, timezone, locale, max_hr, resting_hr, lthr, threshold_pace, ftp, run_ftp, weight_kg, sportSettings, hr_zones, pace_zones, power_zones

**Fitness (from wellness):** id (date), ctl, atl, rampRate, ctlLoad, atlLoad — compute TSB as `ctl - atl`

## Endpoints

### Get Athlete Profile

```bash
curl -s -u "API_KEY:$INTERVALS_API_KEY" \
  "https://intervals.icu/api/v1/athlete/$INTERVALS_ATHLETE_ID" \
  | jq '{id, name, sex, birthday, weight, city, country, timezone, locale, max_hr, resting_hr, lthr, threshold_pace, ftp, run_ftp, weight_kg, sportSettings, hr_zones, pace_zones, power_zones}'
```

### Get Events (Planned Workouts)

```bash
curl -s -u "API_KEY:$INTERVALS_API_KEY" \
  "https://intervals.icu/api/v1/athlete/$INTERVALS_ATHLETE_ID/events.json?oldest=YYYY-MM-DD&newest=YYYY-MM-DD"
```

### Get Activities (Completed)

```bash
curl -s -u "API_KEY:$INTERVALS_API_KEY" \
  "https://intervals.icu/api/v1/athlete/$INTERVALS_ATHLETE_ID/activities?oldest=YYYY-MM-DD&newest=YYYY-MM-DD" \
  | jq '[.[] | {id, name, type, start_date_local, distance, moving_time, elapsed_time, avg_hr, max_hr, total_elevation_gain, icu_training_load, icu_intensity, icu_efficiency_factor, average_speed, description, pace, icu_average_watts, calories}]'
```

### Get Single Activity (with intervals)

```bash
curl -s -u "API_KEY:$INTERVALS_API_KEY" \
  "https://intervals.icu/api/v1/activity/ACTIVITY_ID?intervals=true" \
  | jq '{id, name, type, start_date_local, distance, moving_time, elapsed_time, avg_hr, max_hr, total_elevation_gain, icu_training_load, icu_intensity, icu_efficiency_factor, average_speed, description, pace, icu_average_watts, calories, icu_hr_zones, icu_pace_zones, icu_power_zones, icu_intervals: [.icu_intervals[]? | {type, label, distance, moving_time, elapsed_time, average_speed, gap, average_heartrate, max_heartrate, average_cadence, total_elevation_gain, average_gradient, zone, intensity}], icu_groups: [.icu_groups[]? | {id, count, distance, moving_time, average_speed, gap, average_heartrate, average_cadence, total_elevation_gain, zone}]}'
```

This filters intervals to just the fields useful for coaching analysis (pace, HR, cadence, elevation, zone). Raw responses include ~70 fields per interval, most null — always filter.

### Get Activity Streams (time-series)

Second-by-second data. Available stream types: `heartrate`, `watts`, `cadence`, `altitude`, `velocity_smooth`, `distance`, `time`, `latlng`.

```bash
curl -s -u "API_KEY:$INTERVALS_API_KEY" \
  "https://intervals.icu/api/v1/activity/ACTIVITY_ID/streams.json?types=heartrate,velocity_smooth,altitude"
```

Only fetch the stream types you need. This data can be very large.

### Get Wellness

```bash
curl -s -u "API_KEY:$INTERVALS_API_KEY" \
  "https://intervals.icu/api/v1/athlete/$INTERVALS_ATHLETE_ID/wellness.json?oldest=YYYY-MM-DD&newest=YYYY-MM-DD"
```

### Get Fitness (CTL/ATL/TSB)

Fitness data is embedded in the wellness endpoint. Extract the fitness fields and compute TSB:

```bash
curl -s -u "API_KEY:$INTERVALS_API_KEY" \
  "https://intervals.icu/api/v1/athlete/$INTERVALS_ATHLETE_ID/wellness.json?oldest=YYYY-MM-DD&newest=YYYY-MM-DD" \
  | jq '[.[] | {date: .id, ctl, atl, tsb: ((.ctl // 0) - (.atl // 0)), rampRate, ctlLoad, atlLoad}]'
```

### Create Event (Planned Workout)

```bash
curl -s -u "API_KEY:$INTERVALS_API_KEY" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "category": "WORKOUT",
    "start_date_local": "YYYY-MM-DDT08:00:00",
    "name": "Workout Name",
    "description": "Warmup\n- 15m easy\n\nMain Set 3x\n- 8m 88-92%\n- 3m 60%\n\nCooldown\n- 10m easy",
    "type": "Run",
    "moving_time": 3600,
    "distance": 16000
  }' \
  "https://intervals.icu/api/v1/athlete/$INTERVALS_ATHLETE_ID/events"
```

Fields:
- `category`: `"WORKOUT"`, `"NOTE"`, or `"TARGET"`
- `start_date_local`: date with time, e.g. `"2025-04-01T08:00:00"`. Default to `T08:00:00` if only date given.
- `name`: workout name
- `description`: workout text (see Workout Description Syntax in COMPANION.md)
- `type`: e.g. `"Run"`, `"Ride"`, `"Swim"`
- `moving_time`: planned duration in seconds (optional)
- `distance`: planned distance in meters (optional)

### Update Event

```bash
curl -s -u "API_KEY:$INTERVALS_API_KEY" \
  -X PUT \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name", "description": "new description"}' \
  "https://intervals.icu/api/v1/athlete/$INTERVALS_ATHLETE_ID/events/EVENT_ID"
```

Send only the fields you want to change.

### Delete Event

```bash
curl -s -u "API_KEY:$INTERVALS_API_KEY" \
  -X DELETE \
  "https://intervals.icu/api/v1/athlete/$INTERVALS_ATHLETE_ID/events/EVENT_ID"
```

Returns 204 on success.

## Weather (Open-Meteo)

Weather uses the free Open-Meteo API (no auth needed). Use the athlete's lat/lon from `athlete/profile.md`.

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=LAT&longitude=LON&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,wind_gusts_10m,weather_code&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m,weather_code&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,weather_code,sunrise,sunset,uv_index_max&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=TIMEZONE&forecast_days=7"
```

Replace `LAT`, `LON`, and `TIMEZONE` (IANA format, e.g. `America/Los_Angeles`) with values from the athlete's profile. Switch units to metric if the athlete prefers.

## Error Handling

- Check HTTP status codes. Non-2xx means something went wrong.
- Common issues: 401 (bad API key), 404 (wrong athlete ID or activity ID), 429 (rate limited)
- If an API call fails, show the error to the athlete and suggest checking their API key or trying again.

## Tips

- **Parallel calls:** When fetching multiple endpoints (events + wellness + fitness + weather), run them as parallel Bash tool calls for speed.
- **Date math:** Use `date -d "7 days ago" +%Y-%m-%d` for relative dates.
- **Large responses:** Always pipe through `jq` to filter fields. Activity streams especially can be massive.
- **Zones are cached:** The athlete's zones are in `athlete/profile.md` — no need to call the athlete endpoint unless zones are missing or need refreshing.
