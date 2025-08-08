
import httpx
from app.config import settings

SLACK_POST_MESSAGE_URL = "https://slack.com/api/chat.postMessage"

async def post_review_card(channel_id: str, thread_id: str, sender: str, subject: str, preview_html: str):
    if not settings.slack_bot_token or not channel_id:
        return {"status":"stub","detail":"Slack not configured"}
    text = f"*PHH Draft Reply*\n*From:* {sender}\n*Subject:* {subject}\n\nA draft is ready. Use the buttons below."
    blocks = [
        {"type":"section","text":{"type":"mrkdwn","text":text}},
        {"type":"actions","elements":[
            {"type":"button","text":{"type":"plain_text","text":"Approve & Send"},"style":"primary","value":thread_id,"action_id":"approve_send"},
            {"type":"button","text":{"type":"plain_text","text":"Edit in Help Scout"},"value":thread_id,"action_id":"edit_hs"},
            {"type":"button","text":{"type":"plain_text","text":"Escalate to Human"},"style":"danger","value":thread_id,"action_id":"escalate"}
        ]}
    ]
    headers = {
        "Authorization": f"Bearer {settings.slack_bot_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {"channel": channel_id, "text": text, "blocks": blocks}
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(SLACK_POST_MESSAGE_URL, headers=headers, json=payload)
        try:
            return r.json()
        except Exception:
            return {"ok": False, "status_code": r.status_code, "text": r.text}
