#!/usr/bin/env node
// Switchback MCP Server — zero dependencies
// Implements MCP protocol over stdio using only Node.js built-ins.

import { createInterface } from "readline";

const API_KEY = process.env.INTERVALS_API_KEY;
const ATHLETE_ID = process.env.INTERVALS_ATHLETE_ID;
if (!API_KEY || !ATHLETE_ID) { process.stderr.write("Missing INTERVALS_API_KEY or INTERVALS_ATHLETE_ID\n"); process.exit(1); }

const BASE = "https://intervals.icu/api/v1";
const AUTH = "Basic " + Buffer.from(`API_KEY:${API_KEY}`).toString("base64");

// --- API helpers ---

async function api(path, opts = {}) {
  const r = await fetch(`${BASE}${path}`, { ...opts, headers: { Authorization: AUTH, "Content-Type": "application/json", ...opts.headers } });
  if (!r.ok) throw new Error(`API ${r.status}: ${await r.text()}`);
  return r.status === 204 ? null : r.json();
}

function pick(obj, fields) {
  const r = {};
  for (const f of fields) if (obj[f] !== null && obj[f] !== undefined) r[f] = obj[f];
  return r;
}

// --- Field filters ---

const ATHLETE_F = ["id","name","sex","birthday","weight","city","country","timezone","locale","max_hr","resting_hr","lthr","threshold_pace","ftp","run_ftp","weight_kg","sportSettings","hr_zones","pace_zones","power_zones"];
const ACTIVITY_F = ["id","name","type","start_date_local","updated","distance","moving_time","elapsed_time","avg_hr","max_hr","total_elevation_gain","icu_training_load","icu_intensity","icu_efficiency_factor","average_speed","description","pace","icu_average_watts","suffer_score","calories","source"];
const INTERVAL_F = ["type","label","distance","moving_time","elapsed_time","average_speed","gap","average_heartrate","max_heartrate","average_cadence","total_elevation_gain","average_gradient","zone","intensity"];
const GROUP_F = ["id","count","distance","moving_time","average_speed","gap","average_heartrate","average_cadence","total_elevation_gain","zone"];

// --- Tool definitions ---

