@echo off
setlocal EnableDelayedExpansion

echo ======================================================================
echo    Personal Expense Intelligence & Spending Analyzer - Setup
echo    Day 1 - 90 Days 90 Projects Challenge
echo ======================================================================
echo.

:: 1. Detect Python runtime (prefer 3.12 or py launcher)
echo [1/6] Checking for Python installation...
set PYTHON_CMD=

py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3.12
    goto PYTHON_FOUND
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto PYTHON_FOUND
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto PYTHON_FOUND
)

echo [ERROR] No compatible Python installation found on system PATH.
echo Please install Python 3.10, 3.11, or 3.12 from https://www.python.org/
exit /b 1

:PYTHON_FOUND
echo Found Python via: %PYTHON_CMD%
%PYTHON_CMD% --version

:: 2. Create project-specific virtual environment
echo.
echo [2/6] Configuring virtual environment (.venv)...
if not exist .venv (
    echo Creating virtual environment at .venv...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Existing .venv directory detected.
)

:: 3. Install project dependencies
echo.
echo [3/6] Installing dependencies from requirements.txt...
.\.venv\Scripts\python -m pip install --upgrade pip >nul 2>&1
.\.venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    exit /b 1
)
echo Dependencies installed successfully.

:: 4. Ensure directories exist
echo.
echo [4/6] Initializing local directories...
if not exist data mkdir data
if not exist models mkdir models
if not exist screenshots mkdir screenshots

:: 5. Copy environment file if not present
if not exist .env (
    echo Creating .env configuration from .env.example...
    copy .env.example .env >nul
) else (
    echo Existing .env detected; preserving user configuration.
)

:: 6. Initialize database, sample data & baseline ML model
echo.
echo [5/6] Initializing SQLite database and sample dataset...
.\.venv\Scripts\python -c "from src.database import init_db; init_db(); print('SQLite schema initialized.')"
if not exist data\sample_expenses.csv (
    echo Generating sample transactions...
    .\.venv\Scripts\python scripts\generate_sample_data.py
)

echo.
echo [6/6] Training baseline Machine Learning classifier...
.\.venv\Scripts\python scripts\train_classifier.py
if %errorlevel% neq 0 (
    echo [WARNING] ML training had a warning, will use rule-based fallback.
)

echo.
echo ======================================================================
echo    SETUP COMPLETE! You are ready to run the project.
echo    To launch the dashboard, run:  run.bat
echo    To execute the automated test suite, run: test.bat
echo ======================================================================
echo.
pause
