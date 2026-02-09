#!/bin/bash
# AI Micro Break System - Quick Start Script for macOS/Linux

echo ""
echo "============================================"
echo "AI Micro Break System - Quick Start"
echo "============================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.8 or higher."
    echo "For macOS: brew install python3"
    echo "For Linux: sudo apt install python3 python3-venv"
    exit 1
fi

python3 --version

echo "[1/5] Python found. Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[2/5] Installing dependencies..."
pip install -r config/requirements.txt

echo "[3/5] Creating logs directory..."
mkdir -p logs

echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 - Start Backend:"
echo "  cd backend"
echo "  python3 app.py"
echo ""
echo "Terminal 2 - Serve Frontend:"
echo "  cd frontend"
echo "  python3 -m http.server 9000"
echo ""
echo "Then open your browser and go to: http://localhost:9000"
echo ""
