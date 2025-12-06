@echo off
echo Starting Remote Control Server (Host Computer)...
echo.
echo This computer will be controlled remotely via Replit relay
echo Keep this window open while being controlled
echo Press Ctrl+C to stop the server
echo.
echo Enter your Replit relay URL (e.g., ws://your-repl.repl.co:8765)
echo Or press Enter to test locally (ws://localhost:8765)
echo.
python server.py
pause
