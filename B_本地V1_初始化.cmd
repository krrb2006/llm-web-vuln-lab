@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  python tools\b_local_analysis.py init
) else (
  py -3 tools\b_local_analysis.py init
)
pause
