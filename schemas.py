
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class EmailEvent(BaseModel):
    id: str
    subject: str
    from_email: str
    to_email: str
    body_text: str
    thread_id: Optional[str] = None
    mailbox_id: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

class ReplyDraft(BaseModel):
    thread_id: str
    subject: Optional[str] = None
    body_html: str
    send: bool = False

class KBItem(BaseModel):
    id: str
    title: str
    content: str
    tags: List[str] = []
