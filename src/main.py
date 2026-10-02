"""
Ticket Analysis API using Laya decision model via Ollama.
Routes support tickets based on department and urgency.
"""

import os
import httpx
import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Tenta carregar Laya, mas continua com fallback se não disponível
try:
    from laya import Router
    router = Router(preload=True)
    LAYA_AVAILABLE = True
except Exception:
    LAYA_AVAILABLE = False


class Ticket(BaseModel):
    id: str
    description: str
    user_id: str
    timestamp: str
    metadata: Dict[str, Any] = {}


class TicketResponse(BaseModel):
    ticket_id: str
    department: str
    confidence: float
    urgency_score: float
    is_urgent: bool
    reasoning: str


# Departamento roteamento info
DEPARTMENT_ROUTING: Dict[str, Dict[str, str]] = {
    "billing": {
        "team": "Billing & Payments Team",
        "channel": "payment-support@company.com",
        "sla": "2 hours for urgent"
    },
    "technical": {
        "team": "Technical Support Team",
        "channel": "tech-support@company.com",
        "sla": "4 hours"
    },
    "account": {
        "team": "Account Management Team",
        "channel": "accounts@company.com",
        "sla": "8 hours"
    },
    "sales": {
        "team": "Sales Team",
        "channel": "sales@company.com",
        "sla": "1 business day"
    },
    "general": {
        "team": "General Support Team",
        "channel": "support@company.com",
        "sla": "2 business days"
    }
}

# Classification rules - ORDER MATTERS for priority
BILLING_KEYWORDS = ("charg", "refund", "payment", "bill", "paid", "duplicate", "double", "credit")
TECHNICAL_KEYWORDS = ("crash", "bug", " app ", "error", "broken", "connectivity", "site down", "login issue", "frozen")
ACCOUNT_KEYWORDS = ("account", "profile", "reset password", "password reset", "access my account", "change email", "update billing")
SALES_KEYWORDS = ("price", "upgrade", "plan", "feature", "cost", "questions", "inquiry", "about", "how to")
URGENT_KEYWORDS = ("today", "urgent", "asap", "immediately", "now", "emergency", "critical", "blocked", 
                   "down", "outage", "cannot", "can't", "please fix", "24 hours")


def classify_department_laya(description: str) -> Dict[str, Any]:
    """Classify ticket into department using Laya choice question."""
    if not LAYA_AVAILABLE:
        return {"department": simple_fallback_classification(description), "confidence": 0.7, "distribution": {}}
    
    questions = {
        "department": {
            "type": "choice",
            "instructions": "Which department should handle this ticket?",
            "criteria": {
                "billing": "Billing, payments, refunds, charge disputes, double charges",
                "technical": "App bugs, login issues, connectivity problems, crashes, cannot access",
                "account": "Account access, profile changes, password reset, personal details",
                "sales": "Product inquiries, pricing, plans, upgrades, features",
                "general": "General questions, feedback, non-specific issues"
            }
        }
    }
    
    result = router.route(input=description, questions=questions)
    dept_result = result["results"]["department"]
    
    return {
        "department": dept_result.selected,
        "confidence": dept_result.confidence,
        "distribution": dept_result.distribution
    }


def assess_urgency_laya(description: str) -> Dict[str, Any]:
    """Assess urgency score using Laya noul (boolean probability)."""
    if not LAYA_AVAILABLE:
        is_urgent = any(kw in description.lower() for kw in URGENT_KEYWORDS)
        return {"urgency_score": 0.85 if is_urgent else 0.3, "confidence": 0.7}
    
    questions = {
        "is_urgent": {
            "type": "noul",
            "instructions": "Does this ticket require immediate attention? Consider keywords like urgent, down, broken, cannot access, today..."
        }
    }
    
    result = router.route(input=description, questions=questions)
    is_urgent = result["results"]["is_urgent"]
    
    return {
        "urgency_score": is_urgent.noul,
        "confidence": is_urgent.confidence
    }


def simple_fallback_classification(description: str) -> str:
    """Simple keyword-based fallback for department classification."""
    desc = description.lower()
    
    # Check payment/charging keywords for billing
    if any(kw in desc for kw in BILLING_KEYWORDS):
        return "billing"
    # Check account-related keywords (password reset goes here)
    elif any(kw in desc for kw in ACCOUNT_KEYWORDS):
        return "account"
    # Check technical keywords
    elif any(kw in desc for kw in TECHNICAL_KEYWORDS):
        return "technical"
    # Check sales keywords
    elif any(kw in desc for kw in SALES_KEYWORDS):
        return "sales"
    else:
        return "general"


def simple_urgency_score(description: str) -> float:
    """Simple keyword-based urgency scoring."""
    desc = description.lower()
    
    if any(kw in desc for kw in URGENT_KEYWORDS):
        return 0.85
    elif any(kw in desc for kw in ("soon", "next business day", "when possible")):
        return 0.4
    return 0.2


def process_ticket(ticket: Ticket) -> TicketResponse:
    """Process ticket using Laya or fallback classification."""
    description = ticket.description
    
    # Validate department classification
    dept_result = classify_department_laya(description)
    dept = dept_result["department"]
    confidence = dept_result.get("confidence", 0.7)
    
    # Assess urgency
    urgency_result = assess_urgency_laya(description)
    urgency_score = urgency_result["urgency_score"]
    
    # Build reasoning
    routing = DEPARTMENT_ROUTING.get(dept, DEPARTMENT_ROUTING["general"])
    
    reasoning = (
        f"Department: {dept} (confidence: {confidence:.2f}). "
        f"Urgency: {urgency_score:.2f}. "
        f"Routing to: {routing['team']}"
    )
    
    return TicketResponse(
        ticket_id=ticket.id,
        department=dept,
        confidence=confidence,
        urgency_score=urgency_score,
        is_urgent=urgency_score > 0.5,
        reasoning=reasoning
    )


# FastAPI application
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Ticket Analysis API",
    description="Classification system using Laya decision model",
    version="1.0.0"
)


@app.post("/analyze", response_model=TicketResponse)
async def analyze_ticket(ticket: Ticket):
    """Analyze a support ticket and return routing decision."""
    try:
        return process_ticket(ticket)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-batch", response_model=List[TicketResponse])
async def analyze_tickets(tickets: List[Ticket]):
    """Batch analyze multiple tickets."""
    results = []
    for ticket in tickets:
        try:
            result = process_ticket(ticket)
            results.append(result)
        except Exception as e:
            results.append(TicketResponse(
                ticket_id=ticket.id,
                department="error",
                confidence=0.0,
                urgency_score=0.0,
                is_urgent=False,
                reasoning=f"Error: {str(e)}"
            ))
    return results


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "ollama_url": OLLAMA_URL,
        "laya_available": LAYA_AVAILABLE
    }


@app.get("/tickets/example")
def get_example_ticket():
    """Returns an example ticket for testing."""
    return Ticket(
        id="TKT-001",
        description="I was charged twice for my subscription this month. Please refund one of the charges. I need this resolved today.",
        user_id="USR-12345",
        timestamp="2024-01-15T14:30:00Z"
    )