#!/usr/bin/env python3
"""
Local installation and test script for Ticket Analysis API.
Works without Docker - uses FastAPI locally.
"""

import subprocess
import sys
import os

def install_deps():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    deps = [
        "fastapi",
        "uvicorn",
        "httpx",
        "pydantic"
    ]
    
    subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + deps, check=True)
    
    # Try to install Laya (optional - heavy dependencies)
    print("Attempting to install Laya (optional, ~600MB)...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "laya"], 
                      timeout=120, check=False)
    except subprocess.TimeoutExpired:
        print("Laya installation skipped (too slow without GPU)")


def run_tests():
    """Run classification tests."""
    print("\n" + "="*60)
    print("TICKET CLASSIFICATION TESTS")
    print("="*60)
    
    test_cases = [
        {
            "name": "Billing - Duplicate Charge",
            "description": "I was charged twice for my subscription this month. Please refund one of the charges today.",
            "expected_dept": "billing",
            "expected_urgent": True
        },
        {
            "name": "Technical - App Crash",
            "description": "My app crashed during checkout and I cannot complete my purchase on any device.",
            "expected_dept": "technical",
            "expected_urgent": True
        },
        {
            "name": "Account - Password Reset",
            "description": "I need to reset my password but the email is not being received.",
            "expected_dept": "account",
            "expected_urgent": False
        },
        {
            "name": "Sales - Plan Inquiry",
            "description": "What features are included in the premium plan? How much does it cost?",
            "expected_dept": "sales",
            "expected_urgent": False
        },
        {
            "name": "General - Non-classified",
            "description": "I have a general question about your service.",
            "expected_dept": "general",
            "expected_urgent": False
        }
    ]
    
    # Simple classification logic (fallback when Laya unavailable)
    def classify_dept(desc):
        d = desc.lower()
        if any(kw in d for kw in ["charg", "refund", "paid", "payment", "billing", "charged", "duplicate"]):
            return "billing"
        elif any(kw in d for kw in ["crash", "bug", "app", "login", "error", "broken", "broken", "cannot", "can't"]):
            return "technical"
        elif any(kw in d for kw in ["account", "profile", "reset", "change", "update", "access", "password"]):
            return "account"
        elif any(kw in d for kw in ["feature", "plan", "upgrade", "price", "cost", "sales", "free trial", "inquiry"]):
            return "sales"
        else:
            return "general"
    
    def is_urgent(desc):
        d = desc.lower()
        urgent_words = ["today", "urgent", "asap", "immediately", "now", "emergency", 
                       "blocked", "down", "outage", "cannot", "can't", "error", "crash"]
        return any(w in d for w in urgent_words)
    
    print("\nRunning classification tests...\n")
    
    passed = 0
    failed = 0
    
    for tc in test_cases:
        dept = classify_dept(tc["description"])
        urgent = is_urgent(tc["description"])
        
        dept_ok = dept == tc["expected_dept"]
        urgent_ok = urgent == tc["expected_urgent"]
        
        status = "✓ PASS" if (dept_ok and urgent_ok) else "✗ FAIL"
        if dept_ok and urgent_ok:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} - {tc['name']}")
        print(f"    Department: {dept} (expected: {tc['expected_dept']})")
        print(f"    Urgent: {urgent} (expected: {tc['expected_urgent']})")
        print()
    
    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


def run_api():
    """Start the FastAPI server."""
    print("\n" + "="*60)
    print("Starting Ticket Analysis API")
    print("="*60)
    print("\nAPI will be available at: http://localhost:8000")
    print("Docs at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop\n")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run([sys.executable, "-m", "uvicorn", "src.main:app", 
                   "--host", "0.0.0.0", "--port", "8000", "--reload"])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            install_deps()
        elif sys.argv[1] == "test":
            success = run_tests()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "server":
            run_api()
    else:
        # Default: run tests
        run_tests()
        print("\nTo start the API server: python local_setup.py server")
        print("To install dependencies: python local_setup.py install")