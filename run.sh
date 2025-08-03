#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Ensure the debug flag is not set
unset PERSONAL_ASSISTANT_DEBUG

# Run the main application
python src/main.py
