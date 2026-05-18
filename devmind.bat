@echo off
echo [DevMind] Checking Python environment...

if not exist "venv\Scripts\activate.bat" (
    echo [DevMind] Creating virtual environment...
    python -m venv venv
)

echo [DevMind] Activating virtual environment...
call venv\Scripts\activate.bat

echo [DevMind] Installing dependencies...
pip install -r requirements.txt --quiet

echo [DevMind] Launching DevMind CLI...
python main.py

pause
