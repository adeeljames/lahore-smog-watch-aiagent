<div align="center">

# 🌫️ Lahore Smog Watch

**An AI agent that tells Lahore what is in the air right now, and what it means for your health.**

Live AQI · fire hotspots · wind · weather · nearby stations · Punjab EPA advisories

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Agents-1C3C3C?style=flat-square)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Memory-1C3C3C?style=flat-square)](https://www.langchain.com/langgraph)
[![Groq](https://img.shields.io/badge/Groq-gpt--oss--120b-F55036?style=flat-square)](https://groq.com/)
[![Data](https://img.shields.io/badge/Data-WAQI_%C2%B7_NASA_FIRMS_%C2%B7_Open--Meteo-2E7D32?style=flat-square)](#where-the-data-comes-from)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-muhammadadeelai-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/muhammadadeelai/)

</div>

---

## What this is

Lahore is regularly among the most polluted cities in the world, and the worst
of it lands in smog season, October to February. Most apps show a number and a
colour. **Lahore Smog Watch** goes one step further: an LLM agent reads live
station data, satellite fire detections and wind, then answers real questions
in plain language.

> *"Is it safe for my kids to play outside today?"*
> *"Where is the smoke coming from?"*
> *"Will it clear up tomorrow?"*

It also uses the **Punjab Environmental Protection Department's AQI scale**,
not the US EPA one that most apps default to. The two scales use different
category boundaries, so the same reading can carry a different label.

## Features

- **Live AQI gauge** with a needle that sweeps to the current reading, and a page colour that shifts with the air quality
- **Conversational agent** with memory. Ask follow-ups and it remembers the thread
- **Fire hotspot count** near Lahore and the border belt
- **Wind compass and live weather** for Lahore
- **Nearby station map** showing AQI at monitoring stations across the city
- **Forecast charts** that appear automatically when you ask about tomorrow or the coming days
- **Exact health categories** on the Punjab EPA scale

## How it works

```
 Browser (frontend/index.html)
     │
     ├── POST /ask ─────────► FastAPI ──► LangGraph agent (Groq LLM)
     │                                         │
     │                                         ├─ get_aqi              → WAQI
     │                                         ├─ get_fire_hotspots    → NASA FIRMS
     │                                         ├─ get_wind             → Open-Meteo
     │                                         ├─ get_health_advisory  → Punjab EPA scale
     │                                         └─ get_aqi_forecast     → Open-Meteo Air Quality
     │
     ├── GET /stations ─────► FastAPI ──► WAQI map bounds API
     │
     └── Weather & wind ────► Open-Meteo (called directly from the browser)
```

The agent decides which tools to call, in what order, and writes the final
answer. Health categories always come from `get_health_advisory`, so the label
is never invented by the model.

## Where the data comes from

| Data | Source | Notes |
|---|---|---|
| Air quality (AQI, pollutants) | [World Air Quality Index Project](https://waqi.info) | Ground stations inside Lahore |
| Fire hotspots | [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov) | VIIRS satellite detections across Punjab and the border belt |
| Wind and weather | [Open-Meteo](https://open-meteo.com) | Free, no key needed |
| AQI forecast | [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) | Hourly forecast, shown as the daily peak |
| Health categories | [Punjab Environmental Protection Department](https://epd.punjab.gov.pk) | Official provincial scale |

Every reading is public data. Nothing shown is estimated by this project.

## Tech stack

| Layer | Tool |
|---|---|
| LLM | Groq, `openai/gpt-oss-120b` |
| Agent | LangChain `create_agent` + LangGraph `InMemorySaver` |
| Backend | FastAPI |
| Frontend | Plain HTML, CSS and JavaScript in a single file, no build step |

## Project structure

```
lahore-smog-watch/
├── tools.py            # the 5 agent tools
├── agent.py            # agent, system prompt and memory
├── api.py              # FastAPI app: /health, /ask, /stations
├── requirements.txt
├── .env.example        # the 3 keys you need
└── frontend/
    └── index.html      # the web UI
```

## Run it locally

```bash
git clone https://github.com/<your-username>/lahore-smog-watch.git
cd lahore-smog-watch

uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

cp .env.example .env      # add your keys
python api.py             # backend on http://127.0.0.1:8000
```

Then open `frontend/index.html` in your browser.

**Keys needed** (all have free tiers):
[Groq](https://console.groq.com) ·
[WAQI](https://aqicn.org/data-platform/token/) ·
[NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/api/map_key/)

## API

| Method | Route | Description |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}` |
| `POST` | `/ask` | Body: `{"message": "...", "thread_id": "..."}`. Returns `{"answer": "..."}` |
| `GET` | `/stations` | Nearby monitoring stations with coordinates and AQI |

## Disclaimer

Readings are indicative and come from third-party sources that can lag or go
offline. For medical decisions, talk to a doctor.

---

<div align="center">

Made with ❤️ by **[@muhammadadeelai](https://www.linkedin.com/in/muhammadadeelai/)**

[![Connect on LinkedIn](https://img.shields.io/badge/Connect_on-LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/muhammadadeelai/)

</div>
