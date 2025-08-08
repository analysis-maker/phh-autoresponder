
# PHH Autoresponder

Self-hostable FastAPI service for Professional Holiday Homes:
- Receives Help Scout webhooks
- Drafts replies from a local KB (CSV/MD + embeddings)
- Slack "Review & Approve" channel
- HomeHero lookup (stub until real endpoint provided)
- OAuth placeholders for Help Scout (fill env + we’ll finish wiring)

## Quick Start
1. Copy env
   ```bash
   cp .env.example .env
   ```
2. Seed KB
   ```bash
   python scripts/seed_kb.py
   ```
3. Run
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```
4. Health check: `GET /healthz`

## Endpoints
- `POST /webhook/helpscout` — incoming HS events
- `GET /oauth/helpscout/start` — begin OAuth (placeholder)
- `GET /oauth/helpscout/callback` — finish OAuth (placeholder storage)
- `POST /slack/actions` — Slack button clicks
- `POST /admin/reply` — test a draft from raw text
- `GET /healthz` — status

## Slack
Set `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `SLACK_REVIEW_CHANNEL_ID` in env.

## Help Scout
Create an OAuth app in Help Scout and paste credentials into env. Webhook secret must match Help Scout webhook config.
