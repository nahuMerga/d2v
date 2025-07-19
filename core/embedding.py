# core/embedding.py

import uuid
import torch
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from .config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME

from transformers import AutoTokenizer, AutoModel

MODEL_NAME = "intfloat/multilingual-e5-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

def generate_offline_embedding(text: str) -> list:
    if "intfloat" in MODEL_NAME:
        text = f"passage: {text}"
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        normalized = torch.nn.functional.normalize(embeddings, p=2, dim=1)
    return normalized[0].tolist()

def generate_embeddings_for_chunks(chunks: list) -> list:
    """Generate embeddings for a list of text chunks without uploading."""
    results = []
    for chunk in chunks:
        embedding = generate_offline_embedding(chunk)
        results.append({"text": chunk, "embedding": embedding})
    return results

def get_qdrant_client():
    if QDRANT_API_KEY:
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return QdrantClient(url=QDRANT_URL)

def ensure_collection(client: QdrantClient, vector_size: int):
    collections = client.get_collections().collections
    if COLLECTION_NAME not in [c.name for c in collections]:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )

def upload_embeddings_to_qdrant(embeddings: list):
    if not embeddings:
        print("⚠️ No embeddings to upload.")
        return

    vector_size = len(embeddings[0]['embedding'])
    client = get_qdrant_client()
    ensure_collection(client, vector_size)

    points = []
    for entry in embeddings:
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=entry['embedding'],
            payload={"text": entry['text']}
        )
        points.append(point)

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Uploaded {len(points)} chunks to Qdrant.")
