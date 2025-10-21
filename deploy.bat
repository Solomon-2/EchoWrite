@echo off
echo EchoWrite AI - Quick Deploy Script
echo.

:: Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

:: Check if .env file exists
if not exist ".env" (
    echo Creating .env file from template...
    copy ".env.example" ".env" >nul
    echo.
    echo IMPORTANT: Please edit the .env file and add your GROQ_API_KEY
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)

:: Check if GROQ_API_KEY is set in .env
findstr /C:"GROQ_API_KEY=your_groq_api_key_here" .env >nul
if %errorlevel% equ 0 (
    echo.
    echo WARNING: Please update your GROQ_API_KEY in the .env file
    echo Current value appears to be the default placeholder.
    echo.
    pause
)

echo Building and starting EchoWrite...
docker-compose up --build -d

if %errorlevel% equ 0 (
    echo.
    echo ✅ EchoWrite is starting up!
    echo.
    echo 🌐 Frontend (Streamlit): http://localhost:8501
    echo 🔗 Backend API: http://localhost:8000
    echo 📚 API Documentation: http://localhost:8000/docs
    echo.
    echo To view logs: docker-compose logs -f
    echo To stop: docker-compose down
    echo.
) else (
    echo.
    echo ❌ Failed to start EchoWrite
    echo Check the error messages above.
    echo.
)

pause