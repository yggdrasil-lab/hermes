from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

class NotificationRequest(BaseModel):
    channel: Literal["email", "discord"]
    recipient: str # Could be email or channel ID, validation depends on channel in logic
    subject: Optional[str] = None
    body: str
