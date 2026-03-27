@echo off
echo ====================================
echo  AAB to APK Converter - Build .exe
echo ====================================
echo.

REM Check Python (py launcher)
py -3 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Install dependencies
echo [1/3] Installing dependencies...
py -3 -m pip install customtkinter pyinstaller
echo.

REM Build .exe
echo [2/3] Building .exe with bundletool.jar bundled inside...
py -3 -m PyInstaller --onefile --windowed ^
    --add-data "bundletool.jar;." ^
    --name "AAB2APK" ^
    --clean ^
    aab_converter.py
echo.

echo [3/3] Build complete!
echo.
echo ====================================
echo  Output: dist\AAB2APK.exe
echo ====================================
echo.
echo NOTE: 
echo   - Copy AAB2APK.exe anywhere and run it.
echo   - bundletool.jar is already bundled inside .exe
echo   - Java JRE must be installed on the target machine.
echo.
pause
