@echo off
echo ========================================
echo    INSTALADOR DO STEAM SCRAPER
echo ========================================
echo.

echo Verificando se Python esta instalado...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao esta instalado!
    echo Por favor, instale Python 3.8+ primeiro
    echo Visite: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python encontrado!
echo.

echo Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao instalar dependencias!
    echo Tente executar manualmente: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ========================================
echo    INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Para usar o scraper basico:
echo   python exemplo_uso.py
echo.
echo Para usar o scraper avancado:
echo   python exemplo_avancado.py
echo.
echo Para testar a instalacao:
echo   python teste_scraper.py
echo.
echo Pressione qualquer tecla para sair...
pause >nul
