import os
import requests
from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("WEATHER_API_KEY")
_BASE = "https://api.openweathermap.org/data/2.5"


def _owm_location(location: str) -> str:
    """Normalise a location string for OWM's q parameter.

    OWM accepts "City" or "City,CountryCode" but not "City, ST" (US state
    abbreviations with a space).  Strip anything after the first comma so
    "Denver, CO" becomes "Denver" and "London,UK" stays "London,UK".
    """
    parts = [p.strip() for p in location.split(",", 1)]
    if len(parts) == 2 and len(parts[1]) <= 3:
        # Looks like a state/country code — drop it, OWM geocodes by city name
        return parts[0]
    return location


def get_current_weather(location: str) -> dict:
    """Get current weather for a location — temp, humidity, rainfall, wind, UV index."""
    resp = requests.get(
        f"{_BASE}/weather",
        params={"q": _owm_location(location), "appid": _API_KEY, "units": "imperial"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    lat, lon = data["coord"]["lat"], data["coord"]["lon"]

    # UV index requires a separate call using lat/lon
    uv_resp = requests.get(
        f"{_BASE}/uvi",
        params={"lat": lat, "lon": lon, "appid": _API_KEY},
        timeout=10,
    )
    uv_index = uv_resp.json().get("value") if uv_resp.ok else None

    return {
        "location": data["name"],
        "temp_f": data["main"]["temp"],
        "feels_like_f": data["main"]["feels_like"],
        "humidity_pct": data["main"]["humidity"],
        "rainfall_in_last_1h": data.get("rain", {}).get("1h", 0),
        "wind_mph": data["wind"]["speed"],
        "description": data["weather"][0]["description"],
        "uv_index": uv_index,
    }


def get_forecast(location: str, days: int = 5) -> dict:
    """Get a multi-day forecast with rain probability and temp ranges (max 5 days on free tier)."""
    days = max(1, min(days, 5))
    resp = requests.get(
        f"{_BASE}/forecast",
        params={"q": _owm_location(location), "appid": _API_KEY, "units": "imperial"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    # Aggregate 3-hour intervals into daily summaries
    daily: dict[str, dict] = {}
    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        if date not in daily:
            daily[date] = {"temps": [], "pop": [], "desc": []}
        daily[date]["temps"].append(item["main"]["temp"])
        daily[date]["pop"].append(item.get("pop", 0))
        daily[date]["desc"].append(item["weather"][0]["description"])

    forecast = []
    for date, vals in list(daily.items())[:days]:
        most_common_desc = max(set(vals["desc"]), key=vals["desc"].count)
        forecast.append({
            "date": date,
            "temp_high_f": round(max(vals["temps"]), 1),
            "temp_low_f": round(min(vals["temps"]), 1),
            "rain_probability_pct": round(max(vals["pop"]) * 100),
            "description": most_common_desc,
        })

    return {
        "location": data["city"]["name"],
        "days_requested": days,
        "forecast": forecast,
    }
