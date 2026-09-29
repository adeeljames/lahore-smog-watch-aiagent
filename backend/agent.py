from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from tools import get_aqi, get_fire_hotspots, get_wind, get_health_advisory, get_aqi_forecast

tools = [get_aqi, get_fire_hotspots, get_wind, get_health_advisory, get_aqi_forecast]

agent = create_agent(
    model="groq:openai/gpt-oss-120b",
    tools=tools,
    system_prompt=(
        "You are Lahore Smog Watch, an assistant that explains Lahore's air quality "
        "using live AQI, fire hotspot, and wind data. Always call get_aqi first for "
        "current conditions. Once you have a numeric AQI, always call get_health_advisory "
        "and state its EXACT category name. Use get_aqi_forecast only for future questions. "
        "Keep answers short, clear, and specific."
    ),
    checkpointer=InMemorySaver(),
)
