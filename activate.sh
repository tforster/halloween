#!/bin/bash
# Quick activation helper for Python virtual environment
# Usage: source activate.sh (or . activate.sh)

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
    echo "  Python: $(which python)"
    echo "  Version: $(python --version)"
    echo ""
    echo "Run 'deactivate' when done"
else
    echo "Error: venv/ directory not found"
    echo "Create it with: python3.13 -m venv venv"
    return 1
fi
