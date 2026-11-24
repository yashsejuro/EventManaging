#!/bin/bash
set -e
echo "BUILD START"

export UV_BREAK_SYSTEM_PACKAGES=true

if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

echo "Installing dependencies..."
if command -v uv &>/dev/null; then
    uv pip install -r requirements.txt --system --break-system-packages || $PYTHON_CMD -m pip install -r requirements.txt --break-system-packages
else
    $PYTHON_CMD -m pip install -r requirements.txt --break-system-packages
fi

echo "Collecting static files..."
$PYTHON_CMD manage.py collectstatic --noinput --clear

echo "BUILD END"
