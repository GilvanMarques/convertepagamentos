@echo off
REM Script para instalar dependências do projeto (Windows)

echo 🔧 Instalando dependências do Gerador CNAB 240...
echo.

REM Verifica se está em ambiente virtual
if exist "venv\Scripts\activate.bat" (
    echo 📦 Ambiente virtual encontrado. Ativando...
    call venv\Scripts\activate.bat
)

REM Instala dependências
echo 📥 Instalando pacotes do requirements.txt...
pip install -r requirements.txt

echo.
echo ✅ Dependências instaladas com sucesso!
echo.
echo 📋 Pacotes instalados:
pip list | findstr /i "pandas openpyxl PyYAML streamlit"

echo.
echo 🚀 Para executar a aplicação Streamlit:
echo    streamlit run app\streamlit_app.py
echo.

pause

