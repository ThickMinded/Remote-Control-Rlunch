#!/bin/bash

echo "========================================"
echo "Remote Control Software - Setup"
echo "========================================"
echo ""

echo "Installing Python dependencies..."
echo ""

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "Python found. Installing required packages..."
echo ""

# Install packages
python3 -m pip install --user websockets pyautogui Pillow mss

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Installation Complete!"
    echo "========================================"
    echo ""
else
    echo ""
    echo "WARNING: Some packages may have failed to install"
    echo "This is normal if you already have them installed"
    echo ""
fi

echo "You can now run:"
echo "  - python3 server.py (on the computer to be controlled)"
echo "  - python3 client.py (on the controlling computer)"
echo ""

# Make scripts executable
chmod +x server.py client.py 2>/dev/null

echo "Setup complete!"
