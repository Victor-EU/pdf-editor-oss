#!/bin/bash

# PDF Editor Frontend Startup Script

echo "================================================"
echo "  PDF Editor - Starting Frontend Server"
echo "================================================"
echo ""

cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

echo "🚀 Starting frontend development server..."
echo "📍 URL: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
