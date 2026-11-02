@echo off
setlocal
cd /d "%~dp0"
echo VulnLab local launcher
echo Working directory: %CD%
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run-native.ps1" %*
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if not "%EXIT_CODE%"=="0" (
  echo VulnLab failed to start. Read the error above.
  pause
)
exit /b %EXIT_CODE%
