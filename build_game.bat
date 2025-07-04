@echo off
echo === Створення гри moose_game.exe ===

REM Створення .exe з PyInstaller
pyinstaller --onefile --windowed moose_game.py

echo.
echo === Готово! ===
echo Відкриваємо папку dist...
start dist

pause
