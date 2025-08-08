
from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/oauth/helpscout/start")
def oauth_start():
    # Placeholder: Construct the Help Scout OAuth authorize URL using env values.
    # User will be redirected to Help Scout, then back to /oauth/helpscout/callback.
    return {
        "message": "Placeholder - configure Help Scout OAuth in env, then replace with redirect.",
        "client_id": settings.helpscout_client_id,
        "redirect_uri": settings.helpscout_redirect_uri
    }

@router.get("/oauth/helpscout/callback")
def oauth_callback(code: str = "", state: str = ""):
    # Placeholder: Exchange 'code' for tokens and persist to disk (data/helpscout_tokens.json).
    # We'll complete this once Help Scout app is created.
    return {"message": "Placeholder callback received", "code": code, "state": state}
