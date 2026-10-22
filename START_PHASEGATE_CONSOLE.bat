@echo off
cd /d "%~dp0"
echo DPN PHASEGATE // SYNTHETIC DEMONSTRATION, NOT REAL INSTRUMENTATION
where py >nul 2>nul
if %errorlevel%==0 (
 start "" "http://127.0.0.1:8765"
 py -3 -m console.server --port 8765
) else (
 where python >nul 2>nul
 if errorlevel 1 (
  echo Python 3.12 or later is required.
  pause
  exit /b 1
 )
 start "" "http://127.0.0.1:8765"
 python -m console.server --port 8765
)
pause
