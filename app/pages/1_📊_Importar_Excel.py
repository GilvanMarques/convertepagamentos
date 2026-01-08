"""
Página de Importação de Excel - Gerador CNAB 240
Permite fazer upload e visualizar o arquivo Excel de pagamentos
"""
import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

# Verifica dependências
try:
    import pandas as pd
except ImportError:
    st.error("""
    ❌ **Módulo pandas não encontrado!**
    
    Por favor, instale as dependências executando:
    ```bash
    pip install -r requirements.txt
    ```
    """)
    st.stop()

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.title("📊 Importar Excel")
st.markdown("Faça upload do arquivo Excel com os dados dos pagamentos.")

# Verifica se a configuração foi feita
if 'config' not in st.session_state or st.session_state.config is None:
    st.warning("⚠️ Configure primeiro os dados da empresa na página **Configuração**.")
    st.info("💡 Use o menu lateral para navegar até a página de Configuração.")
    st.stop()

# Inicializa pagamentos se não existir
if 'pagamentos' not in st.session_state:
    st.session_state.pagamentos = None
if 'pagamentos_df' not in st.session_state:
    st.session_state.pagamentos_df = None

# Upload do arquivo
st.subheader("📁 Upload do Arquivo Excel")

uploaded_file = st.file_uploader(
    "Selecione o arquivo Excel (.xlsx ou .xls)",
    type=['xlsx', 'xls'],
    help="O arquivo deve conter as colunas obrigatórias conforme especificado abaixo"
)

# Informações sobre o formato esperado
with st.expander("📋 Formato Esperado do Excel", expanded=False):
    st.markdown("""
    ### Colunas Obrigatórias:
    
    - **id_pagamento**: Identificador único do pagamento
    - **valor**: Valor do pagamento (numérico, ex: 100.50)
    - **data_pagamento**: Data do pagamento (formato data)
    - **nome_favorecido**: Nome do favorecido (máx. 30 caracteres)
    - **tipo_pessoa**: F (Física) ou J (Jurídica)
    - **cpf_cnpj**: CPF (11 dígitos) ou CNPJ (14 dígitos), apenas números
    - **tipo_pagamento**: PIX, TED ou DOC
    
    ### Colunas para PIX:
    - **tipo_chave_pix**: CPF, CNPJ, EMAIL, TELEFONE ou ALEATORIA
    - **chave_pix**: Chave PIX (conforme o tipo)
    - **txid**: TXID (opcional)
    
    ### Colunas para TED/DOC:
    - **banco_favorecido**: Código do banco (3 dígitos)
    - **agencia_favorecido**: Agência (5 dígitos)
    - **digito_agencia_favorecido**: Dígito da agência (opcional)
    - **conta_favorecido**: Conta (até 12 dígitos)
    - **digito_conta_favorecido**: Dígito da conta (obrigatório)
    - **tipo_conta**: 1 (Corrente) ou 2 (Poupança)
    - **finalidade_ted**: Código da finalidade TED (5 dígitos, padrão: 00001)
    - **aviso_favorecido**: 0 (não avisar) ou 1 (avisar)
    """)

