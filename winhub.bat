@echo off
:: ============================================================
:: WinHub Launcher — Runs as Administrator automatically
:: Author: ricinus  https://github.com/ricinuss
:: ============================================================

title WinHub — Windows Optimizer

:: Check if running as admin
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo.
    echo  [WinHub] Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Move to script directory
cd /d "%~dp0"

:: Check Python is available
where python >nul 2>&1
if %errorLevel% NEQ 0 (
    echo.
    echo  [ERROR] Python not found. Please install Python 3.11+ from:
    echo          https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Install dependencies silently if needed
pip show colorama >nul 2>&1
if %errorLevel% NEQ 0 (
    echo  [WinHub] Installing dependencies...
    pip install -r requirements.txt --quiet
)

:: Enable virtual terminal (ANSI) processing
reg add "HKCU\Console" /v "VirtualTerminalLevel" /t REG_DWORD /d 1 /f >nul 2>&1

:: Launch WinHub
python main.py %*

if %errorLevel% NEQ 0 (
    echo.
    echo  [WinHub] Exited with error code %errorLevel%
    pause
)
