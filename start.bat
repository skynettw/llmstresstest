@echo off
echo Starting Ollama Stress Test Tool...
echo.
echo Checking if Ollama is running...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Ollama server is not running!
    echo Please start Ollama first by running: ollama serve
    echo.
    pause
    exit /b 1
)

echo Ollama server is running.
echo Starting Flask application...
echo.
echo Open your browser and go to: http://localhost:5001
echo Press Ctrl+C to stop the server.
echo.

python app_simple.py
