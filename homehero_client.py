
import httpx
from app.config import settings

async def get_guest_authorization(email: str):
    # TODO: Replace with real HomeHero call
    if not settings.home_hero_api_key:
        return {"is_guest": True, "booking_id": None, "property_code_allowed": False}
    return {"is_guest": True, "booking_id": "HH-EXAMPLE", "property_code_allowed": True}
