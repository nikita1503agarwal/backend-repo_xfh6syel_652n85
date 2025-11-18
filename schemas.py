"""
Database Schemas for the corporate website

Each Pydantic model corresponds to a MongoDB collection (lowercased class name).
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime

class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=5000)
    company: Optional[str] = Field(None, max_length=200)
    source: Optional[str] = Field(None, description="Where the message originated from (page/section)")

class ContactMessageDB(ContactMessage):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class NewsletterSubscriber(BaseModel):
    email: EmailStr
    source: Optional[str] = Field(None)

class NewsletterSubscriberDB(NewsletterSubscriber):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

ConsentAction = Literal['accept','reject','update']

class ConsentEvent(BaseModel):
    session_id: str = Field(..., min_length=6, max_length=200)
    category: Literal['necessary','analytics','marketing','preferences','all'] = 'all'
    action: ConsentAction = 'accept'
    consent: bool = True
    source: Optional[str] = Field(None)
    user_agent: Optional[str] = None

class ConsentEventDB(ConsentEvent):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
