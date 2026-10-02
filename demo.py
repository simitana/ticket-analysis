#!/usr/bin/env python3
"""
Quick demo script for ticket classification.
No external dependencies required - just uses keyword matching.
"""

# Classification rules - ORDER MATTERS for priority
BILLING_KEYWORDS = ("charg", "refund", "payment", "bill", "paid", "duplicate", "double", "credit")
TECHNICAL_KEYWORDS = ("crash", "bug", "app ", "error", "broken", "connectivity", "broken link", "site down", "site is down")
ACCOUNT_KEYWORDS = ("account", "profile", "reset password", "password reset", "change ", "update ", "remove ", "add ", "delete", "access my account")
SALES_KEYWORDS = ("price", "upgrade", "plan", "feature", "cost", "questions", "inquiry", "about", "how to")
URGENT_KEYWORDS = ("today", "urgent", "asap", "immediately", "now", "emergency", "critical", "blocked", 
                   "down", "outage", "24 hours", "cannot", "can't", "please fix")


def classify_ticket(description: str) -> dict:
    """Classify a support ticket into department and urgency."""
    desc = description.lower()
    
    # Determine department with priority
    # billing > account > technical > sales > general
    if any(kw in desc for kw in BILLING_KEYWORDS):
        department = "billing"
    elif any(kw in desc for kw in ACCOUNT_KEYWORDS):
        department = "account"
    elif any(kw in desc for kw in TECHNICAL_KEYWORDS):
        department = "technical"
    elif any(kw in desc for kw in SALES_KEYWORDS):
        department = "sales"
    else:
        department = "general"
    
    # Determine urgency
    is_urgent = any(kw in desc for kw in URGENT_KEYWORDS)
    urgency_score = 0.85 if is_urgent else 0.3
    
    routing = {
        "billing": {"team": "Billing & Payments Team", "channel": "payment-support@company.com"},
        "technical": {"team": "Technical Support Team", "channel": "tech-support@company.com"},
        "account": {"team": "Account Management Team", "channel": "accounts@company.com"},
        "sales": {"team": "Sales Team", "channel": "sales@company.com"},
        "general": {"team": "General Support Team", "channel": "support@company.com"}
    }
    
    route = routing[department]
    
    return {
        "department": department,
        "urgency_score": urgency_score,
        "is_urgent": is_urgent,
        "team": route["team"],
        "channel": route["channel"]
    }


def main():
    """Demo the classification."""
    import json
    
    tickets = [
        {"id": "001", "desc": "I was charged twice for my subscription. Please refund one charge today."},
        {"id": "002", "desc": "My app crashed during checkout and I cannot complete my purchase."},
        {"id": "003", "desc": "I need help resetting my password but the email is not arriving."},
        {"id": "004", "desc": "What features are included in the premium plan? How much does it cost?"},
        {"id": "005", "desc": "I have a general question about your service."},
    ]
    
    print("=" * 60)
    print("TICKET CLASSIFICATION DEMO")
    print("=" * 60)
    
    for t in tickets:
        result = classify_ticket(t["desc"])
        print(f"\nTicket {t['id']}: {t['desc'][:50]}...")
        print(f"  -> Department: {result['department'].upper()}")
        print(f"  -> Urgency: {result['urgency_score']:.0%} {'🔴' if result['is_urgent'] else '🟢'}")
        print(f"  -> Team: {result['team']}")


if __name__ == "__main__":
    main()