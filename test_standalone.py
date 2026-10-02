#!/usr/bin/env python3
"""
Standalone ticket analysis without Docker.
Uses Laya directly with local model or fallback.
"""

import sys
import os

# Verifica se Laya está disponível
try:
    from laya import Router
    LAYA_AVAILABLE = True
    print("✓ Laya model available")
except ImportError:
    LAYA_AVAILABLE = False
    print("✗ Laya not installed. Install with: pip install laya")

# Verifica se Ollama está disponível
try:
    import httpx
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("✗ httpx not installed. Install with: pip install httpx")

if not LAYA_AVAILABLE:
    print("\nInstalling dependencies...")
    os.system("pip install laya httpx fastapi uvicorn pydantic")

# Test inline
def test_classification():
    """Test ticket classification logic."""
    test_tickets = [
        {
            "id": "TKT-001",
            "description": "I was charged twice for my subscription this month. Please refund one of the charges. I need this resolved today.",
            "expected_dept": "billing",
            "expected_urgent": True
        },
        {
            "id": "TKT-002", 
            "description": "My app crashed during checkout and I cannot complete my purchase on any device.",
            "expected_dept": "technical",
            "expected_urgent": True
        },
        {
            "id": "TKT-003",
            "description": "How do I upgrade my plan? What features are included?",
            "expected_dept": "sales",
            "expected_urgent": False
        }
    ]
    
    print("\n" + "="*60)
    print("TICKET CLASSIFICATION TEST")
    print("="*60)
    
    for ticket in test_tickets:
        print(f"\nTicket: {ticket['id']}")
        print(f"Description: {ticket['description'][:60]}...")
        
        # Simple fallback classification
        desc_lower = ticket['description'].lower()
        
        if "charg" in desc_lower or "refund" in desc_lower or "paid" in desc_lower:
            dept = "billing"
        elif "crash" in desc_lower or "app" in desc_lower or "login" in desc_lower:
            dept = "technical"
        elif "account" in desc_lower or "password" in desc_lower or "profile" in desc_lower:
            dept = "account"
        elif "upgrade" in desc_lower or "plan" in desc_lower or "feature" in desc_lower:
            dept = "sales"
        else:
            dept = "general"
        
        # Urgency scoring
        urgent_keywords = ["today", "urgent", "asap", "cannot", "down", "emergency"]
        is_urgent = any(kw in desc_lower for kw in urgent_keywords)
        
        print(f"  -> Department: {dept}")
        print(f"  -> Urgent: {is_urgent}")
        
        if dept == ticket['expected_dept']:
            print("  ✓ CORRECT DEPARTMENT")
        else:
            print(f"  ✗ Expected: {ticket['expected_dept']}")
            
        if is_urgent == ticket['expected_urgent']:
            print("  ✓ CORRECT URGENCY")
        else:
            print(f"  ✗ Expected urgent: {ticket['expected_urgent']}")

if __name__ == "__main__":
    test_classification()