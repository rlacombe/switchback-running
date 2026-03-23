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
      return ok(data);
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
      return ok(data);
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
      let path = `/athlete/${ATHLETE_ID}/fitness`;
      const params: string[] = [];
      if (oldest) params.push(`oldest=${oldest}`);
      if (newest) params.push(`newest=${newest}`);
      if (params.length) path += `?${params.join("&")}`;
      const data = await fetchAPI(path);
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
