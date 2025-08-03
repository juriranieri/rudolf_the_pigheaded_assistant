#!/bin/bash
echo "🐍 Setting up Python environment..."
# Create a clean virtual environment
uv venv --clear
echo "📦 Installing dependencies from requirements.txt..."
# Explicitly install packages into the created virtual environment
uv pip install -p .venv/bin/python -r requirements.txt
echo "✅ Setup complete."
