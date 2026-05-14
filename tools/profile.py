import json
from pathlib import Path

_PROFILES_DIR = Path(__file__).parent.parent / "data" / "profiles"


def _safe_profile_path(user_id: str) -> Path | None:
    """Return the resolved profile path, or None if user_id would escape the profiles dir."""
    _PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    path = (_PROFILES_DIR / f"{user_id}.json").resolve()
    if not str(path).startswith(str(_PROFILES_DIR.resolve())):
        return None
    return path


def get_garden_profile(user_id: str) -> dict:
    """Read a user's garden profile (location, plants, and preferences)."""
    path = _safe_profile_path(user_id)
    if path is None:
        return {"error": "Invalid user ID."}
    if not path.exists():
        return {"error": f"No profile found for user '{user_id}'."}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def update_garden_profile(user_id: str, updates: dict) -> dict:
    """Merge updates into a user's garden profile and persist it."""
    path = _safe_profile_path(user_id)
    if path is None:
        return {"error": "Invalid user ID."}
    profile = {}
    if path.exists():
        with open(path, encoding="utf-8") as f:
            profile = json.load(f)
    profile.update(updates)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    return {"status": "updated", "user_id": user_id, "profile": profile}
