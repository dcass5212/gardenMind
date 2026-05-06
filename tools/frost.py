# Hardcoded average frost dates for common US cities (USDA historical data)
_CITY_FROST_DATA = {
    # Northeast
    "boston": {"last_spring_frost": "Apr 8", "first_fall_frost": "Oct 27"},
    "new york": {"last_spring_frost": "Apr 1", "first_fall_frost": "Nov 11"},
    "new york city": {"last_spring_frost": "Apr 1", "first_fall_frost": "Nov 11"},
    "nyc": {"last_spring_frost": "Apr 1", "first_fall_frost": "Nov 11"},
    "philadelphia": {"last_spring_frost": "Mar 28", "first_fall_frost": "Nov 17"},
    "baltimore": {"last_spring_frost": "Mar 26", "first_fall_frost": "Nov 19"},
    "washington": {"last_spring_frost": "Mar 25", "first_fall_frost": "Nov 15"},
    "washington dc": {"last_spring_frost": "Mar 25", "first_fall_frost": "Nov 15"},
    "buffalo": {"last_spring_frost": "Apr 30", "first_fall_frost": "Oct 15"},
    "portland": {"last_spring_frost": "Apr 15", "first_fall_frost": "Oct 15"},
    "portland me": {"last_spring_frost": "Apr 29", "first_fall_frost": "Oct 15"},
    "burlington": {"last_spring_frost": "May 3", "first_fall_frost": "Oct 1"},
    "albany": {"last_spring_frost": "Apr 27", "first_fall_frost": "Oct 7"},
    "pittsburgh": {"last_spring_frost": "Apr 20", "first_fall_frost": "Oct 23"},
    # Southeast
    "atlanta": {"last_spring_frost": "Mar 13", "first_fall_frost": "Nov 19"},
    "charlotte": {"last_spring_frost": "Mar 21", "first_fall_frost": "Nov 15"},
    "raleigh": {"last_spring_frost": "Mar 24", "first_fall_frost": "Nov 15"},
    "nashville": {"last_spring_frost": "Mar 28", "first_fall_frost": "Nov 7"},
    "memphis": {"last_spring_frost": "Mar 16", "first_fall_frost": "Nov 13"},
    "louisville": {"last_spring_frost": "Apr 1", "first_fall_frost": "Nov 1"},
    "richmond": {"last_spring_frost": "Mar 30", "first_fall_frost": "Nov 3"},
    "miami": {"last_spring_frost": "N/A (frost-free)", "first_fall_frost": "N/A (frost-free)"},
    "tampa": {"last_spring_frost": "Jan 28", "first_fall_frost": "Dec 26"},
    "orlando": {"last_spring_frost": "Feb 6", "first_fall_frost": "Dec 17"},
    "jacksonville": {"last_spring_frost": "Feb 13", "first_fall_frost": "Dec 10"},
    "new orleans": {"last_spring_frost": "Feb 13", "first_fall_frost": "Dec 10"},
    # Midwest
    "chicago": {"last_spring_frost": "Apr 19", "first_fall_frost": "Oct 28"},
    "minneapolis": {"last_spring_frost": "Apr 30", "first_fall_frost": "Oct 13"},
    "detroit": {"last_spring_frost": "Apr 24", "first_fall_frost": "Oct 22"},
    "columbus": {"last_spring_frost": "Apr 17", "first_fall_frost": "Oct 26"},
    "indianapolis": {"last_spring_frost": "Apr 17", "first_fall_frost": "Oct 27"},
    "st. louis": {"last_spring_frost": "Apr 2", "first_fall_frost": "Nov 7"},
    "st louis": {"last_spring_frost": "Apr 2", "first_fall_frost": "Nov 7"},
    "kansas city": {"last_spring_frost": "Apr 1", "first_fall_frost": "Nov 1"},
    "milwaukee": {"last_spring_frost": "Apr 27", "first_fall_frost": "Oct 19"},
    "cincinnati": {"last_spring_frost": "Apr 15", "first_fall_frost": "Oct 20"},
    "cleveland": {"last_spring_frost": "Apr 22", "first_fall_frost": "Nov 2"},
    "omaha": {"last_spring_frost": "Apr 14", "first_fall_frost": "Oct 20"},
    "des moines": {"last_spring_frost": "Apr 20", "first_fall_frost": "Oct 19"},
    # South / Texas
    "houston": {"last_spring_frost": "Feb 4", "first_fall_frost": "Dec 11"},
    "dallas": {"last_spring_frost": "Mar 3", "first_fall_frost": "Nov 17"},
    "san antonio": {"last_spring_frost": "Feb 24", "first_fall_frost": "Nov 24"},
    "austin": {"last_spring_frost": "Feb 20", "first_fall_frost": "Dec 1"},
    "oklahoma city": {"last_spring_frost": "Mar 28", "first_fall_frost": "Nov 7"},
    "little rock": {"last_spring_frost": "Mar 16", "first_fall_frost": "Nov 15"},
    # Mountain / Southwest
    "denver": {"last_spring_frost": "May 3", "first_fall_frost": "Oct 7"},
    "salt lake city": {"last_spring_frost": "Apr 12", "first_fall_frost": "Nov 1"},
    "albuquerque": {"last_spring_frost": "Apr 15", "first_fall_frost": "Oct 29"},
    "phoenix": {"last_spring_frost": "Feb 5", "first_fall_frost": "Dec 15"},
    "tucson": {"last_spring_frost": "Feb 28", "first_fall_frost": "Dec 1"},
    "boise": {"last_spring_frost": "May 8", "first_fall_frost": "Oct 9"},
    "billings": {"last_spring_frost": "May 15", "first_fall_frost": "Sep 24"},
    "cheyenne": {"last_spring_frost": "May 20", "first_fall_frost": "Sep 27"},
    # Pacific Northwest
    "seattle": {"last_spring_frost": "Mar 24", "first_fall_frost": "Nov 11"},
    "portland or": {"last_spring_frost": "Mar 18", "first_fall_frost": "Nov 21"},
    "spokane": {"last_spring_frost": "May 4", "first_fall_frost": "Oct 5"},
    # California
    "los angeles": {"last_spring_frost": "Jan 22", "first_fall_frost": "Dec 15"},
    "san francisco": {"last_spring_frost": "Feb 5", "first_fall_frost": "Dec 20"},
    "san diego": {"last_spring_frost": "N/A (frost-free)", "first_fall_frost": "N/A (frost-free)"},
    "sacramento": {"last_spring_frost": "Feb 17", "first_fall_frost": "Dec 1"},
    "fresno": {"last_spring_frost": "Feb 16", "first_fall_frost": "Dec 1"},
    # Alaska / Hawaii
    "anchorage": {"last_spring_frost": "May 28", "first_fall_frost": "Sep 16"},
    "honolulu": {"last_spring_frost": "N/A (frost-free)", "first_fall_frost": "N/A (frost-free)"},
}


def get_frost_dates(location: str) -> dict:
    """Return average last spring frost and first fall frost date for a US city."""
    key = location.lower().strip()

    if key in _CITY_FROST_DATA:
        return {"location": location.title(), **_CITY_FROST_DATA[key]}

    # Partial match — city name contained in key or vice versa
    for city, dates in _CITY_FROST_DATA.items():
        if key in city or city in key:
            return {"location": city.title(), **dates}

    return {
        "error": (
            f"No frost data found for '{location}'. "
            "Try a major US city name (e.g., 'Denver', 'Atlanta', 'Seattle')."
        )
    }
