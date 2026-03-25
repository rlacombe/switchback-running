import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const API_KEY = process.env.INTERVALS_API_KEY;
const ATHLETE_ID = process.env.INTERVALS_ATHLETE_ID;

if (!API_KEY || !ATHLETE_ID) {
  console.error(
    "Missing INTERVALS_API_KEY or INTERVALS_ATHLETE_ID environment variables"
  );
  process.exit(1);
}

const BASE_URL = "https://intervals.icu/api/v1";
const AUTH_HEADER =
  "Basic " + Buffer.from(`API_KEY:${API_KEY}`).toString("base64");

async function fetchAPI(path: string, options: RequestInit = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      Authorization: AUTH_HEADER,
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

function ok(data: unknown) {
  return {
    content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }],
  };
}

// --- Response filters ---
// Keep only the fields Virgil needs to avoid blowing up the context window.

const ATHLETE_FIELDS = [
  "id", "name", "sex", "birthday", "weight", "city", "country", "timezone",
  "locale", "max_hr", "resting_hr", "lthr", "threshold_pace",
  "ftp", "run_ftp", "weight_kg",
  "sportSettings", "hr_zones", "pace_zones", "power_zones",
];

const ACTIVITY_FIELDS = [
  "id", "name", "type", "start_date_local", "distance", "moving_time",
  "elapsed_time", "avg_hr", "max_hr", "total_elevation_gain",
  "icu_training_load", "icu_intensity", "icu_efficiency_factor",
  "average_speed", "description", "pace", "icu_average_watts",
  "suffer_score", "calories", "source",
];

const ACTIVITY_DETAIL_FIELDS = [
  ...ACTIVITY_FIELDS,
  "icu_intervals", "icu_laps", "icu_hr_zones", "icu_pace_zones",
  "icu_power_zones", "icu_groups",
];

function pick<T extends Record<string, unknown>>(obj: T, fields: string[]): Partial<T> {
  const result: Record<string, unknown> = {};
  for (const f of fields) {
    if (f in obj) result[f] = obj[f];
  }
  return result as Partial<T>;
}

function err(e: unknown) {
  return {
    isError: true as const,
    content: [
      { type: "text" as const, text: String(e instanceof Error ? e.message : e) },
    ],
  };
}

const server = new McpServer({
  name: "intervals-icu",
  version: "1.0.0",
});

// --- GET tools ---

server.tool(
  "get_events",
  "Fetch planned workouts/events from the Intervals.icu calendar for a date range (YYYY-MM-DD).",
  { oldest: z.string(), newest: z.string() },
  async ({ oldest, newest }) => {
    try {
      const data = await fetchAPI(
        `/athlete/${ATHLETE_ID}/events.json?oldest=${oldest}&newest=${newest}`
      );
      return ok(data);
    } catch (e) {
      return err(e);
    }
  }
);

server.tool(
  "get_activities",
  "Fetch completed activities for a date range (YYYY-MM-DD).",
  { oldest: z.string(), newest: z.string() },
  async ({ oldest, newest }) => {
    try {
      const data = await fetchAPI(
        `/athlete/${ATHLETE_ID}/activities?oldest=${oldest}&newest=${newest}`
      );
      const activities = Array.isArray(data)
        ? data.map((a: Record<string, unknown>) => pick(a, ACTIVITY_FIELDS))
        : data;
      return ok(activities);
    } catch (e) {
      return err(e);
    }
  }
);

server.tool(
  "get_activity",
  "Fetch a single activity by ID with interval/lap details.",
  { id: z.string() },
  async ({ id }) => {
    try {
      const data = await fetchAPI(`/activity/${id}?intervals=true`);
      return ok(pick(data as Record<string, unknown>, ACTIVITY_DETAIL_FIELDS));
    } catch (e) {
      return err(e);
    }
  }
);

server.tool(
  "get_wellness",
  "Fetch wellness data (HRV, sleep, weight, fatigue, mood) for a date range (YYYY-MM-DD).",
  { oldest: z.string(), newest: z.string() },
  async ({ oldest, newest }) => {
    try {
      const data = await fetchAPI(
        `/athlete/${ATHLETE_ID}/wellness.json?oldest=${oldest}&newest=${newest}`
      );
      return ok(data);
    } catch (e) {
      return err(e);
    }
  }
);

server.tool(
  "get_fitness",
  "Fetch current fitness metrics (CTL, ATL, TSB) and recent trend.",
  { oldest: z.string().optional(), newest: z.string().optional() },
  async ({ oldest, newest }) => {
    try {
      const o = oldest ?? new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10);
      const n = newest ?? new Date().toISOString().slice(0, 10);
      const data = await fetchAPI(
        `/athlete/${ATHLETE_ID}/wellness.json?oldest=${o}&newest=${n}`
      );
      const rows = Array.isArray(data) ? data : [];
      const FITNESS_FIELDS = ["id", "ctl", "atl", "rampRate", "ctlLoad", "atlLoad"];
      const fitness = rows.map((r: Record<string, unknown>) => {
        const entry: Record<string, unknown> = {};
        for (const f of FITNESS_FIELDS) {
          if (r[f] !== undefined && r[f] !== null) entry[f] = r[f];
        }
        if (entry.ctl !== undefined && entry.atl !== undefined) {
          entry.tsb = Number(entry.ctl) - Number(entry.atl);
        }
        return entry;
      }).filter((e: Record<string, unknown>) => Object.keys(e).length > 1);
      return ok(fitness);
    } catch (e) {
      return err(e);
    }
  }
);

