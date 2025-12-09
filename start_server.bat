@echo off
echo ======================================================================
echo Remote Control Server - Heroku Mode
echo ======================================================================
echo.
echo Checking requirements...
python -m pip install -q websockets==12.0 pyautogui pillow mss pyperclip pynput 2>nul
echo.
echo This computer will be controlled remotely via Heroku relay
echo Automatically connecting to: wss://obscure-crag-09189-c525dbc46d88.herokuapp.com
echo.
echo Keep this window open while being controlled
echo Press Ctrl+C to stop the server
echo.
echo ======================================================================
echo.
python server.py
pause
