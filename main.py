
from fastapi import FastAPI
from app.routers.webhooks import router as webhooks_router
from app.routers.slack import router as slack_router
from app.routers.oauth_hs import router as oauth_hs_router

app = FastAPI(title="PHH Autoresponder", version="0.2.0")

app.include_router(webhooks_router, tags=["webhooks"])
app.include_router(slack_router, tags=["slack"])
app.include_router(oauth_hs_router, tags=["oauth"])
