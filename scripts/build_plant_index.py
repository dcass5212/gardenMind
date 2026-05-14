"""
Build (or rebuild) the ChromaDB semantic index from data/plants.json.

Run once before starting the app, or whenever plants.json changes:
    py scripts/build_plant_index.py

The index is persisted to data/plant_index/ and loaded at runtime by
tools/plants.py. Embeddings use all-MiniLM-L6-v2 (~80 MB, downloads once).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

PLANTS_FILE = Path(__file__).parent.parent / "data" / "plants.json"
INDEX_DIR   = Path(__file__).parent.parent / "data" / "plant_index"
MODEL_NAME  = "all-MiniLM-L6-v2"
COLLECTION  = "plants"


def build_document(key: str, info: dict) -> str:
    """Produce a rich text blob that captures all searchable plant attributes."""
    problems = ", ".join(info.get("common_problems", []))
    return (
        f"{info['common_name']} ({key}). "
        f"Type: {info['type']}. "
        f"Sun: {info['sun_requirements']}. "
        f"Watering: {info['watering_frequency']}. "
        f"Temperature range: {info['min_temp_f']}–{info['max_temp_f']}°F. "
        f"Common problems: {problems}. "
        f"Notes: {info['planting_notes']}"
    )


def main():
    plants = json.loads(PLANTS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(plants)} plants from {PLANTS_FILE.name}")

    ef = SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    client = chromadb.PersistentClient(path=str(INDEX_DIR))

    # Delete and recreate so rebuilds are idempotent
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION, embedding_function=ef)

    ids, documents, metadatas = [], [], []
    for key, info in plants.items():
        ids.append(key)
        documents.append(build_document(key, info))
        metadatas.append({"key": key})

    # ChromaDB recommends batches ≤ 5000; 200 plants is well under that
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print(f"Indexed {len(ids)} plants into {INDEX_DIR}")
    print("Done.")


if __name__ == "__main__":
    main()