if uploaded_file is not None:
    try:
        # Lê o arquivo Excel
        df = pd.read_excel(uploaded_file, sheet_name=0)
        
        # Normaliza nomes das colunas
        df.columns = df.columns.str.strip().str.lower()
        
        # Exibe informações do arquivo
        st.success(f"✅ Arquivo carregado com sucesso! {len(df)} registro(s) encontrado(s).")
        
        # Mostra colunas encontradas
        st.subheader("📋 Colunas Encontradas")
        colunas_encontradas = list(df.columns)
        colunas_obrigatorias = [
            'id_pagamento', 'valor', 'data_pagamento', 'nome_favorecido',
            'tipo_pessoa', 'cpf_cnpj', 'tipo_pagamento'
        ]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Colunas obrigatórias:**")
            for col in colunas_obrigatorias:
                if col in colunas_encontradas:
                    st.markdown(f"✅ {col}")
                else:
                    st.markdown(f"❌ {col} (faltando)")
        
        with col2:
            st.markdown("**Outras colunas encontradas:**")
            outras_colunas = [c for c in colunas_encontradas if c not in colunas_obrigatorias]
            if outras_colunas:
                for col in outras_colunas:
                    st.markdown(f"• {col}")
            else:
                st.markdown("_Nenhuma_")
        
        # Processa os dados
        st.divider()
        st.subheader("🔄 Processando Dados")
        
        with st.spinner("Processando pagamentos..."):
            pagamentos = []
            
            for index, row in df.iterrows():
                # Trata data_pagamento
                data_pagamento = row.get('data_pagamento', '')
                if pd.notna(data_pagamento):
                    if isinstance(data_pagamento, datetime):
                        data_pagamento = data_pagamento.strftime('%Y-%m-%d')
                    else:
                        data_pagamento = str(data_pagamento).strip()
                else:
                    data_pagamento = ''
                
                # Trata data_vencimento
                data_vencimento = row.get('data_vencimento', '')
                if pd.notna(data_vencimento):
                    if isinstance(data_vencimento, datetime):
                        data_vencimento = data_vencimento.strftime('%Y-%m-%d')
                    else:
                        data_vencimento = str(data_vencimento).strip()
                else:
                    data_vencimento = ''
                
                # Limpa valores numéricos
                def clean_numeric(value):
                    if pd.isna(value):
                        return ''
                    value_str = str(value).replace('.0', '').strip()
                    return value_str
                
                pagamento = {
                    'tipo_pagamento': str(row.get('tipo_pagamento', 'PIX')).strip().upper() if pd.notna(row.get('tipo_pagamento')) else 'PIX',
                    'id_pagamento': str(row.get('id_pagamento', '')).strip() if pd.notna(row.get('id_pagamento')) else '',
                    'data_pagamento': data_pagamento,
                    'valor': float(row.get('valor', 0)) if pd.notna(row.get('valor')) else 0.0,
                    'nome_favorecido': str(row.get('nome_favorecido', '')).strip() if pd.notna(row.get('nome_favorecido')) else '',
                    'tipo_pessoa': str(row.get('tipo_pessoa', 'F')).strip().upper() if pd.notna(row.get('tipo_pessoa')) else 'F',
                    'cpf_cnpj': clean_numeric(row.get('cpf_cnpj', '')),
                    # Campos PIX
                    'tipo_chave_pix': str(row.get('tipo_chave_pix', '')).strip().upper() if pd.notna(row.get('tipo_chave_pix')) else '',
                    'chave_pix': clean_numeric(row.get('chave_pix', '')),
                    'txid': str(row.get('txid', '')).strip() if pd.notna(row.get('txid')) else '',
                    # Campos TED/DOC
                    'banco_favorecido': clean_numeric(row.get('banco_favorecido', '')),
                    'agencia_favorecido': clean_numeric(row.get('agencia_favorecido', '')),
                    'digito_agencia_favorecido': clean_numeric(row.get('digito_agencia_favorecido', '')),
                    'conta_favorecido': clean_numeric(row.get('conta_favorecido', '')),
                    'digito_conta_favorecido': clean_numeric(row.get('digito_conta_favorecido', '')),
                    'tipo_conta': clean_numeric(row.get('tipo_conta', '1')),
                    'finalidade_ted': clean_numeric(row.get('finalidade_ted', '00001')),
                    'aviso_favorecido': int(row.get('aviso_favorecido', 0)) if pd.notna(row.get('aviso_favorecido')) else 0,
                    # Campos adicionais
                    'descricao_pagamento': str(row.get('descricao_pagamento', '')).strip() if pd.notna(row.get('descricao_pagamento')) else '',
                    'data_vencimento': data_vencimento,
                }
                
                pagamentos.append(pagamento)
            
            # Salva no session_state
            st.session_state.pagamentos = pagamentos
            st.session_state.pagamentos_df = df
            
            st.success(f"✅ {len(pagamentos)} pagamento(s) processado(s) com sucesso!")
        
        # Estatísticas
        st.divider()
        st.subheader("📊 Estatísticas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_pagamentos = len(pagamentos)
        total_valor = sum(p.get('valor', 0) for p in pagamentos)
        
        tipos = {}
        for p in pagamentos:
            tipo = p.get('tipo_pagamento', 'PIX')
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        with col1:
            st.metric("Total de Pagamentos", total_pagamentos)
        
        with col2:
            st.metric("Valor Total", f"R$ {total_valor:,.2f}")
        
        with col3:
            st.metric("Tipos de Pagamento", len(tipos))
        
        with col4:
            tipos_str = ", ".join([f"{k}: {v}" for k, v in tipos.items()])
            st.metric("Distribuição", tipos_str[:20] + "..." if len(tipos_str) > 20 else tipos_str)
        
        # Prévia dos dados
        st.divider()
        st.subheader("👀 Prévia dos Dados")
        
        # Cria DataFrame para exibição
        df_display = df.copy()
        st.dataframe(df_display, width="stretch", height=400)
        
        # Botão para limpar
        if st.button("🗑️ Limpar Dados", width="stretch"):
            st.session_state.pagamentos = None
            st.session_state.pagamentos_df = None
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {str(e)}")
        st.exception(e)

else:
    st.info("👆 Faça upload do arquivo Excel para começar.")

