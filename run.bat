@echo off
REM Windows — run infographic generator
REM Usage: run.bat "Your prompt here"

SET DIR=%~dp0

REM ── Check Python ──────────────────────────────────────────────
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python not found. Opening download page...
    start https://www.python.org/downloads/
    echo Please install Python, check "Add Python to PATH", then re-run this script.
    pause
    exit /b 1
)

REM ── Check replicate package ───────────────────────────────────
python -c "import replicate" >nul 2>&1
IF ERRORLEVEL 1 (
    echo Installing replicate package...
    python -m pip install replicate --quiet
)

python -c "import PIL" >nul 2>&1
IF ERRORLEVEL 1 (
    echo Installing Pillow package...
    python -m pip install Pillow --quiet
)

REM ── Load .env ─────────────────────────────────────────────────
IF NOT EXIST "%DIR%.env" (
    echo ERROR: .env file not found. Create it with: REPLICATE_API_TOKEN=your_token
    pause
    exit /b 1
)

FOR /F "tokens=1,2 delims==" %%A IN (%DIR%.env) DO (
    SET %%A=%%B
)

REM ── Run ───────────────────────────────────────────────────────
IF "%~1"=="" (
    echo Usage: run.bat "Your infographic prompt here"
    pause
    exit /b 1
)

python "%DIR%run.py" --prompt "%~1" %2 %3 %4
pause
