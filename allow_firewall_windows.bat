@echo off
setlocal
net session >nul 2>&1
if not "%errorlevel%"=="0" (
  echo This script must be run as Administrator.
  echo Right-click allow_firewall_windows.bat and choose "Run as administrator".
  pause
  exit /b 1
)

set "PORT=5000"
if not "%~1"=="" set "PORT=%~1"

echo Allowing LANCloud (TCP %PORT%) on Private and Domain networks...
netsh advfirewall firewall delete rule name="LANCloud" >nul 2>&1
netsh advfirewall firewall add rule name="LANCloud" dir=in action=allow protocol=TCP localport=%PORT% profile=private,domain
if errorlevel 1 (
  echo.
  echo Could not add the firewall rule.
  pause
  exit /b 1
)

echo.
echo Done. Make sure your WiFi network is set to "Private", not "Public".
echo Then open the Network URL printed by app.py on your phone or another PC.
pause
