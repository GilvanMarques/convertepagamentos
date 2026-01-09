"""
Página de Importação de Excel - Gerador CNAB 240
Permite fazer upload e visualizar o arquivo Excel de pagamentos
"""
import streamlit as st
from pathlib import Path
import sys
import re
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

try:
    from src.cnab240 import validate
except ImportError as e:
    st.error(f"❌ Erro ao importar módulos: {str(e)}")
    st.info("💡 Certifique-se de que todas as dependências estão instaladas: `pip install -r requirements.txt`")
    st.stop()

st.title("📊 Importar Excel")
st.markdown("Faça upload do arquivo Excel com os dados dos pagamentos.")

# Garante configuração carregada (Configuração é opcional)
if 'config' not in st.session_state or st.session_state.config is None:
    try:
        from src.cnab240.config import load_config

        config_path = Path(__file__).parent.parent.parent / 'config' / 'bradesco.yaml'
        st.session_state.config = load_config(str(config_path))
    except Exception as e:
        st.warning("⚠️ Não foi possível carregar a configuração automaticamente.")
        st.error(f"Detalhe: {e}")
        st.info("💡 Vá até a página **Configuração** para revisar/salvar a configuração.")
        st.stop()

# Inicializa pagamentos se não existir
if 'pagamentos' not in st.session_state:
    st.session_state.pagamentos = None
if 'pagamentos_df' not in st.session_state:
    st.session_state.pagamentos_df = None
if 'validacao_resultado' not in st.session_state:
    st.session_state.validacao_resultado = None

# Upload do arquivo
st.subheader("📁 Upload do Arquivo Excel")

uploaded_file = st.file_uploader(
    "Selecione o arquivo Excel (.xlsx ou .xls)",
    type=['xlsx', 'xls'],
    help="O arquivo deve conter as colunas obrigatórias conforme especificado abaixo"
)

