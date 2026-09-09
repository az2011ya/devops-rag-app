import os
import glob
import hashlib
import requests

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333").strip().strip('"').strip("'").rstrip('/')
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").strip().strip('"').strip("'").rstrip('/')
COLLECTION_NAME = "devops_knowledge"

def ensure_collection():
    """S'assure que la collection Qdrant existe via l'API REST HTTP."""
    headers = {"Content-Type": "application/json"}
    
    # 1. Vérifie si la collection existe
    resp = requests.get(f"{QDRANT_URL}/collections", headers=headers, timeout=30.0)
    resp.raise_for_status()
    collections = [c["name"] for c in resp.json().get("result", {}).get("collections", [])]
    
    # 2. Si elle n'existe pas, on la crée
    if COLLECTION_NAME not in collections:
        payload = {
            "vectors": {
                "size": 768,
                "distance": "Cosine"
            }
        }
        create_resp = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION_NAME}", 
            json=payload, 
            headers=headers, 
            timeout=30.0
        )
        create_resp.raise_for_status()
        print(f"📦 Collection '{COLLECTION_NAME}' créée.")

def get_embedding(text: str) -> list[float]:
    """Génère l'embedding vectoriel via Ollama."""
    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json={
        "model": "nomic-embed-text",
        "prompt": text
    }, timeout=60.0)
    resp.raise_for_status()
    return resp.json()["embedding"]

def file_to_id(filepath: str) -> int:
    """Génère un ID entier déterministe à partir du chemin du fichier."""
    return int(hashlib.md5(filepath.encode()).hexdigest()[:8], 16)

def process_docs_folder(folder_path="docs"):
    """Lit tous les fichiers .md du dossier et les injecte dans Qdrant via l'API REST."""
    ensure_collection()
    pattern = os.path.join(folder_path, "*.md")
    files = glob.glob(pattern)

    if not files:
        print(f"⚠️ Aucun fichier .md trouvé dans '{folder_path}'")
        return

    print(f"🚀 Début de l'ingestion depuis '{folder_path}'...")
    headers = {"Content-Type": "application/json"}

    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        point_id = file_to_id(filepath)
        filename = os.path.basename(filepath)

        print(f"  ➜ Vectorisation de {filename}...")
        vector = get_embedding(content)

        # Upsert des points via l'API REST native de Qdrant
        payload = {
            "points": [
                {
                    "id": point_id,
                    "vector": vector,
                    "payload": {
                        "source": filename,
                        "text": content,
                        "path": filepath
                    }
                }
            ]
        }
        
        upsert_resp = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points?wait=true", 
            json=payload, 
            headers=headers, 
            timeout=60.0
        )
        upsert_resp.raise_for_status()
        print(f"  ✅ Ingesté avec succès (ID: {point_id})")

    print("🎉 Ingestion terminée !")

if __name__ == "__main__":
    process_docs_folder()
