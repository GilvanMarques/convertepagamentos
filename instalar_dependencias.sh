#!/bin/bash
# Script para instalar dependências do projeto

echo "🔧 Instalando dependências do Gerador CNAB 240..."
echo ""

# Verifica se está em ambiente virtual
if [ -d "venv" ]; then
    echo "📦 Ambiente virtual encontrado. Ativando..."
    source venv/bin/activate
fi

# Instala dependências
echo "📥 Instalando pacotes do requirements.txt..."
pip install -r requirements.txt

echo ""
echo "✅ Dependências instaladas com sucesso!"
echo ""
echo "📋 Pacotes instalados:"
pip list | grep -E "pandas|openpyxl|PyYAML|streamlit"

echo ""
echo "🚀 Para executar a aplicação Streamlit:"
echo "   streamlit run app/streamlit_app.py"
echo ""




