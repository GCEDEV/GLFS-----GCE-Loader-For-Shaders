@echo off
echo Starting GLFS - Minecraft Bedrock Shader Loader...

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Install/upgrade pip
python -m ensurepip --upgrade > nul 2>&1

REM Install required packages
echo Installing required packages...
python -m pip install --upgrade pip > nul 2>&1
python -m pip install -r requirements.txt > nul 2>&1

REM Change directory and open browser
cd /d "%~dp0"
start "" "http://localhost:5000"

REM Run the application
python src/main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error starting GLFS. Running in debug mode...
    python debug.py
    pause
)
