@echo off
echo Building English Fluency Coach executable...

REM Run PyInstaller with necessary flags
pyinstaller --noconfirm ^
    --onedir ^
    --windowed ^
    --name "EnglishFluencyCoach" ^
    --paths "src" ^
    --collect-all PyQt6 ^
    --collect-all faster_whisper ^
    --collect-all ctranslate2 ^
    --collect-all ollama ^
    src/main.py

echo.
echo Build complete! The executable is located in the 'dist/EnglishFluencyCoach' folder.
pause
