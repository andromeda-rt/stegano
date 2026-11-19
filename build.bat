@echo off
title ElectroBlue Stego - Build
echo ========================================
echo   ElectroBlue Stego - Build Script
echo   Author: AndromedaHK
echo ========================================
echo.

echo [1/3] Installing dependencies...
pip install customtkinter Pillow pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo [2/3] Building single .exe (this may take a minute)...
pyinstaller --onefile --windowed --name "ElectroBlueStego" --clean stego_app.py
if errorlevel 1 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo [3/3] Done!
echo.
echo ========================================
echo   Executable created:
echo   dist\ElectroBlueStego.exe
echo ========================================
echo.
pause
