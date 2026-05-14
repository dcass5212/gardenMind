import json
from pathlib import Path

_PLANTS_FILE = Path(__file__).parent.parent / "data" / "plants.json"
_INDEX_DIR   = Path(__file__).parent.parent / "data" / "plant_index"
_MODEL_NAME  = "all-MiniLM-L6-v2"
_COLLECTION  = "plants"
_SIM_THRESHOLD = 0.70  # cosine distance; below this we consider it a hit

# Lazy-loaded singletons — initialised on first call, None if unavailable
_collection = None
_plants_json: dict | None = None
_vector_ready: bool | None = None  # None = not yet checked


def _load_json() -> dict:
    global _plants_json
    if _plants_json is None:
        with open(_PLANTS_FILE, encoding="utf-8") as f:
            _plants_json = json.load(f)
    return _plants_json


def _get_collection():
    """Return the ChromaDB collection, or None if the index isn't built yet."""
    global _collection, _vector_ready
    if _vector_ready is not None:
        return _collection  # already resolved

    try:
        import chromadb
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

        if not _INDEX_DIR.exists():
            _vector_ready = False
            return None

        ef = SentenceTransformerEmbeddingFunction(model_name=_MODEL_NAME)
        client = chromadb.PersistentClient(path=str(_INDEX_DIR))
        _collection = client.get_collection(_COLLECTION, embedding_function=ef)
        _vector_ready = True
    except Exception:
        _vector_ready = False
        _collection = None

    return _collection


def _json_lookup(plant_name: str) -> dict | None:
    """Exact/plural/substring lookup against the JSON file (original logic)."""
    plants = _load_json()
    name_lower = plant_name.lower()
    normalized = name_lower.replace(" ", "_").replace("-", "_")

    candidates = [normalized]
    if normalized.endswith("es"):
        candidates.append(normalized[:-2])
    elif normalized.endswith("s"):
        candidates.append(normalized[:-1])

    for candidate in candidates:
        if candidate in plants:
            return plants[candidate]

    for info in plants.values():
        common = info["common_name"].lower()
        if name_lower in common or common in name_lower:
            return info

    return None


def lookup_plant_care(plant_name: str) -> dict:
    """Look up watering, sun, temp tolerances, and care info for a plant.

    Tries semantic vector search first (if the index is built), then falls
    back to exact/substring JSON lookup, then returns an error dict.
    """
    # JSON exact/plural/substring lookup is fast — try it first
    result = _json_lookup(plant_name)
    if result is not None:
        return result

    # Semantic vector search for queries the JSON can't match (e.g. "Italian herb")
    collection = _get_collection()
    if collection is not None:
        try:
            results = collection.query(
                query_texts=[plant_name],
                n_results=1,
                include=["distances", "metadatas"],
            )
            distance = results["distances"][0][0]
            if distance < _SIM_THRESHOLD:
                key = results["metadatas"][0][0]["key"]
                plants = _load_json()
                if key in plants:
                    return plants[key]
        except Exception:
            pass

    return {
        "error": (
            f"No plant data found for '{plant_name}'. "
            "Try a common name such as 'tomato', 'basil', or 'marigold'."
        )
    }
