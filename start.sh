#!/bin/bash

echo "🛍️ Amazon Deals Finder - Quick Start"
echo "===================================="
echo ""

cd "$(dirname "$0")/backend"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run the app
echo ""
echo "✅ Starting server..."
echo "🌐 Open http://localhost:8000 in your browser"
echo ""
python main.py
