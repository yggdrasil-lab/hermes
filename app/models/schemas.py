from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

class NotificationRequest(BaseModel):
    channel: Literal["email"]
    recipient: str # Could be email or channel ID, validation depends on channel in logic
    sender: Optional[str] = None
    subject: Optional[str] = None
    body: str
