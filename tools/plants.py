import json
from pathlib import Path

_PLANTS_FILE = Path(__file__).parent.parent / "data" / "plants.json"


def _load_plants() -> dict:
    with open(_PLANTS_FILE, encoding="utf-8") as f:
        return json.load(f)


def lookup_plant_care(plant_name: str) -> dict:
    """Look up watering, sun, temp tolerances, and care info for a plant."""
    plants = _load_plants()

    # Build a list of candidate keys to try, from most to least specific:
    # original → strip trailing 's' → strip trailing 'es'
    name_lower = plant_name.lower()
    normalized = name_lower.replace(" ", "_").replace("-", "_")
    candidates = [normalized]
    if normalized.endswith("es"):
        candidates.append(normalized[:-2])
    if normalized.endswith("s"):
        candidates.append(normalized[:-1])

    for candidate in candidates:
        if candidate in plants:
            return plants[candidate]

    # Substring match against common_name field (handles plurals in display names too)
    for info in plants.values():
        common = info["common_name"].lower()
        if name_lower in common or common in name_lower:
            return info

    return {
        "error": (
            f"No plant data found for '{plant_name}'. "
            "Try a common name such as 'tomato', 'basil', or 'marigold'."
        )
    }
