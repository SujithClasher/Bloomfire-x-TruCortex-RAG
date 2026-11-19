@echo off
echo ========================================================
echo Starting KMP + TruCortex + Bloomfire Backend (Python 3.14)
echo ========================================================
cd /d %~dp0backend

set "PY=C:\Python314\python.exe"

echo Freeing port 8010 if occupied by previous session...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8010 ^| findstr LISTENING') do (
    echo Killing existing process on port 8010 (PID %%a)...
    taskkill /f /pid %%a >nul 2>&1
)

echo Starting FastAPI Server on http://localhost:8010...
"%PY%" -m uvicorn main:app --host 0.0.0.0 --port 8010 --reload
pause
