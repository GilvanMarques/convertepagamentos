"""
Aplicação Streamlit - Gerador CNAB 240 Bradesco
Interface web para geração de arquivos de remessa CNAB 240 (TED/DOC e PIX)
"""
import streamlit as st
from pathlib import Path
import sys

# Verifica dependências críticas ANTES de qualquer importação
dependencias_faltando = []

try:
    import yaml
except ImportError:
    dependencias_faltando.append("PyYAML")

try:
    import pandas as pd
except ImportError:
    dependencias_faltando.append("pandas")

try:
    import openpyxl
except ImportError:
    dependencias_faltando.append("openpyxl")

# Se faltar alguma dependência, mostra erro e para
if dependencias_faltando:
    st.error(f"""
    ❌ **Dependências não encontradas: {', '.join(dependencias_faltando)}**
    
    Por favor, instale as dependências executando:
    ```bash
    pip install -r requirements.txt
    ```
    
    Ou use o script de instalação:
    ```bash
    ./instalar_dependencias.sh
    ```
    
    **Dependências necessárias:**
    - pandas>=2.0.0
    - openpyxl>=3.1.0
    - PyYAML>=6.0
    - streamlit>=1.28.0
    """)
    st.stop()

# Adiciona o diretório raiz ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuração da página
st.set_page_config(
    page_title="Gerador CNAB 240 - Bradesco",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhorar a aparência
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-ok {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização do session_state
if 'config' not in st.session_state:
    st.session_state.config = None
if 'pagamentos' not in st.session_state:
    st.session_state.pagamentos = None
if 'validacao_resultado' not in st.session_state:
    st.session_state.validacao_resultado = None
if 'arquivo_gerado' not in st.session_state:
    st.session_state.arquivo_gerado = None

# Carrega automaticamente a configuração padrão do YAML (Configuração é opcional)
if st.session_state.config is None:
    try:
        from src.cnab240.config import load_config

        config_path = Path(__file__).parent.parent / 'config' / 'bradesco.yaml'
        st.session_state.config = load_config(str(config_path))
    except Exception as e:
        st.error(
            "❌ Não foi possível carregar a configuração padrão em `config/bradesco.yaml`.\n\n"
            f"Detalhe: {e}"
        )
        st.stop()

# Header principal
st.markdown('<h1 class="main-header">🏦 Gerador CNAB 240 - Bradesco Multipag</h1>', unsafe_allow_html=True)

# Sidebar com informações
with st.sidebar:
    st.header("ℹ️ Informações")
    st.markdown("""
    **Sistema de Geração de Remessa CNAB 240**
    
    Suporta:
    - 💸 PIX
    - 💰 TED/DOC
    
    **Fluxo de trabalho:**
    1. 📊 Importar Excel
    2. ✅ Validar Dados (na própria página Importar Excel)
    3. 📄 Gerar CNAB
    4. ⚙️ Configuração (opcional)
    """)
    
    st.divider()
    
    # Status do fluxo
    st.subheader("Status do Fluxo")
    
    config_status = "✅" if st.session_state.config else "⏳"
    excel_status = "✅" if st.session_state.pagamentos is not None else "⏳"
    validacao_status = "✅" if st.session_state.validacao_resultado else "⏳"
    geracao_status = "✅" if st.session_state.arquivo_gerado else "⏳"
    
    st.markdown(f"""
    {config_status} Configuração
    
    {excel_status} Importar Excel
    
    {validacao_status} Validação
    
    {geracao_status} Geração
    """)
    
    st.divider()
    
    # Botão para limpar sessão
    if st.button("🔄 Limpar Sessão", width="stretch"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Página inicial
st.markdown("""
## Bem-vindo ao Gerador CNAB 240

Esta aplicação permite gerar arquivos de remessa CNAB 240 para pagamentos via Bradesco Multipag.

### Como usar:

1. **Importar Excel**: Faça upload do arquivo Excel com os pagamentos
2. **Validar**: Verifique se todos os dados estão corretos
3. **Gerar CNAB**: Gere o arquivo de remessa para envio ao banco
4. **Configuração**: (Opcional) Configure os dados da empresa e conta bancária quando necessário

### Requisitos do Excel:

O arquivo Excel deve conter as seguintes colunas obrigatórias:
- `id_pagamento`: Identificador único do pagamento
- `valor`: Valor do pagamento (formato numérico)
- `data_pagamento`: Data do pagamento (formato data)
- `nome_favorecido`: Nome do favorecido
- `cpf_cnpj`: CPF ou CNPJ do favorecido
- `tipo_pagamento`: Tipo de pagamento (PIX, TED, DOC)

Para mais detalhes, consulte a página **Importar Excel**.
""")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <small>Gerador CNAB 240 - Bradesco Multipag | Versão 1.0</small>
</div>
""", unsafe_allow_html=True)

