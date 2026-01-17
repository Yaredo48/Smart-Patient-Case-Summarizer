#!/bin/bash

# Quick script to register a test user via API

echo "🔐 Creating test user..."

# Wait a moment for backend to be ready
sleep 2

# Register test user
response=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@test.com",
    "password": "password123",
    "full_name": "Dr. Test User",
    "role": "doctor"
  }')

# Check if successful
if echo "$response" | grep -q "email"; then
    echo "✅ Test user created successfully!"
    echo ""
    echo "================================================"
    echo "🔑 LOGIN CREDENTIALS:"
    echo "================================================"
    echo "📧 Email: doctor@test.com"
    echo "🔑 Password: password123"
    echo "================================================"
    echo ""
    echo "Go to: http://localhost:5173/login"
else
    echo "ℹ️  User might already exist or backend isn't ready"
    echo "📝 Manual Registration:"
    echo "   Go to: http://localhost:5173/register"
    echo "   Use: doctor@test.com / password123"
fi
