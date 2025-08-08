
from pydantic import BaseModel
import os

class Settings(BaseModel):
    env: str = os.getenv("ENV", "dev")
    port: int = int(os.getenv("PORT", "8080"))
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Help Scout OAuth + webhook
    helpscout_client_id: str = os.getenv("HELP_SCOUT_OAUTH_CLIENT_ID", "")
    helpscout_client_secret: str = os.getenv("HELP_SCOUT_OAUTH_CLIENT_SECRET", "")
    helpscout_redirect_uri: str = os.getenv("HELP_SCOUT_OAUTH_REDIRECT_URI", "")
    helpscout_webhook_secret: str = os.getenv("HELP_SCOUT_WEBHOOK_SECRET", "")
    helpscout_mailbox_id: str = os.getenv("HELP_SCOUT_MAILBOX_ID", "")

    home_hero_api_key: str = os.getenv("HOME_HERO_API_KEY", "")
    home_hero_base_url: str = os.getenv("HOME_HERO_BASE_URL", "")

    kb_path: str = os.getenv("KB_PATH", "./data/kb")
    kb_store: str = os.getenv("KB_EMBEDDINGS_STORE", "./data/kb/embeddings.json")

    # Slack
    slack_bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    slack_signing_secret: str = os.getenv("SLACK_SIGNING_SECRET", "")
    slack_review_channel_id: str = os.getenv("SLACK_REVIEW_CHANNEL_ID", "")

    # Control flags
    draft_mode: bool = os.getenv("DRAFT_MODE", "true").lower() == "true"
    auto_reply_enabled: bool = os.getenv("AUTO_REPLY_ENABLED", "false").lower() == "true"

settings = Settings()
