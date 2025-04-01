@echo off
REM LocaLocaLocalize Installation Script for Windows

echo === LocaLocaLocalize Installation ===
echo This script will set up the LocaLocaLocalize tool.

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Using Python %PYTHON_VERSION%

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Install Playwright browsers
echo Installing Playwright browsers...
python -m playwright install chromium

REM Create config from sample if it doesn't exist
if not exist config\config.yaml (
    echo Creating default configuration...
    if not exist config mkdir config
    copy config\config.sample.yaml config\config.yaml
    echo Please edit config\config.yaml to configure the tool.
)

REM Create .env from sample if it doesn't exist
if not exist .env (
    echo Creating environment file...
    copy .env.sample .env
    echo Please edit .env to add your credentials and API keys if needed.
)

REM Create necessary directories
echo Creating necessary directories...
if not exist screenshots mkdir screenshots
if not exist reports mkdir reports
if not exist logs mkdir logs

echo Installation complete!
echo.
echo To start using LocaLocaLocalize:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Edit config\config.yaml to configure your testing needs
echo 3. Run the tool: python src\main.py
echo.
echo Happy localizing!

pause 