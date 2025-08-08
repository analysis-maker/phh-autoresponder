
from app.models.schemas import ReplyDraft

async def create_draft(reply: ReplyDraft):
    # TODO: Implement Help Scout Conversations API call with OAuth access token
    return {"status":"ok", "detail":"(stub) draft created or queued"}

async def send_now(thread_id: str):
    # TODO: Implement send via Help Scout API
    return {"status":"ok", "detail":"(stub) sent"}

def link_to_conversation(thread_id: str) -> str:
    return f"https://secure.helpscout.net/conversation/{thread_id}/"
