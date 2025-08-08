
from typing import List, Tuple, Dict
import os, json, numpy as np, pandas as pd
from app.models.schemas import KBItem
from app.config import settings
from openai import OpenAI

def _load_kb_csv(path: str) -> List[KBItem]:
    rows = []
    if not os.path.exists(path):
        return rows
    df = pd.read_csv(path)
    for i, r in df.iterrows():
        rows.append(KBItem(
            id=str(r.get('id', i)),
            title=str(r.get('title', '')),
            content=str(r.get('content', '')),
            tags=str(r.get('tags', '')).split('|') if isinstance(r.get('tags', ''), str) else []
        ))
    return rows

def _load_kb_md(path: str) -> List[KBItem]:
    items = []
    if not os.path.exists(path):
        return items
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    sections = [s.strip() for s in content.split('\n## ') if s.strip()]
    for i, sec in enumerate(sections):
        lines = sec.splitlines()
        title = lines[0].strip('# ').strip()
        body = '\n'.join(lines[1:]).strip()
        items.append(KBItem(id=f"md-{i}", title=title, content=body, tags=[]))
    return items

def build_or_load_embeddings(kb_items: List[KBItem]) -> Dict:
    store_path = settings.kb_store
    if os.path.exists(store_path):
        with open(store_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    texts = [f"{it.title}\n{it.content}" for it in kb_items]
    if client:
        resp = client.embeddings.create(model=settings.embedding_model, input=texts)
        vectors = [d.embedding for d in resp.data]
    else:
        vectors = [np.random.rand(256).tolist() for _ in texts]
    store = {"ids":[it.id for it in kb_items], "titles":[it.title for it in kb_items],
             "tags":[it.tags for it in kb_items], "vectors":vectors, "contents":[it.content for it in kb_items]}
    os.makedirs(os.path.dirname(store_path), exist_ok=True)
    with open(store_path, 'w', encoding='utf-8') as f:
        json.dump(store, f)
    return store

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(a.dot(b) / denom) if denom else 0.0

def search(query: str, k: int = 5) -> List[Tuple[str, str, str]]:
    with open(settings.kb_store, 'r', encoding='utf-8') as f:
        store = json.load(f)
    client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    if client:
        qv = client.embeddings.create(model=settings.embedding_model, input=[query]).data[0].embedding
    else:
        qv = np.random.rand(256).tolist()
    qv = np.array(qv)
    sims = []
    for i, v in enumerate(store["vectors"]):
        sims.append((cosine_similarity(qv, np.array(v)), store["titles"][i], store["contents"][i], store["ids"][i]))
    sims.sort(key=lambda x: x[0], reverse=True)
    return [(t, c, i) for _, t, c, i in sims[:k]]
