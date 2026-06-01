Write-Host "Building English Fluency Coach executable..."

# Run PyInstaller with necessary flags
pyinstaller --noconfirm `
    --onedir `
    --windowed `
    --name "EnglishFluencyCoach" `
    --paths "src" `
    --hidden-import views.ui `
    --hidden-import controllers.media_handler `
    --hidden-import controllers.ai_agent `
    --hidden-import controllers.topic_engine `
    --hidden-import models.database `
    --collect-all PyQt6 `
    --collect-all faster_whisper `
    --collect-all ctranslate2 `
    --collect-all ollama `
    --collect-all tokenizers `
    src/main.py

Write-Host "`nBuild complete! The executable is located in the 'dist\EnglishFluencyCoach' folder."
