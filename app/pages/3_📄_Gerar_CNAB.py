"""
Página de Geração de CNAB - Gerador CNAB 240
Gera o arquivo CNAB 240 para envio ao banco
"""
import streamlit as st
from pathlib import Path
import sys
from datetime import datetime
import io
import pandas as pd
import zipfile

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Verifica dependências antes de importar
try:
    import yaml
except ImportError:
    st.error("""
    ❌ **Módulo PyYAML não encontrado!**
    
    Por favor, instale as dependências executando:
    ```bash
    pip install -r requirements.txt
    ```
    
    Ou use o script de instalação:
    ```bash
    ./instalar_dependencias.sh
    ```
    """)
    st.stop()

# Tenta importar os geradores, mas captura erros de dependências
try:
    from src.cnab240.bradesco_pix import BradescoPIXGenerator
    from src.cnab240.bradesco_ted import BradescoTEDGenerator
except (ImportError, Exception) as e:
    error_msg = str(e)
    # Verifica se é erro de PyYAML
    if "PyYAML" in error_msg or "yaml" in error_msg.lower() or "No module named 'yaml'" in error_msg:
        st.error("""
        ❌ **Módulo PyYAML não encontrado!**
        
        Por favor, instale as dependências executando:
        ```bash
        pip install -r requirements.txt
        ```
        
        Ou use o script de instalação:
        ```bash
        ./instalar_dependencias.sh
        ```
        """)
    else:
        st.error(f"❌ Erro ao importar módulos: {error_msg}")
        st.info("💡 Certifique-se de que todas as dependências estão instaladas: `pip install -r requirements.txt`")
    st.stop()

st.title("📄 Gerar CNAB")
st.markdown("Gere o arquivo CNAB 240 para envio ao banco.")

# Verificações prévias
erros_preliminares = []

if 'config' not in st.session_state or st.session_state.config is None:
    erros_preliminares.append("⚠️ Configure os dados da empresa na página **Configuração**.")

if 'pagamentos' not in st.session_state or st.session_state.pagamentos is None:
    erros_preliminares.append("⚠️ Importe o arquivo Excel na página **Importar Excel**.")

if 'validacao_resultado' not in st.session_state or st.session_state.validacao_resultado is None:
    erros_preliminares.append("⚠️ Execute a validação na página **Validar**.")

if erros_preliminares:
    for erro in erros_preliminares:
        st.warning(erro)
    st.stop()

# Verifica se há erros na validação
resultado_validacao = st.session_state.validacao_resultado
if resultado_validacao['total_erros'] > 0:
    st.error(f"❌ Existem {resultado_validacao['total_erros']} erro(s) nos pagamentos. Corrija os erros antes de gerar o arquivo.")
    st.info("💡 Vá para a página **Validar** para ver os detalhes dos erros.")
    st.stop()

# Configuração
config = st.session_state.config
pagamentos = st.session_state.pagamentos
data_gravacao = st.session_state.get('data_gravacao', datetime.now().date())

# Agrupa pagamentos por tipo
tipos_pagamento = {}
for p in pagamentos:
    tipo = p.get('tipo_pagamento', 'PIX').upper().strip()
    if tipo not in tipos_pagamento:
        tipos_pagamento[tipo] = []
    tipos_pagamento[tipo].append(p)

# Informações sobre os arquivos a serem gerados
st.subheader("📋 Resumo dos Pagamentos")

# Mostra resumo por tipo
if tipos_pagamento:
    col1, col2, col3 = st.columns(3)
    
    total_geral = sum(p.get('valor', 0) for p in pagamentos)
    quantidade_geral = len(pagamentos)
    
    with col1:
        st.metric("Total de Pagamentos", quantidade_geral)
        st.metric("Tipos de Pagamento", len(tipos_pagamento))
    
    with col2:
        st.metric("Valor Total Geral", f"R$ {total_geral:,.2f}")
    
    with col3:
        data_str = data_gravacao.strftime('%d/%m/%Y') if isinstance(data_gravacao, datetime) or hasattr(data_gravacao, 'strftime') else str(data_gravacao)
        st.metric("Data de Gravação", data_str)
        sequencial = config.get('arquivo', {}).get('sequencial_inicial', 1)
        st.metric("Sequencial Inicial", sequencial)
    
    # Tabela com detalhes por tipo
    st.markdown("### 📊 Detalhamento por Tipo")
    dados_tabela = []
    for tipo, pagamentos_tipo in tipos_pagamento.items():
        total_tipo = sum(p.get('valor', 0) for p in pagamentos_tipo)
        dados_tabela.append({
            'Tipo': tipo,
            'Quantidade': len(pagamentos_tipo),
            'Valor Total': f"R$ {total_tipo:,.2f}"
        })
    
    df_tipos = pd.DataFrame(dados_tabela)
    st.dataframe(df_tipos, use_container_width=True, hide_index=True)
