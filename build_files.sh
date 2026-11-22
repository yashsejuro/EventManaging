#!/bin/bash
set -e
echo "BUILD START"

if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

echo "Installing dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

echo "Collecting static files..."
$PYTHON_CMD manage.py collectstatic --noinput --clear

echo "BUILD END"
