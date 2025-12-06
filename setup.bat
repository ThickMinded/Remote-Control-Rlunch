@echo off
echo ========================================
echo Remote Control Software - Setup
echo ========================================
echo.

echo Installing Python dependencies...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from python.org
    pause
    exit /b 1
)

echo Python found. Installing required packages...
echo.

pip install --user websockets pyautogui Pillow mss

if errorlevel 1 (
    echo.
    echo WARNING: Some packages may have failed to install
    echo This is normal if you already have them installed
    echo.
) else (
    echo.
    echo ========================================
    echo Installation Complete!
    echo ========================================
    echo.
)

echo You can now run:
echo   - server.py (on the computer to be controlled)
echo   - client.py (on the controlling computer)
echo.

pause
