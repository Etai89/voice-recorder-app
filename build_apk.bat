@echo off
echo Voice Recorder APK Builder
echo =========================

echo.
echo This script will build an APK file for the Voice Recorder app.
echo.
echo Prerequisites:
echo - Python 3.7 or higher
echo - Java 8 or higher
echo - Internet connection (for downloading Android SDK/NDK)
echo.

set /p continue="Do you want to continue? (y/n): "
if /i "%continue%" neq "y" (
    echo Build cancelled.
    pause
    exit /b 1
)

echo.
echo Starting build process...
echo.

python build_apk.py

echo.
echo Build process finished.
pause