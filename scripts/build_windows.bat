@echo off
REM Build PaperForge.exe (Windows, GUI + CLI dual mode, custom icon).
REM Output: dist\paperforge.exe

cd /d "%~dp0\.."

python -m pip install --upgrade pip
pip install -e .[dev]

python scripts\build_icon.py
if errorlevel 1 goto :error

pyinstaller paperforge.spec --noconfirm
if errorlevel 1 goto :error

echo.
echo Done. Binary at: dist\paperforge.exe
goto :eof

:error
echo.
echo Build failed.
exit /b 1
