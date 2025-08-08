
from fastapi import APIRouter, Header
from app.models.schemas import EmailEvent, ReplyDraft
from app.services.classifier import classify_sender
from app.services.kb import search
from app.services.llm import generate_reply
from app.services.templating import render_reply
from app.clients.helpscout_client import create_draft
from app.clients.homehero_client import get_guest_authorization
from app.clients.slack_client import post_review_card
from app.config import settings

router = APIRouter()

def verify_signature(signature: str, body: bytes):
    # TODO: HMAC check vs settings.helpscout_webhook_secret
    return True

@router.post("/webhook/helpscout")
async def helpscout_webhook(event: EmailEvent, x_signature: str | None = Header(default=None, alias="X-Signature")):
    category = classify_sender(event.from_email, event.subject, event.body_text)
    if category == "owner":
        return {"status":"ok", "routed":"owner", "action":"none"}

    hh = await get_guest_authorization(event.from_email)

    top = search(event.body_text, k=5)
    kb_chunks = [{"title":t, "content":c, "id":i} for (t,c,i) in top]

    reply_text = generate_reply(event.body_text, kb_chunks)
    html = render_reply({"body": reply_text, "references_html": ""})
    draft = ReplyDraft(thread_id=event.thread_id or event.id, body_html=html, send=(settings.auto_reply_enabled and category=="guest"))
    res = await create_draft(draft)

    try:
        await post_review_card(settings.slack_review_channel_id or "", event.thread_id or event.id, event.from_email, event.subject, html)
    except Exception:
        pass
    return {"status":"ok", "category":category, "hh":hh, "kb_used":[k['id'] for k in kb_chunks], "send_attempt":res}

@router.post("/admin/reply")
async def manual_reply(event: EmailEvent):
    top = search(event.body_text, k=5)
    kb_chunks = [{"title":t, "content":c, "id":i} for (t,c,i) in top]
    reply_text = generate_reply(event.body_text, kb_chunks)
    html = render_reply({"body": reply_text, "references_html": ""})
    return {"html": html, "kb_ids":[k['id'] for k in kb_chunks]}

@router.get("/healthz")
async def healthz():
    return {"ok": True}
