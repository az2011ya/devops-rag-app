import os
import glob
import hashlib
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
COLLECTION_NAME = "devops_knowledge"

client = QdrantClient(url=QDRANT_URL)

def ensure_collection():
    """S'assure que la collection Qdrant existe."""
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
        print(f"📦 Collection '{COLLECTION_NAME}' créée.")

def get_embedding(text: str) -> list[float]:
    """Génère l'embedding vectoriel via le modèle nomic-embed-text d'Ollama."""
    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json={
        "model": "nomic-embed-text",
        "prompt": text
    })
    resp.raise_for_status()
    return resp.json()["embedding"]

def file_to_id(filepath: str) -> int:
    """Génère un ID entier déterministe à partir du chemin du fichier."""
    return int(hashlib.md5(filepath.encode()).hexdigest()[:8], 16)

def process_docs_folder(folder_path="docs"):
    """Lit tous les fichiers .md du dossier et les injecte dans Qdrant."""
    ensure_collection()
    pattern = os.path.join(folder_path, "*.md")
    files = glob.glob(pattern)

    if not files:
        print(f"⚠️ Aucun fichier .md trouvé dans '{folder_path}'")
        return

    print(f"🚀 Début de l'ingestion depuis '{folder_path}'...")
    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        point_id = file_to_id(filepath)
        filename = os.path.basename(filepath)
        
        print(f"  ➜ Vectorisation de {filename}...")
        vector = get_embedding(content)

        # Upsert : insère ou met à jour si l'ID existe déjà
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "source": filename,
                        "text": content,
                        "path": filepath
                    }
                )
            ]
        )
        print(f"  ✅ Ingesté avec succès (ID: {point_id})")

    print("🎉 Ingestion terminée !")

if __name__ == "__main__":
    process_docs_folder()