else:
    st.warning("⚠️ Nenhum pagamento encontrado para gerar arquivos.")
    st.stop()

# Botão para gerar
st.divider()
st.subheader("🚀 Gerar Arquivos CNAB")

if st.button("▶️ Gerar Todos os Arquivos CNAB", use_container_width=True, type="primary"):
    with st.spinner("Gerando arquivos CNAB..."):
        try:
            # Prepara data
            if isinstance(data_gravacao, datetime):
                file_date = data_gravacao
            elif hasattr(data_gravacao, 'strftime'):
                file_date = datetime.combine(data_gravacao, datetime.min.time())
            else:
                file_date = datetime.now()
            
            sequencial = config.get('arquivo', {}).get('sequencial_inicial', 1)
            arquivos_gerados = []
            sequencial_atual = sequencial
            
            # Gera um arquivo para cada tipo de pagamento
            for tipo, pagamentos_tipo in tipos_pagamento.items():
                try:
                    # Gera arquivo conforme tipo
                    if tipo == 'PIX':
                        generator = BradescoPIXGenerator()
                        lines = generator.generate_file(
                            pagamentos_tipo,
                            file_date=file_date,
                            file_seq=sequencial_atual
                        )
                        nome_arquivo = f"BRADESCO_PIX_REMESSA_{file_date.strftime('%Y%m%d')}_{sequencial_atual:06d}.txt"
                    elif tipo in ['TED', 'DOC']:
                        generator = BradescoTEDGenerator()
                        lines = generator.generate_file(
                            pagamentos_tipo,
                            file_date=file_date,
                            file_seq=sequencial_atual,
                            tipo_servico=tipo
                        )
                        nome_arquivo = f"BRADESCO_{tipo}_REMESSA_{file_date.strftime('%Y%m%d')}_{sequencial_atual:06d}.txt"
                    elif tipo == 'BOLETO':
                        st.warning(f"⚠️ Tipo BOLETO ainda não implementado. Pulando {len(pagamentos_tipo)} pagamento(s).")
                        continue
                    else:
                        st.warning(f"⚠️ Tipo de pagamento não suportado: {tipo}. Pulando {len(pagamentos_tipo)} pagamento(s).")
                        continue
                    
                    # Valida linhas
                    linhas_validas = True
                    erros_validacao = []
                    
                    for i, line in enumerate(lines, 1):
                        if len(line) != 240:
                            linhas_validas = False
                            erros_validacao.append(f"Linha {i}: tamanho incorreto ({len(line)} caracteres, esperado 240)")
                    
                    if not linhas_validas:
                        st.error(f"❌ Erro na validação do arquivo {nome_arquivo}:")
                        for erro in erros_validacao:
                            st.error(erro)
                        continue
                    
                    # Calcula total do tipo
                    total_valor = sum(p.get('valor', 0) for p in pagamentos_tipo)
                    
                    # Salva arquivo
                    arquivo_conteudo = '\r\n'.join(lines)
                    arquivos_gerados.append({
                        'nome': nome_arquivo,
                        'conteudo': arquivo_conteudo,
                        'linhas': len(lines),
                        'tipo': tipo,
                        'data': file_date,
                        'sequencial': sequencial_atual,
                        'total_valor': total_valor,
                        'quantidade': len(pagamentos_tipo)
                    })
                    
                    sequencial_atual += 1
                    
                except (ImportError, Exception) as e:
                    error_msg = str(e)
                    if "PyYAML" in error_msg or "yaml" in error_msg.lower() or "No module named 'yaml'" in error_msg:
                        st.error("""
                        ❌ **Módulo PyYAML não encontrado!**
                        
                        Por favor, instale as dependências executando:
                        ```bash
                        pip install -r requirements.txt
                        ```
                        """)
                        st.stop()
                    else:
                        st.error(f"❌ Erro ao gerar arquivo para {tipo}: {str(e)}")
                        continue
            
            if arquivos_gerados:
                # Salva todos os arquivos no session_state
                st.session_state.arquivos_gerados = arquivos_gerados
                st.success(f"✅ {len(arquivos_gerados)} arquivo(s) CNAB gerado(s) com sucesso!")
                st.rerun()
            else:
                st.error("❌ Nenhum arquivo foi gerado. Verifique os erros acima.")
        
        except Exception as e:
            st.error(f"❌ Erro ao gerar arquivos: {str(e)}")
            st.exception(e)

