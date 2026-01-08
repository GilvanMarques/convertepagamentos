"""
Página de Validação - Gerador CNAB 240
Valida os dados dos pagamentos antes de gerar o arquivo CNAB
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

try:
    from src.cnab240 import validate
except ImportError as e:
    st.error(f"❌ Erro ao importar módulos: {str(e)}")
    st.info("💡 Certifique-se de que todas as dependências estão instaladas: `pip install -r requirements.txt`")
    st.stop()

st.title("✅ Validar Dados")
st.markdown("Valide os dados dos pagamentos antes de gerar o arquivo CNAB.")

# Verifica se há pagamentos carregados
if 'pagamentos' not in st.session_state or st.session_state.pagamentos is None:
    st.warning("⚠️ Nenhum pagamento carregado. Importe o arquivo Excel na página **Importar Excel**.")
    st.info("💡 Use o menu lateral para navegar até a página de Importar Excel.")
    st.stop()

pagamentos = st.session_state.pagamentos

# Inicializa resultado de validação
if 'validacao_resultado' not in st.session_state:
    st.session_state.validacao_resultado = None

# Botão para executar validação
st.subheader("🔍 Executar Validação")

if st.button("▶️ Validar Todos os Pagamentos", width="stretch", type="primary"):
    with st.spinner("Validando pagamentos..."):
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
                    # Classifica como erro ou aviso
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
        
        # Salva resultado
        st.session_state.validacao_resultado = {
            'erros': erros,
            'avisos': avisos,
            'validos': validos,
            'total': len(pagamentos),
            'total_erros': len(erros),
            'total_avisos': len(avisos),
            'total_validos': len(validos)
        }
        
        st.rerun()

# Exibe resultados se houver
if st.session_state.validacao_resultado:
    resultado = st.session_state.validacao_resultado
    
    st.divider()
    st.subheader("📊 Resultado da Validação")
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total", resultado['total'])
    
    with col2:
        st.metric("✅ Válidos", resultado['total_validos'], 
                 delta=None if resultado['total_validos'] == resultado['total'] else f"-{resultado['total'] - resultado['total_validos']}")
    
    with col3:
        st.metric("⚠️ Avisos", resultado['total_avisos'])
    
    with col4:
        st.metric("❌ Erros", resultado['total_erros'],
                 delta=None if resultado['total_erros'] == 0 else f"+{resultado['total_erros']}")
    
    # Status geral
    st.divider()
    
    if resultado['total_erros'] == 0:
        st.success("✅ Todos os pagamentos estão válidos! Você pode prosseguir para a geração do arquivo CNAB.")
    else:
        st.error(f"❌ Encontrados {resultado['total_erros']} erro(s). Corrija os erros antes de gerar o arquivo CNAB.")
    
    # Tabela de erros
    if resultado['erros']:
        st.subheader("❌ Erros Encontrados")
        df_erros = pd.DataFrame(resultado['erros'])
        st.dataframe(df_erros, width="stretch", hide_index=True)
    
    # Tabela de avisos
    if resultado['avisos']:
        st.subheader("⚠️ Avisos")
        df_avisos = pd.DataFrame(resultado['avisos'])
        st.dataframe(df_avisos, width="stretch", hide_index=True)
    
    # Tabela de válidos (se houver espaço)
    if resultado['validos'] and len(resultado['validos']) <= 50:
        with st.expander(f"✅ Pagamentos Válidos ({len(resultado['validos'])})", expanded=False):
            df_validos = pd.DataFrame(resultado['validos'])
            st.dataframe(df_validos, width="stretch", hide_index=True)
    
    # Download do relatório
    st.divider()
    st.subheader("📥 Download do Relatório")
    
    # Cria relatório completo
    relatorio = []
    for item in resultado['erros'] + resultado['avisos'] + resultado['validos']:
        relatorio.append(item)
    
    if relatorio:
        df_relatorio = pd.DataFrame(relatorio)
        csv = df_relatorio.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Baixar Relatório CSV",
            data=csv,
            file_name=f"relatorio_validacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width="stretch"
        )
    
    # Indicador de progresso
    st.divider()
    progresso = resultado['total_validos'] / resultado['total'] if resultado['total'] > 0 else 0
    st.progress(progresso)
    st.caption(f"Progresso: {resultado['total_validos']}/{resultado['total']} pagamentos válidos ({progresso*100:.1f}%)")

else:
    st.info("👆 Clique no botão acima para executar a validação dos pagamentos.")

