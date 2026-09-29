from dotenv import load_dotenv
load_dotenv()  # must run before agent.py / tools.py are imported

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import agent
from tools import WAQI_TOKEN

app = FastAPI(title="Lahore Smog Watch Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Welcome to the Lahore Smog Watch Ai Agent"}


@app.get("/health")
def health():
    return {"status": "ok"}


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"


@app.post("/ask")
def ask(req: ChatRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    response = agent.invoke(
        {"messages": [{"role": "user", "content": req.message}]},
        config=config,
    )
    return {"answer": response["messages"][-1].content}


def _parse(s):
    st = s.get("station", {})
    lat, lon = s.get("lat"), s.get("lon")
    geo = st.get("geo") or []
    if (lat is None or lon is None) and len(geo) == 2:
        lat, lon = geo
    try:
        lat, lon = float(lat), float(lon)
    except (TypeError, ValueError):
        return None
    if abs(lat) > 90:  # some feeds send [lon, lat]
        lat, lon = lon, lat
    try:
        aqi = float(s.get("aqi"))
    except (TypeError, ValueError):
        aqi = None  # "-" : top-level AQI offline, PM2.5 may still be live
    return {"uid": s.get("uid"), "name": st.get("name", "Station"),
            "lat": lat, "lon": lon, "aqi": aqi}


@app.get("/stations")
def stations(bounds: str = "31.30,74.10,31.70,74.55"):
    """
    Nearby WAQI monitoring stations for the frontend map.
    bounds format: south,west,north,east
    """
    south, west, north, east = [float(x) for x in bounds.split(",")]
    out, seen, pending, debug = [], set(), [], []
    counts = {"no_geo": 0, "out_of_box": 0, "from_pm25": 0, "offline_in_box": 0}

    def add(items):
        for s in items:
            st = _parse(s)
            if not st:
                counts["no_geo"] += 1
                continue
            if not (south <= st["lat"] <= north and west <= st["lon"] <= east):
                counts["out_of_box"] += 1
                continue
            key = st["uid"] or (round(st["lat"], 4), round(st["lon"], 4))
            if key in seen:
                continue
            seen.add(key)
            if st["aqi"] is None:
                pending.append(st)
            else:
                out.append(st)

    def call(url, params, label):
        try:
            d = requests.get(url, params=params, timeout=15).json()
            data = d.get("data")
            debug.append(f"{label} status={d.get('status')} data={len(data) if isinstance(data, list) else data}")
            if d.get("status") == "ok" and isinstance(data, list):
                add(data)
        except Exception as e:
            debug.append(f"{label} failed: {e}")

    # 1) map bounds (v1, then v2)
    call("https://api.waqi.info/map/bounds/",
         {"latlng": bounds, "token": WAQI_TOKEN}, "bounds")
    call("https://api.waqi.info/v2/map/bounds",
         {"latlng": bounds, "networks": "all", "token": WAQI_TOKEN}, "bounds-v2")

    # 2) keyword search, kept only if inside the box
    if len(out) + len(pending) < 3:
        for kw in ("lahore", "pakistan", "punjab", "LHE"):
            call("https://api.waqi.info/search/",
                 {"keyword": kw, "token": WAQI_TOKEN}, f"search '{kw}'")

    # 3) stations whose top-level AQI is "-": use the live PM2.5 sub-index
    for st in pending[:12]:
        try:
            d = requests.get(f"https://api.waqi.info/feed/@{st['uid']}/",
                             params={"token": WAQI_TOKEN}, timeout=10).json()
            v = d["data"]["iaqi"]["pm25"]["v"]
            st["aqi"] = float(v)
            out.append(st)
            counts["from_pm25"] += 1
        except Exception:
            counts["offline_in_box"] += 1

    debug.append(f"{counts}")
    return {"stations": out, "debug": "; ".join(debug)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)