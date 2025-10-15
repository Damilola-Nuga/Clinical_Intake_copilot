from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from datetime import datetime
from ..convo_functions import process_message
from ..ai import generate_final_summary
from ..triage import assess_message_urgency


from ..models import Session, Message

from ..schema import (
    SessionCreateSchema,
    SessionCreateOutSchema,
    MessageInSchema,
    MessageOutSchema,
    ChatResponseSchema,
    SessionSummarySchema,
)



router = Router(auth=JWTAuth(), tags=["Sessions"])

@router.post("/sessions/", response=ChatResponseSchema)
def create_session(request, payload: SessionCreateSchema):
    """Start a new chat session."""
    user = request.auth

    # End any previous active sessions for safety
    Session.objects.filter(user=user, is_active=True).update(is_active=False)

    session = Session.objects.create(
        user=user,
        current_section="biodata",
        is_active=True,
        collected_data={},
    )

    # Create the assistant’s first message
    first_message = "Hello, What's your full name please?"
    Message.objects.create(session=session, sender="assistant", text=first_message)

    return ChatResponseSchema(
        session_id=session.id,
        message=first_message,         
        current_section=session.current_section,  
        triage_level=session.triage_level,        
        session_active=session.is_active 
    )




@router.post("/sessions/{session_id}/message/", response=ChatResponseSchema)
def send_message(request, session_id: int, payload: MessageInSchema):
    """
    User sends a message; assistant responds.
    - Logs user message
    - Runs real-time triage
    - Processes assistant response via logic layer
    - Updates session triage level and section if needed
    """
    user = request.auth
    session = get_object_or_404(Session, id=session_id, user=user)

    if not session.is_active:
        raise HttpError(400, "This session has ended. Please start a new one.")


    Message.objects.create(session=session, sender="user", text=payload.text)

    level, keyword = assess_message_urgency(payload.text)
    priority_order = {"Routine": 0, "Urgent": 1, "Emergency": 2}
    current_level = session.triage_level or "Routine"

    # Update session triage if higher priority or first time
    if priority_order[level] > priority_order[current_level]:
        session.triage_level = level
        session.save()

    

    result = process_message(session, payload.text)

    next_question = result.get("next_question")
    current_section = result.get("current_section")
    session_active = result.get("session_active")
    triage_level = session.triage_level

    
    # Save assistant message
    if next_question:
        Message.objects.create(session=session, sender="assistant", text=next_question)
    else:
        next_question = "Thank you for the information. I have everything I need."

    # Return structured response ---
    return ChatResponseSchema(
        message=next_question,
        triage_level=triage_level,
        session_active=session_active,
        current_section=current_section,
        session_id=session.id
    )

    



@router.get("/sessions/{session_id}/summary/", response=SessionSummarySchema)
def get_session_summary(request, session_id: int):
    """Get the final summary of a session (HPC, differentials, triage)."""
    user = request.auth
    session = get_object_or_404(Session, id=session_id, user=user)

    if session.is_active:
        # Optional: could warn that session is not fully complete yet
        raise HttpError(400, "Session is still active. Final summary is not available.")
    
    if session.hpc_summary and session.differentials is not None and len(session.differentials) > 0:
        summary_data = {
            "hpc_summary": session.hpc_summary,
            "differentials": session.differentials,
            "triage_level": session.triage_level,
        }

    else:
        summary_data = generate_final_summary(session)

    # summary_data = generate_final_summary(session)

    if summary_data.get("hpc_summary") != "Unable to generate summary.":
        session.hpc_summary = summary_data.get("hpc_summary")
        session.differentials = summary_data.get("differentials")
        session.triage_level = summary_data.get("triage_level") or session.triage_level or "Routine"
        session.save()


    return SessionSummarySchema(
        id=session.id,
        hpc_summary=summary_data.get("hpc_summary"),
        differentials=summary_data.get("differentials"),
        triage_level=summary_data.get("triage_level")
    )
