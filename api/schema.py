from ninja import Schema
from typing import Optional, Dict, List
from datetime import datetime


class RegisterSchema(Schema):
    username: str
    password: str



#Message Schemas

class MessageInSchema(Schema):
    """Incoming user message."""
    text: str

class MessageOutSchema(Schema):
    """Represents stored message details."""
    id: int
    sender: str
    text: str
    timestamp: datetime
    is_triage_trigger: bool

# Session Schemas

class SessionCreateSchema(Schema):
    """Input for creating a session (currently no input needed)."""
    pass

class DifferentialSchema(Schema):
    diagnosis: str
    confidence: str

class SessionCreateOutSchema(Schema):
    """Output after session is created."""
    id: int
    user_id: int
    started_at: datetime
    current_section: str
    is_active: bool


class SessionDetailSchema(Schema):
    """Detailed view of a session, including messages."""
    id: int
    user_id: int
    started_at: datetime
    current_section: str
    is_active: bool
    triage_level: Optional[str]
    collected_data: Dict
    hpc_summary: Optional[str]
    differentials: Optional[Dict]
    messages: List[MessageOutSchema]


class SessionSummarySchema(Schema):
    """Summary of the session after conversation is complete."""
    id: int
    hpc_summary: Optional[str]
    differentials: List[DifferentialSchema]
    triage_level: Optional[str]

# Chat Schema

class ChatResponseSchema(Schema):
    """Response to each user message during the conversation."""
    session_id: int
    message: str
    current_section: str
    triage_level: Optional[str] = None
    session_active: bool = True