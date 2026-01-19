@echo off
setlocal ENABLEDELAYEDEXPANSION
REM DeepKrak3n startup - one command to launch backend + frontend

title deepkrak3n - Username Checker
cd /d "%~dp0"

for %%I in ("%cd%\..") do set ROOT_DIR=%%~fI
set FRONTEND_DIR=%cd%
set BACKEND_DIR=%cd%\backend
set PYTHON_EXE=%ROOT_DIR%\.venv\Scripts\python.exe
set API_URL=http://127.0.0.1:8000
set NEXT_PUBLIC_API_BASE=%API_URL%

echo ========================================
echo     deepkrak3n - Username Checker
echo ========================================
echo API: %API_URL%
echo Frontend dir: %FRONTEND_DIR%
echo Backend dir: %BACKEND_DIR%
echo ----------------------------------------

REM Ensure shared venv at repo root (preferred so we don't need py launcher)
if not exist "%PYTHON_EXE%" (
	echo [backend] Creating venv at %ROOT_DIR%\.venv ...
	python -m venv "%ROOT_DIR%\.venv" 2>nul
)
if not exist "%PYTHON_EXE%" (
	echo [backend] python -m venv failed, trying py -3 ...
	py -3 -m venv "%ROOT_DIR%\.venv" 2>nul
)
if not exist "%PYTHON_EXE%" (
	echo [backend] ERROR: Could not create Python venv. Install Python 3.x and rerun.
	exit /b 1
)

echo [backend] Installing requirements (pip) ...
pushd "%BACKEND_DIR%"
"%PYTHON_EXE%" -m pip install -r requirements.txt >nul
popd

REM Ensure node_modules
if not exist "%FRONTEND_DIR%\node_modules" (
	echo [frontend] Installing npm dependencies...
	pushd "%FRONTEND_DIR%"
	npm install >nul
	popd
)

REM Start backend (separate window, using shared venv python)
set BACKEND_CMD=cd /d "%BACKEND_DIR%" ^&^& "%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
echo [backend] Starting FastAPI on %API_URL% ...
REM /k keeps the window open so crash logs stay visible
start "deepkrak3n-backend" cmd /k "%BACKEND_CMD%"

REM Wait briefly for backend health before starting frontend
echo [backend] Waiting for API to respond...
powershell -NoLogo -NoProfile -Command "for ($i=0; $i -lt 20; $i++) { try { $r = Invoke-WebRequest -UseBasicParsing %API_URL%/health -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Seconds 1 }; exit 1"
if errorlevel 1 (
	echo [backend] WARNING: API did not respond on %API_URL% yet. Check the backend window for errors.
)

REM Start frontend (current window)
echo [frontend] Starting Next.js dev server...
cd /d "%FRONTEND_DIR%"
npm run dev -- --port 3000

endlocal
