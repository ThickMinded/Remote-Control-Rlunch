@echo off
REM Create VBS script to launch server completely hidden
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\start_server_hidden.vbs"
echo WshShell.Run "pythonw ""%~dp0server.py""", 0, False >> "%TEMP%\start_server_hidden.vbs"
REM Execute VBS script and delete it
cscript //nologo "%TEMP%\start_server_hidden.vbs"
del "%TEMP%\start_server_hidden.vbs"
exit
