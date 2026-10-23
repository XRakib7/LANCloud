@echo off
setlocal
cd /d "%~dp0"

set "PY=py"
where py >nul 2>nul
if errorlevel 1 set "PY=python"

%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python was not found.
  echo Install Python 3.8 or newer from https://www.python.org/downloads/
  echo and tick "Add Python to PATH" during installation.
  pause
  exit /b 1
)

%PY% -c "import flask" >nul 2>nul
if errorlevel 1 (
  echo Installing dependencies...
  %PY% -m pip install -r requirements.txt
  if errorlevel 1 (
    echo.
    echo Dependency installation failed. Check your internet connection and Python version.
    pause
    exit /b 1
  )
)

echo.
echo Starting LANCloud...
echo Keep this window open while you use the file manager.
echo Press Ctrl+C to stop.
echo.
%PY% app.py
pause
