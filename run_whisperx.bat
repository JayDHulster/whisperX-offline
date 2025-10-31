@echo off
:: Activate your Python environment
call wxs_env\Scripts\activate

:: Run the PowerShell GUI
powershell -NoProfile -ExecutionPolicy Bypass -File "run_whisperx_gui.ps1"
pause
