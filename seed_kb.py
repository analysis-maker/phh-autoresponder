
import os, json
from app.services.kb import _load_kb_csv, _load_kb_md, build_or_load_embeddings
from app.config import settings

def main():
    csv_path = os.path.join(settings.kb_path, "faq.csv")
    md_path = os.path.join(settings.kb_path, "examples.md")
    items = _load_kb_csv(csv_path) + _load_kb_md(md_path)
    store = build_or_load_embeddings(items)
    print(f"Embedded {len(store['ids'])} KB items -> {settings.kb_store}")

if __name__ == "__main__":
    main()
