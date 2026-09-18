#!/bin/bash

# Student Placement Analysis - Auto Setup & Launch Script
# For use in Git Bash, Linux, or macOS terminals

echo ""
echo "============================================================"
echo "  Student Placement Analysis System"
echo "  Automatic Dependency Installation & Launch"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python not found. Please install Python 3.x first."
        echo "Download from: https://www.python.org/downloads/"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Show Python version
echo "[INFO] Using: $($PYTHON_CMD --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment."
        exit 1
    fi
else
    echo "[INFO] Virtual environment already exists."
fi

# Activate virtual environment
echo ""
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "[INFO] Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip

# Install requirements
echo ""
echo "[INFO] Installing requirements from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install requirements."
        exit 1
    fi
else
    echo "[WARNING] requirements.txt not found. Skipping dependency installation."
fi

# Function to open URL in default browser based on OS
open_browser() {
    local url="$1"
    case "$(uname -s)" in
        Darwin*)  # macOS
            open "$url"
            ;;
        Linux*)   # Linux
            xdg-open "$url"
            ;;
        CYGWIN*|MINGW*|MSYS*)  # Windows (including Git Bash)
            # Try to use Windows start command via cmd
            cmd //c start "$url"
            ;;
        *)
            echo "[WARNING] Unable to auto-open browser on this OS."
            echo "Please open your browser and navigate to: $url"
            ;;
    esac
}

# Launch the application
echo ""
echo "[INFO] Starting Student Placement Analysis Application..."
echo ""

# Start Flask app in background
$PYTHON_CMD application.py &
FLASK_PID=$!

# Wait for app to start (give it a few seconds)
echo "[INFO] Waiting for application to start..."
sleep 3

# Additional verification: try to connect to the port
echo "[INFO] Verifying application is ready..."
for i in {1..10}; do
    if curl -s http://127.0.0.1:5000 >/dev/null 2>&1; then
        echo "[INFO] Application is ready!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "[WARNING] Application may not be fully ready yet. Opening browser anyway."
    fi
    sleep 1
done

# Open browser
echo ""
echo "[INFO] Opening application in web browser..."
open_browser "http://127.0.0.1:5000"

echo ""
echo "Application running at: http://127.0.0.1:5000"
echo "Default login credentials:"
echo "  Admin: admin / admin123"
echo "  Student: student1 / student123"
echo ""
echo "Press CTRL+C to stop the application"
echo "============================================================"
echo ""

# Wait for the Flask process to complete (when user presses CTRL+C)
wait $FLASK_PID

# Note: When the app stops, the virtual environment will remain activated in this shell session