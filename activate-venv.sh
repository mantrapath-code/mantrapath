#!/bin/bash
# Quick activation script for MantraPath virtual environment

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo "Run ./setup-venv.sh first to create it"
    exit 1
fi

echo "🐍 Activating MantraPath virtual environment..."
source "$VENV_DIR/bin/activate"
echo "✅ Virtual environment activated"
echo "Python: $(which python)"
echo "Pip: $(which pip)"

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT/backend/shared:$PYTHONPATH"
export MANTRAPATH_ROOT="$PROJECT_ROOT"

echo "🔧 Environment variables set:"
echo "   PYTHONPATH includes: $PROJECT_ROOT/backend/shared"
echo "   MANTRAPATH_ROOT: $MANTRAPATH_ROOT"
echo ""
echo "🚀 Ready to run MantraPath backend services!"
echo "To deactivate, run: deactivate"
