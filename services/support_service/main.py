import json
import uuid
import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from services.common.database import get_db, Base, engine
from services.common.models import SupportTicketModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "support-service"

app = FastAPI(title="Customer Support Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

class CreateTicketRequest(BaseModel):
    user_id: int
    user_email: EmailStr
    order_number: Optional[str] = None
    subject: str
    category: str # Order Issue, Payment, Refund, Return, Product Inquiry, Technical
    message: str
    priority: Optional[str] = "MEDIUM" # LOW, MEDIUM, HIGH, URGENT

class ReplyTicketRequest(BaseModel):
    sender_name: str
    sender_role: str # customer, support_agent
    message: str

class UpdateTicketStatusRequest(BaseModel):
    status: str # OPEN, IN_PROGRESS, RESOLVED, CLOSED

def format_ticket(t: SupportTicketModel) -> dict:
    return {
        "id": t.id,
        "ticket_id": t.ticket_id,
        "user_id": t.user_id,
        "user_email": t.user_email,
        "order_number": t.order_number,
        "subject": t.subject,
        "category": t.category,
        "message": t.message,
        "status": t.status,
        "priority": t.priority,
        "responses": json.loads(t.responses_json) if t.responses_json else [],
        "created_at": t.created_at.isoformat(),
        "updated_at": t.updated_at.isoformat()
    }

@app.post("/tickets", status_code=status.HTTP_201_CREATED)
def create_ticket(req: CreateTicketRequest, db: Session = Depends(get_db)):
    ticket_id = f"TCK-{uuid.uuid4().hex[:6].upper()}"
    now = datetime.datetime.utcnow().isoformat()

    initial_responses = [
        {
            "sender_name": "Support Auto-Responder",
            "sender_role": "system",
            "message": f"Hello! Your request has been logged under Ticket #{ticket_id}. A representative will review it within 2 hours.",
            "timestamp": now
        }
    ]

    ticket = SupportTicketModel(
        ticket_id=ticket_id,
        user_id=req.user_id,
        user_email=req.user_email,
        order_number=req.order_number,
        subject=req.subject,
        category=req.category,
        message=req.message,
        status="OPEN",
        priority=req.priority or "MEDIUM",
        responses_json=json.dumps(initial_responses)
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return format_ticket(ticket)

@app.get("/tickets")
def list_tickets(user_id: Optional[int] = None, status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(SupportTicketModel)
    if user_id:
        query = query.filter(SupportTicketModel.user_id == user_id)
    if status_filter:
        query = query.filter(SupportTicketModel.status == status_filter)

    tickets = query.order_by(SupportTicketModel.created_at.desc()).all()
    return [format_ticket(t) for t in tickets]

@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    return format_ticket(ticket)

@app.post("/tickets/{ticket_id}/reply")
def reply_to_ticket(ticket_id: str, req: ReplyTicketRequest, db: Session = Depends(get_db)):
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    responses = json.loads(ticket.responses_json) if ticket.responses_json else []
    responses.append({
        "sender_name": req.sender_name,
        "sender_role": req.sender_role,
        "message": req.message,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    ticket.responses_json = json.dumps(responses)
    if req.sender_role == "support_agent" and ticket.status == "OPEN":
        ticket.status = "IN_PROGRESS"

    db.commit()
    db.refresh(ticket)
    return format_ticket(ticket)

@app.put("/tickets/{ticket_id}/status")
def update_status(ticket_id: str, req: UpdateTicketStatusRequest, db: Session = Depends(get_db)):
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    ticket.status = req.status
    db.commit()
    db.refresh(ticket)
    return format_ticket(ticket)