if uploaded_file is not None:
    try:
        # Lê o arquivo Excel
        df = pd.read_excel(uploaded_file, sheet_name=0)
        
        # Normaliza nomes das colunas
        df.columns = df.columns.str.strip().str.lower()
        
        # Funções auxiliares para processamento
        def clean_numeric(value):
            """Limpa valores numéricos removendo .0 e espaços."""
            if pd.isna(value):
                return ''
            value_str = str(value).replace('.0', '').strip()
            return value_str
        
        def normalize_numeric_field(value, length):
            """
            Normaliza campo numérico preenchendo com zeros à esquerda.
            
            Args:
                value: Valor a ser normalizado
                length: Tamanho total desejado
            
            Returns:
                String normalizada com zeros à esquerda
            """
            if pd.isna(value) or value == '':
                return ''
            # Remove caracteres não numéricos
            value_str = re.sub(r'[^0-9]', '', str(value))
            if not value_str:
                return ''
            # Preenche com zeros à esquerda até o tamanho desejado
            return value_str.zfill(length)
        
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
                # Campos TED/DOC (normalizados com zeros à esquerda)
                'banco_favorecido': normalize_numeric_field(row.get('banco_favorecido', ''), 3),
                'agencia_favorecido': normalize_numeric_field(row.get('agencia_favorecido', ''), 5),
                'digito_agencia_favorecido': clean_numeric(row.get('digito_agencia_favorecido', '')),
                'conta_favorecido': clean_numeric(row.get('conta_favorecido', '')),  # Mantém zeros à esquerda originais
                'digito_conta_favorecido': clean_numeric(row.get('digito_conta_favorecido', '')),
                'tipo_conta': normalize_numeric_field(row.get('tipo_conta', '1'), 1),
                'finalidade_ted': normalize_numeric_field(row.get('finalidade_ted', '00001'), 5),
                'aviso_favorecido': int(row.get('aviso_favorecido', 0)) if pd.notna(row.get('aviso_favorecido')) else 0,
                # Campos adicionais
                'descricao_pagamento': str(row.get('descricao_pagamento', '')).strip() if pd.notna(row.get('descricao_pagamento')) else '',
                'data_vencimento': data_vencimento,
            }

            pagamentos.append(pagamento)

        # Salva no session_state
        st.session_state.pagamentos = pagamentos
        st.session_state.pagamentos_df = df

        # Validação automática ao anexar o arquivo
        erros = []
        avisos = []
        validos = []
        for index, pagamento in enumerate(pagamentos):
            is_valid, errors = validate.validate_pagamento(pagamento, index)
            if is_valid:
                validos.append({
                    'id_pagamento': pagamento.get('id_pagamento', f'#{index}'),
                    'status': 'OK',
                    'mensagem': 'Pagamento válido'
                })
            else:
                for error in errors:
                    if 'será truncado' in error.lower() or 'será ajustado' in error.lower():
                        avisos.append({
                            'id_pagamento': pagamento.get('id_pagamento', f'#{index}'),
                            'status': 'AVISO',
                            'mensagem': error
                        })
                    else:
                        erros.append({
                            'id_pagamento': pagamento.get('id_pagamento', f'#{index}'),
                            'status': 'ERRO',
                            'mensagem': error
                        })

        st.session_state.validacao_resultado = {
            'erros': erros,
            'avisos': avisos,
            'validos': validos,
            'total': len(pagamentos),
            'total_erros': len(erros),
            'total_avisos': len(avisos),
            'total_validos': len(validos)
        }

        if erros:
            st.error(f"❌ {len(erros)} erro(s) encontrado(s). Corrija o Excel e faça novo upload para liberar a geração do CNAB.")
            
            # Seção de debug com detalhes dos erros
            with st.expander("🔍 Ver Detalhes dos Erros", expanded=True):
                st.markdown("### 📋 Erros Encontrados")
                if erros:
                    # Cria DataFrame para exibir erros
                    erros_df = pd.DataFrame(erros)
                    st.dataframe(
                        erros_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "id_pagamento": st.column_config.TextColumn("ID Pagamento", width="small"),
                            "status": st.column_config.TextColumn("Status", width="small"),
                            "mensagem": st.column_config.TextColumn("Mensagem de Erro", width="large")
                        }
                    )
                else:
                    st.info("Nenhum erro encontrado.")
                
                if avisos:
                    st.markdown("### ⚠️ Avisos Encontrados")
                    avisos_df = pd.DataFrame(avisos)
                    st.dataframe(
                        avisos_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "id_pagamento": st.column_config.TextColumn("ID Pagamento", width="small"),
                            "status": st.column_config.TextColumn("Status", width="small"),
                            "mensagem": st.column_config.TextColumn("Mensagem de Aviso", width="large")
                        }
                    )
                
                # Resumo estatístico
                st.markdown("### 📊 Resumo da Validação")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total de Pagamentos", st.session_state.validacao_resultado['total'])
                with col2:
                    st.metric("✅ Válidos", st.session_state.validacao_resultado['total_validos'], delta=None)
                with col3:
                    st.metric("❌ Erros", st.session_state.validacao_resultado['total_erros'], delta=None, delta_color="inverse")
                with col4:
                    st.metric("⚠️ Avisos", st.session_state.validacao_resultado['total_avisos'], delta=None)
        else:
            st.success("✅ Arquivo validado com sucesso! Você já pode ir em **Gerar CNAB**.")
            
            # Mostra avisos mesmo quando não há erros
            if avisos:
                with st.expander("⚠️ Ver Avisos", expanded=False):
                    st.markdown("### ⚠️ Avisos Encontrados")
                    avisos_df = pd.DataFrame(avisos)
                    st.dataframe(
                        avisos_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "id_pagamento": st.column_config.TextColumn("ID Pagamento", width="small"),
                            "status": st.column_config.TextColumn("Status", width="small"),
                            "mensagem": st.column_config.TextColumn("Mensagem de Aviso", width="large")
                        }
                    )
        
        # Botão para limpar
        if st.button("🗑️ Limpar Dados", width="stretch"):
            st.session_state.pagamentos = None
            st.session_state.pagamentos_df = None
            st.session_state.validacao_resultado = None
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {str(e)}")
        st.exception(e)

else:
    st.info("👆 Faça upload do arquivo Excel para começar.")

