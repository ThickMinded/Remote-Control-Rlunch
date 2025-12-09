@echo off
echo ======================================================================
echo Remote Control Client - Heroku Mode
echo ======================================================================
echo.
echo Checking requirements...
python -m pip install -q websockets==12.0 pyautogui pillow mss pyperclip pynput 2>nul
echo.
echo Use this to control a remote computer via Heroku relay
echo Automatically connecting to: wss://obscure-crag-09189-c525dbc46d88.herokuapp.com
echo Target Server: my_computer
echo.
echo ======================================================================
echo.
python client.py
pause
