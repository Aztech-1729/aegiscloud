@echo off
title Aegis Cloud Startup
echo ===================================================
echo     Starting Aegis Cloud Local Environment...
echo ===================================================
echo.

echo [1/3] Starting Docker databases (Postgres & Redis)...
docker compose up -d postgres redis
echo.

echo [2/3] Starting Python Backend API in a new window...
:: Open a new window for the backend so it doesn't block this script
start "Aegis Backend" cmd /k "cd backend && if not exist .venv (echo Creating virtual environment... && python -m venv .venv) && call .venv\Scripts\activate && echo Installing requirements... && pip install -r requirements.txt && echo Starting FastAPI server... && uvicorn app.main:app --reload --port 8000"

echo [3/3] Starting Next.js Frontend in a new window...
:: Open a new window for the frontend
start "Aegis Frontend" cmd /k "cd frontend && echo Installing NPM packages... && npm install && echo Starting Next.js development server... && npm run dev"

echo.
echo ===================================================
echo  All services are starting up! 
echo  - Backend will be available at: http://localhost:8000
echo  - Frontend will be available at: http://localhost:3000
echo ===================================================
echo You can close this window at any time.
pause
