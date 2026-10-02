#!/bin/bash
# Test script for Ticket Analysis API

echo "Testing Ticket Analysis API..."

# Wait for API to be ready
echo "Waiting for API to be ready..."
until curl -s http://localhost:8000/health | grep -q "healthy"; do
  sleep 2
done
echo "API is ready!"

echo ""
echo "=== Test 1: Health Check ==="
curl -s http://localhost:8000/health | jq

echo ""
echo "=== Test 2: Example Ticket ==="
echo "Example ticket:"
curl -s http://localhost:8000/tickets/example | jq

echo ""
echo "=== Test 3: Billing Duplicate Charge ==="
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "id": "TKT-001",
    "description": "I was charged twice for my subscription this month. Please refund one of the charges. I need this resolved today.",
    "user_id": "USR-12345",
    "timestamp": "2024-01-15T14:30:00Z"
  }' | jq

echo ""
echo "=== Test 4: Technical Issue ==="
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "id": "TKT-002",
    "description": "My app crashed during checkout and I cannot complete my purchase on any device.",
    "user_id": "USR-67890",
    "timestamp": "2024-01-15T15:00:00Z"
  }' | jq

echo ""
echo "=== Test 5: Account Access Issue ==="
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "id": "TKT-003",
    "description": "I cannot log into my account after resetting my password. The page keeps saying invalid credentials.",
    "user_id": "USR-11111",
    "timestamp": "2024-01-15T16:00:00Z"
  }' | jq

echo ""
echo "=== Test 6: Sales Inquiry ==="
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "id": "TKT-004",
    "description": "What features are included in the premium plan? How much does it cost?",
    "user_id": "USR-22222",
    "timestamp": "2024-01-15T10:00:00Z"
  }' | jq

echo ""
echo "=== Test 7: Batch Analysis ==="
curl -s -X POST http://localhost:8000/analyze-batch \
  -H "Content-Type: application/json" \
  -d '[
    {
      "id": "BATCH-001",
      "description": "I need a refund for my duplicate charge from yesterday.",
      "user_id": "USR-12345",
      "timestamp": "2024-01-15T14:30:00Z"
    },
    {
      "id": "BATCH-002",
      "description": "How do I upgrade my plan?",
      "user_id": "USR-67890",
      "timestamp": "2024-01-15T15:00:00Z"
    }
  ]' | jq

echo ""
echo "All tests completed!"