
from typing import List, Dict
from app.config import settings
from openai import OpenAI

SYSTEM_PROMPT = (
    "You are PHH's email assistant. Answer concisely, professionally, and helpfully. "
    "Never invent policies; if unsure, ask to escalate to a human agent. "
    "Keep owner emails untouched (flag for human)."
)

def generate_reply(question: str, kb_chunks: List[Dict]) -> str:
    client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    kb_context = "\n\n".join([f"### {c['title']}\n{c['content']}" for c in kb_chunks])
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context from knowledge base:\n{kb_context}\n\n"
        f"User message:\n{question}\n\n"
        "Draft a clear, friendly response. Include bullet points where helpful."
    )
    if client:
        resp = client.chat.completions.create(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":prompt},
            ]
        )
        return resp.choices[0].message.content.strip()
    return "Thanks for reaching out! We'll get back to you shortly with the details you requested."
