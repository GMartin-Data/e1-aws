#!/bin/bash

# --- VARIABLES TO CONFIGURE ---
# Full absolute path to the project's root directory
PROJECT_ROOT="/home/greg/certif/e1-aws"

# Full absolute path to the Python's executable from the venv
PYTHON_EXEC="$PROJECT_ROOT/.venv/bin/python"

# Full absolute path to the local_uploader.py script
UPLOADER_SCRIPT="$PROJECT_ROOT/local_uploader.py"


# --- Script Execution Logic
# 1. Navigate to the project root directory
cd "$PROJECT_ROOT" || { echo "Failed to change directory to $PROJECT_ROOT" >&2; exit 1; }

# 2. Execute the Python script with the correct interpreter
exec "$PYTHON_EXEC" "$UPLOADER_SCRIPT"