const TOOLS = [
  { name: "get_athlete", description: "Fetch athlete profile: HR/pace/power zones, weight, sport settings.",
    inputSchema: { type: "object", properties: {} },
    async handler() { return pick(await api(`/athlete/${ATHLETE_ID}`), ATHLETE_F); }},

  { name: "get_events", description: "Fetch planned workouts for a date range (YYYY-MM-DD).",
    inputSchema: { type: "object", properties: { oldest: { type: "string" }, newest: { type: "string" } }, required: ["oldest", "newest"] },
    async handler({ oldest, newest }) { return api(`/athlete/${ATHLETE_ID}/events.json?oldest=${oldest}&newest=${newest}`); }},

  { name: "get_activities", description: "Fetch completed activities for a date range (YYYY-MM-DD).",
    inputSchema: { type: "object", properties: { oldest: { type: "string" }, newest: { type: "string" } }, required: ["oldest", "newest"] },
    async handler({ oldest, newest }) {
      const d = await api(`/athlete/${ATHLETE_ID}/activities?oldest=${oldest}&newest=${newest}`);
      return Array.isArray(d) ? d.map(a => pick(a, ACTIVITY_F)) : d;
    }},

  { name: "get_activity", description: "Fetch a single activity by ID with filtered interval details.",
    inputSchema: { type: "object", properties: { id: { type: "string" } }, required: ["id"] },
    async handler({ id }) {
      const raw = await api(`/activity/${id}?intervals=true`);
      const a = pick(raw, ACTIVITY_F);
      if (Array.isArray(raw.icu_intervals)) a.icu_intervals = raw.icu_intervals.map(i => pick(i, INTERVAL_F));
      if (Array.isArray(raw.icu_groups)) a.icu_groups = raw.icu_groups.map(g => pick(g, GROUP_F));
      for (const f of ["icu_hr_zones", "icu_pace_zones", "icu_power_zones"]) if (raw[f]) a[f] = raw[f];
      return a;
    }},

  { name: "get_activity_streams", description: "Fetch second-by-second time-series data for an activity.",
    inputSchema: { type: "object", properties: { id: { type: "string" }, types: { type: "array", items: { type: "string" }, description: "e.g. heartrate, watts, cadence, altitude, velocity_smooth" } }, required: ["id"] },
    async handler({ id, types }) {
      const path = types?.length ? `/activity/${id}/streams.json?types=${types.join(",")}` : `/activity/${id}/streams.json`;
      return api(path);
    }},

  { name: "get_wellness", description: "Fetch wellness data (HRV, sleep, weight, fatigue, mood) for a date range (YYYY-MM-DD).",
    inputSchema: { type: "object", properties: { oldest: { type: "string" }, newest: { type: "string" } }, required: ["oldest", "newest"] },
    async handler({ oldest, newest }) { return api(`/athlete/${ATHLETE_ID}/wellness.json?oldest=${oldest}&newest=${newest}`); }},

  { name: "get_fitness", description: "Fetch fitness metrics (CTL, ATL, TSB) and recent trend.",
    inputSchema: { type: "object", properties: { oldest: { type: "string" }, newest: { type: "string" } } },
    async handler({ oldest, newest }) {
      const o = oldest || new Date(Date.now() - 7 * 864e5).toISOString().slice(0, 10);
      const n = newest || new Date().toISOString().slice(0, 10);
      const rows = await api(`/athlete/${ATHLETE_ID}/wellness.json?oldest=${o}&newest=${n}`);
      const FF = ["id", "ctl", "atl", "rampRate", "ctlLoad", "atlLoad"];
      return (Array.isArray(rows) ? rows : []).map(r => {
        const e = pick(r, FF);
        if (e.ctl != null && e.atl != null) e.tsb = e.ctl - e.atl;
        return e;
      }).filter(e => Object.keys(e).length > 1);
    }},

  { name: "get_weather", description: "Fetch current conditions and 7-day forecast. Use athlete's lat/lon from profile.",
    inputSchema: { type: "object", properties: {
      latitude: { type: "number" }, longitude: { type: "number" },
      timezone: { type: "string" },
      temperature_unit: { type: "string", enum: ["fahrenheit", "celsius"] },
      wind_speed_unit: { type: "string", enum: ["mph", "kmh"] },
      precipitation_unit: { type: "string", enum: ["inch", "mm"] }
    }, required: ["latitude", "longitude"] },
    async handler({ latitude, longitude, timezone = "auto", temperature_unit = "fahrenheit", wind_speed_unit = "mph", precipitation_unit = "inch" }) {
      const u = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,wind_gusts_10m,weather_code&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m,weather_code&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,weather_code,sunrise,sunset,uv_index_max&temperature_unit=${temperature_unit}&wind_speed_unit=${wind_speed_unit}&precipitation_unit=${precipitation_unit}&timezone=${timezone}&forecast_days=7`;
      const r = await fetch(u);
      if (!r.ok) throw new Error(`Weather ${r.status}`);
      return r.json();
    }},

  { name: "create_event", description: "Create a planned workout or note on the calendar.",
    inputSchema: { type: "object", properties: {
      category: { type: "string", enum: ["WORKOUT", "NOTE", "TARGET"] },
      start_date_local: { type: "string", description: "YYYY-MM-DD" },
      name: { type: "string" }, description: { type: "string" },
      type: { type: "string", description: "e.g. Run, Ride, Swim" },
      moving_time: { type: "number", description: "seconds" },
      distance: { type: "number", description: "meters" }
    }, required: ["start_date_local", "name"] },
    async handler(p) {
      const body = { ...p, category: p.category || "WORKOUT", start_date_local: p.start_date_local.includes("T") ? p.start_date_local : `${p.start_date_local}T08:00:00` };
      return api(`/athlete/${ATHLETE_ID}/events`, { method: "POST", body: JSON.stringify(body) });
    }},

  { name: "update_event", description: "Update a planned workout/event.",
    inputSchema: { type: "object", properties: {
      id: { type: "number", description: "Event ID" },
      name: { type: "string" }, description: { type: "string" },
      start_date_local: { type: "string" }, category: { type: "string" },
      type: { type: "string" }, moving_time: { type: "number" }, distance: { type: "number" }
    }, required: ["id"] },
    async handler({ id, ...rest }) {
      if (rest.start_date_local && !rest.start_date_local.includes("T")) rest.start_date_local += "T08:00:00";
      return api(`/athlete/${ATHLETE_ID}/events/${id}`, { method: "PUT", body: JSON.stringify(rest) });
    }},

  { name: "delete_event", description: "Delete a planned workout/event.",
    inputSchema: { type: "object", properties: { id: { type: "number", description: "Event ID" } }, required: ["id"] },
    async handler({ id }) { await api(`/athlete/${ATHLETE_ID}/events/${id}`, { method: "DELETE" }); return { deleted: true, id }; }},
];

// --- MCP Protocol (JSON-RPC over stdio) ---

function send(msg) { process.stdout.write(JSON.stringify(msg) + "\n"); }

function handleRequest(req) {
  const { id, method, params } = req;
  if (method === "initialize") return send({ jsonrpc: "2.0", id, result: { protocolVersion: "2024-11-05", capabilities: { tools: {} }, serverInfo: { name: "intervals-icu", version: "3.0.0" } } });
  if (method === "notifications/initialized") return;
  if (method === "tools/list") return send({ jsonrpc: "2.0", id, result: { tools: TOOLS.map(t => ({ name: t.name, description: t.description, inputSchema: t.inputSchema })) } });
  if (method === "tools/call") {
    const tool = TOOLS.find(t => t.name === params.name);
    if (!tool) return send({ jsonrpc: "2.0", id, result: { isError: true, content: [{ type: "text", text: `Unknown tool: ${params.name}` }] } });
    tool.handler(params.arguments || {})
      .then(data => send({ jsonrpc: "2.0", id, result: { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] } }))
      .catch(e => send({ jsonrpc: "2.0", id, result: { isError: true, content: [{ type: "text", text: String(e.message || e) }] } }));
    return;
  }
  if (method?.startsWith("notifications/")) return;
  send({ jsonrpc: "2.0", id, error: { code: -32601, message: `Unknown method: ${method}` } });
}

const rl = createInterface({ input: process.stdin });
rl.on("line", line => { try { handleRequest(JSON.parse(line)); } catch {} });