server.tool(
  "get_athlete",
  "Fetch the athlete's profile: HR zones, pace zones, power zones, weight, sport settings.",
  {},
  async () => {
    try {
      const data = await fetchAPI(`/athlete/${ATHLETE_ID}`);
      return ok(pick(data as Record<string, unknown>, ATHLETE_FIELDS));
    } catch (e) {
      return err(e);
    }
  }
);

server.tool(
  "get_activity_streams",
  "Fetch second-by-second time-series data (HR, pace, power, altitude, etc.) for an activity.",
  {
    id: z.string().describe("Activity ID"),
    types: z
      .array(z.string())
      .optional()
      .describe(
        "Stream types to fetch, e.g. heartrate, watts, cadence, altitude, velocity_smooth, distance, time, latlng"
      ),
  },
  async ({ id, types }) => {
    try {
      let path = `/activity/${id}/streams.json`;
      if (types?.length) path += `?types=${types.join(",")}`;
      const data = await fetchAPI(path);
      return ok(data);
    } catch (e) {
      return err(e);
    }
  }
);

// --- Weather ---

server.tool(
  "get_weather",
  "Fetch current conditions and 7-day forecast for a location. Use the athlete's lat/lon from their profile.",
  {
    latitude: z.number().describe("Latitude"),
    longitude: z.number().describe("Longitude"),
    timezone: z.string().optional().describe("IANA timezone, e.g. America/Los_Angeles"),
    temperature_unit: z.enum(["fahrenheit", "celsius"]).optional().default("fahrenheit"),
    wind_speed_unit: z.enum(["mph", "kmh"]).optional().default("mph"),
    precipitation_unit: z.enum(["inch", "mm"]).optional().default("inch"),
  },
  async ({ latitude, longitude, timezone, temperature_unit, wind_speed_unit, precipitation_unit }) => {
    try {
      const tz = timezone ?? "auto";
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}` +
        `&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,wind_gusts_10m,weather_code` +
        `&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m,weather_code` +
        `&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,weather_code,sunrise,sunset,uv_index_max` +
        `&temperature_unit=${temperature_unit}&wind_speed_unit=${wind_speed_unit}&precipitation_unit=${precipitation_unit}` +
        `&timezone=${tz}&forecast_days=7`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Weather API ${res.status}: ${await res.text()}`);
      const data = await res.json();
      return ok(data);
    } catch (e) {
      return err(e);
    }
  }
);

// --- Write tools ---

server.tool(
  "create_event",
  "Create a planned workout or note on the Intervals.icu calendar.",
  {
    category: z.enum(["WORKOUT", "NOTE", "TARGET"]).default("WORKOUT"),
    start_date_local: z.string().describe("Date in YYYY-MM-DD format"),
    name: z.string(),
    description: z.string().optional(),
    type: z.string().optional().describe("e.g. Run, Ride, Swim"),
    moving_time: z.coerce.number().optional().describe("Planned duration in seconds"),
    distance: z.coerce.number().optional().describe("Planned distance in meters"),
    workout_doc: z.any().optional().describe("Structured workout JSON"),
  },
  async (params) => {
    try {
      const body = {
        ...params,
        start_date_local: params.start_date_local.includes("T")
          ? params.start_date_local
          : `${params.start_date_local}T08:00:00`,
      };
      const data = await fetchAPI(`/athlete/${ATHLETE_ID}/events`, {
        method: "POST",
        body: JSON.stringify(body),
      });
      return ok(data);
    } catch (e) {
      return err(e);
    }
  }
);

server.tool(
  "update_event",
  "Update an existing planned workout/event on the Intervals.icu calendar.",
  {
    id: z.coerce.number().describe("Event ID"),
    name: z.string().optional(),
    description: z.string().optional(),
    start_date_local: z.string().optional(),
    category: z.enum(["WORKOUT", "NOTE", "TARGET"]).optional(),
    type: z.string().optional(),
    moving_time: z.coerce.number().optional().describe("Planned duration in seconds"),
    distance: z.coerce.number().optional().describe("Planned distance in meters"),
    workout_doc: z.any().optional(),
  },
  async ({ id, ...rest }) => {
    try {
      const body = rest.start_date_local
        ? {
            ...rest,
            start_date_local: rest.start_date_local.includes("T")
              ? rest.start_date_local
              : `${rest.start_date_local}T08:00:00`,
          }
        : rest;
      const data = await fetchAPI(`/athlete/${ATHLETE_ID}/events/${id}`, {
        method: "PUT",
        body: JSON.stringify(body),
      });
      return ok(data);
    } catch (e) {
      return err(e);
    }
  }
);

server.tool(
  "delete_event",
  "Delete a planned workout/event from the Intervals.icu calendar.",
  { id: z.coerce.number().describe("Event ID") },
  async ({ id }) => {
    try {
      await fetchAPI(`/athlete/${ATHLETE_ID}/events/${id}`, {
        method: "DELETE",
      });
      return ok({ deleted: true, id });
    } catch (e) {
      return err(e);
    }
  }
);

// --- Start ---

const transport = new StdioServerTransport();
await server.connect(transport);
