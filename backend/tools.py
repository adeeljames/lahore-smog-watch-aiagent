import os
import requests
from langchain_core.tools import tool

WAQI_TOKEN = os.environ["WAQI_TOKEN"]
FIRMS_MAP_KEY = os.environ["FIRMS_MAP_KEY"]


@tool
def get_aqi(station: str = "A471607") -> str:
    """Get real-time Air Quality Index (AQI) for a Lahore WAQI monitoring station."""
    url = f"https://api.waqi.info/feed/{station}/?token={WAQI_TOKEN}"
    r = requests.get(url, timeout=10)
    data = r.json()

    if data.get("status") != "ok":
        return "Could not fetch AQI data right now."

    d = data["data"]
    aqi = d.get("aqi")
    if aqi in ("-", None):
        pm25_index = d.get("iaqi", {}).get("pm25", {}).get("v")
        aqi = pm25_index if pm25_index is not None else None
    if aqi is None:
        return "AQI unavailable from this station right now."

    city = d.get("city", {}).get("name", "Lahore")
    pollutant = d.get("dominentpol", "unknown")
    return f"Station: {city} | AQI: {aqi} | Dominant pollutant: {pollutant}"


@tool
def get_fire_hotspots(days: int = 1) -> str:
    """Get the number of active fire hotspots near Lahore/border region."""
    bbox = "73.5,30.5,75.5,32.5"
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{FIRMS_MAP_KEY}/VIIRS_SNPP_NRT/{bbox}/{days}"
    r = requests.get(url, timeout=15)
    lines = [line for line in r.text.strip().split("\n") if line]
    count = max(len(lines) - 1, 0)
    return f"{count} active fire hotspots detected near Lahore/border in the last {days} day(s)."


@tool
def get_wind(lat: float = 31.5497, lon: float = 74.3436) -> str:
    """Get current wind speed and direction near Lahore."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=wind_speed_10m,wind_direction_10m"
    r = requests.get(url, timeout=10)
    current = r.json().get("current", {})
    return f"Wind speed: {current.get('wind_speed_10m')} km/h | Direction: {current.get('wind_direction_10m')}\u00b0"


@tool
def get_health_advisory(aqi: int) -> str:
    """Return AQI category and health advisory using Punjab EPA's official scale."""
    breakpoints = [
        (50, "Good", "Air quality is satisfactory. Little or no health risk."),
        (100, "Satisfactory", "Air quality is acceptable. Minimal risk for the general public."),
        (150, "Moderate", "Sensitive individuals should consider limiting prolonged outdoor exertion."),
        (200, "Unhealthy for Sensitive People", "Sensitive groups should limit prolonged outdoor exertion."),
        (300, "Unhealthy", "Everyone may begin to experience health effects."),
        (400, "Very Unhealthy", "Health alert: avoid outdoor exertion."),
        (500, "Hazardous", "Health emergency. Avoid all outdoor exertion."),
    ]
    for limit, category, advisory in breakpoints:
        if aqi <= limit:
            return f"AQI {aqi} = {category} (Punjab EPA scale). {advisory}"
    return f"AQI {aqi} = Hazardous (Punjab EPA scale, beyond 500)."


@tool
def get_aqi_forecast(lat: float = 31.5497, lon: float = 74.3436, days: int = 2) -> str:
    """Get FORECASTED air quality for the next N days. Use only for future questions."""
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly=us_aqi&forecast_days={days}"
    r = requests.get(url, timeout=10)
    hourly = r.json().get("hourly", {})
    times, aqi_values = hourly.get("time", []), hourly.get("us_aqi", [])
    if not aqi_values:
        return "Forecast data unavailable right now."

    daily_max = {}
    for t, v in zip(times, aqi_values):
        day = t.split("T")[0]
        if v is not None:
            daily_max[day] = max(daily_max.get(day, 0), v)

    summary = ", ".join(f"{day}: peak AQI {aqi}" for day, aqi in daily_max.items())
    return f"AQI forecast \u2014 {summary}"
