#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Set the debug flag
export PERSONAL_ASSISTANT_DEBUG=true

# Run the main application
python src/main.py
