@echo off
Title Student Placement Analysis - Auto Setup & Launch

echo.
echo ============================================================
echo  Student Placement Analysis System
echo  Automatic Dependency Installation & Launch
echo ============================================================
echo.

:: Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH. Please install Python 3.x first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Get Python version
python --version

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo.
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo.
    echo [INFO] Virtual environment already exists.
)

:: Activate virtual environment
echo.
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

:: Upgrade pip
echo.
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo.
echo [INFO] Installing requirements from requirements.txt...
if exist requirements.txt (
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install requirements.
        pause
        exit /b 1
    )
) else (
    echo [WARNING] requirements.txt not found. Skipping dependency installation.
)

:: Launch the application
echo.
echo [INFO] Starting Student Placement Analysis Application...
echo.

:: Start Flask app in background
start /B "" python application.py

:: Wait for app to start (give it 3 seconds to initialize)
timeout /t 3 >nul

:: Additional check: wait for port 5000 to be ready (max 10 seconds)
set /a attempt=0
:wait_loop
netstat -ano | findstr :5000 >nul
if not errorlevel 1 (
    goto port_ready
)
set /a attempt+=1
if %attempt% geq 20 (
    echo [WARNING] App may not be ready yet. Opening browser anyway.
    goto port_ready
)
timeout /t 1 >nul
goto wait_loop

:port_ready
:: Open browser
start "" "http://127.0.0.1:5000"

echo.
echo Application running at: http://127.0.0.1:5000
echo Default login credentials:
echo   Admin: admin / admin123
echo   Student: student1 / student123
echo.
echo The application is running in the background.
echo To stop it, close this window or look for the Python console window.
echo ============================================================
echo.

:: Keep window open so user can see output and stop if needed
pause