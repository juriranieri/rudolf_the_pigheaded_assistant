#!/bin/bash
echo "🐍 Setting up Python environment..."
uv venv
source venv/bin/activate
echo "📦 Installing dependencies from requirements.txt..."
uv pip install -r requirements.txt
echo "✅ Setup complete."