#!/bin/bash
echo "[DevMind] Checking Python environment..."

if [ ! -d "venv" ]; then
    echo "[DevMind] Creating virtual environment..."
    python3 -m venv venv
fi

echo "[DevMind] Activating virtual environment..."
source venv/bin/activate

echo "[DevMind] Installing dependencies..."
pip install -r requirements.txt --quiet

echo "[DevMind] Launching DevMind CLI..."
python main.py
