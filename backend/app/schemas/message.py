from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class MessageBase(BaseModel):
    lead_id: int
    lead_name: str
    lead_email: EmailStr
    subject: str
    content: str
    campaign_id: int
    campaign_name: str

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    status: Optional[str] = None
    open_date: Optional[datetime] = None
    reply_date: Optional[datetime] = None

class Message(MessageBase):
    id: int
    status: str
    sent_date: datetime
    open_date: Optional[datetime] = None
    reply_date: Optional[datetime] = None

    class Config:
        orm_mode = True

class MessageResponse(Message):
    pass

class PaginatedMessageResponse(BaseModel):
    items: List[Message]
    total: int
    page: int
    limit: int
    totalPages: int 