# Exibe arquivos gerados
if 'arquivos_gerados' in st.session_state and st.session_state.arquivos_gerados:
    arquivos = st.session_state.arquivos_gerados
    
    st.divider()
    st.subheader("📄 Arquivos Gerados")
    
    # Resumo geral
    total_arquivos = len(arquivos)
    total_registros = sum(a['linhas'] for a in arquivos)
    total_valor_geral = sum(a['total_valor'] for a in arquivos)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Arquivos Gerados", total_arquivos)
        st.metric("Total de Registros", total_registros)
    
    with col2:
        st.metric("Valor Total Geral", f"R$ {total_valor_geral:,.2f}")
    
    with col3:
        tipos_gerados = ', '.join(set(a['tipo'] for a in arquivos))
        st.metric("Tipos Gerados", tipos_gerados)
    
    # Lista de arquivos
    st.markdown("### 📋 Detalhes dos Arquivos")
    
    for idx, arquivo in enumerate(arquivos, 1):
        with st.expander(f"📄 {arquivo['nome']} ({arquivo['tipo']})", expanded=(idx == 1)):
            # Informações do arquivo
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Registros", arquivo['linhas'])
                st.metric("Quantidade de Pagamentos", arquivo['quantidade'])
            
            with col2:
                st.metric("Tipo", arquivo['tipo'])
                st.metric("Valor Total", f"R$ {arquivo['total_valor']:,.2f}")
            
            with col3:
                data_str = arquivo['data'].strftime('%d/%m/%Y') if isinstance(arquivo['data'], datetime) else str(arquivo['data'])
                st.metric("Data", data_str)
                st.metric("Sequencial", arquivo['sequencial'])
            
            # Download individual
            st.download_button(
                label=f"📥 Baixar {arquivo['nome']}",
                data=arquivo['conteudo'].encode('utf-8'),
                file_name=arquivo['nome'],
                mime="text/plain",
                use_container_width=True,
                key=f"download_{idx}"
            )
            
            # Prévia do arquivo
            with st.expander("👀 Prévia do Arquivo (primeiras 10 linhas)", expanded=False):
                linhas_previa = arquivo['conteudo'].split('\r\n')[:10]
                st.code('\n'.join(linhas_previa), language=None)
            
            # Informações técnicas
            with st.expander("ℹ️ Informações Técnicas", expanded=False):
                st.markdown(f"""
                - **Tamanho de cada linha**: 240 caracteres
                - **Total de linhas**: {arquivo['linhas']}
                - **Formato**: CNAB 240
                - **Banco**: Bradesco (237)
                - **Layout do Arquivo**: {config.get('arquivo', {}).get('layout_arquivo', 'N/A')}
                - **Layout do Lote**: {config.get('arquivo', {}).get('layout_lote', 'N/A')}
                """)
    
    # Botão para salvar todos os arquivos
    st.divider()
    st.subheader("💾 Salvar Arquivos")
    
    # Cria um ZIP com todos os arquivos
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for arquivo in arquivos:
            zip_file.writestr(arquivo['nome'], arquivo['conteudo'].encode('utf-8'))
    
    zip_buffer.seek(0)
    nome_zip = f"BRADESCO_CNAB_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📦 Baixar Todos os Arquivos (ZIP)",
            data=zip_buffer.getvalue(),
            file_name=nome_zip,
            mime="application/zip",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        if st.button("🔄 Gerar Novos Arquivos", use_container_width=True):
            st.session_state.arquivos_gerados = None
            st.rerun()

else:
    st.info("👆 Clique no botão acima para gerar todos os arquivos CNAB necessários.")

