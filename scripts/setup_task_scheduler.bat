@echo off
REM ============================================
REM FenoFin Dependency Monitor - Task Scheduler
REM ============================================
REM Run this script as Administrator to set up
REM weekly dependency monitoring.

set PROJECT_DIR=C:\Users\FolkertFeenstra\PycharmProjects\dependency-monitor
set PYTHON=%PROJECT_DIR%\.venv\Scripts\python.exe

REM Create the scheduled task
schtasks /create /tn "FenoFin Dependency Monitor" ^
  /tr "\"%PYTHON%\" \"%PROJECT_DIR%\manage.py\" run_monitor" ^
  /sc weekly /d MON /st 09:00 ^
  /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Task scheduled successfully!
    echo   Name: FenoFin Dependency Monitor
    echo   Schedule: Every Monday at 09:00
    echo   Command: python manage.py run_monitor
    echo.
    echo To test manually:
    echo   schtasks /run /tn "FenoFin Dependency Monitor"
    echo.
    echo To remove:
    echo   schtasks /delete /tn "FenoFin Dependency Monitor" /f
) else (
    echo.
    echo ERROR: Failed to create scheduled task.
    echo Make sure you run this script as Administrator.
)

pause
