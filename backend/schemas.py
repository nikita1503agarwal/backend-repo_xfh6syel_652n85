from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=5000)
    company: Optional[str] = Field(None, max_length=200)


class NewsletterSubscriber(BaseModel):
    email: EmailStr
    source: Optional[str] = Field(None, max_length=120)


class ConsentEvent(BaseModel):
    session_id: str
    consent: bool
    details: Optional[dict] = None


# Helper schemas with metadata (timestamps are added by DB helper create_document)
class ContactMessageDB(ContactMessage):
    created_at: Optional[datetime] = None


class NewsletterSubscriberDB(NewsletterSubscriber):
    created_at: Optional[datetime] = None
