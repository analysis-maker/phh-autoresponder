
import hmac, hashlib, urllib.parse, json, time
from fastapi import APIRouter, Request, HTTPException
from app.config import settings
from app.clients.helpscout_client import send_now, link_to_conversation

router = APIRouter()

def verify_slack(body: bytes, ts: str, sig: str) -> bool:
    if not settings.slack_signing_secret:
        return True
    base = f"v0:{ts}:{body.decode()}"
    my = "v0=" + hmac.new(settings.slack_signing_secret.encode(), base.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(my, sig or "")

@router.post("/slack/actions")
async def slack_actions(request: Request):
    ts = request.headers.get("X-Slack-Request-Timestamp", "")
    sig = request.headers.get("X-Slack-Signature", "")
    body = await request.body()
    if not verify_slack(body, ts, sig):
        raise HTTPException(status_code=401, detail="Invalid Slack signature")
    payload = urllib.parse.parse_qs(body.decode()).get("payload", ["{}"])[0]
    data = json.loads(payload)
    action = (data.get("actions") or [{}])[0]
    action_id = action.get("action_id")
    thread_id = action.get("value")
    if action_id == "approve_send":
        res = await send_now(thread_id)
        return {"text": f"Sent: {res}"}
    elif action_id == "edit_hs":
        url = link_to_conversation(thread_id)
        return {"text": f"Open in Help Scout: {url}"}
    elif action_id == "escalate":
        return {"text": "Escalated to human. Automation paused."}
    return {"text": "Unknown action"}
