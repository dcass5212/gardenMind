import json
from pathlib import Path

_PROFILES_DIR = Path(__file__).parent.parent / "data" / "profiles"


def get_garden_profile(user_id: str) -> dict:
    """Read a user's garden profile (location, plants, and preferences)."""
    path = _PROFILES_DIR / f"{user_id}.json"
    if not path.exists():
        return {"error": f"No profile found for user '{user_id}'."}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def update_garden_profile(user_id: str, updates: dict) -> dict:
    """Merge updates into a user's garden profile and persist it."""
    _PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    path = _PROFILES_DIR / f"{user_id}.json"
    profile = {}
    if path.exists():
        with open(path, encoding="utf-8") as f:
            profile = json.load(f)
    profile.update(updates)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    return {"status": "updated", "user_id": user_id, "profile": profile}
