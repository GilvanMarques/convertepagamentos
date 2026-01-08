"""
Página de Configuração - Gerador CNAB 240
Permite carregar e editar a configuração da empresa/conta
"""
import streamlit as st
from pathlib import Path
import sys
import re
from datetime import datetime

# Verifica dependências
try:
    import yaml
except ImportError:
    st.error("""
    ❌ **Módulo PyYAML não encontrado!**
    
    Por favor, instale as dependências executando:
    ```bash
    pip install -r requirements.txt
    ```
    
    Ou instale diretamente:
    ```bash
    pip install PyYAML
    ```
    """)
    st.stop()

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.cnab240.config import load_config
    from src.cnab240 import validate
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

st.title("⚙️ Configuração")
st.markdown("Configure os dados da empresa e conta bancária para geração do arquivo CNAB.")
st.info("💡 **Nota**: Esta página é opcional. A configuração padrão será carregada automaticamente do arquivo `config/bradesco.yaml` se não for alterada aqui.")

st.info("""
💡 **Como usar:**
- Preencha todos os campos marcados com * (obrigatórios)
- Use **"Salvar na Memória"** para testar as configurações na sessão atual
- Use **"Salvar no Arquivo YAML"** para salvar permanentemente no arquivo `config/bradesco.yaml`
- Os dados serão validados automaticamente antes de salvar
""")

# Inicializa config se não existir
if 'config' not in st.session_state:
    st.session_state.config = None

# Função para validar CNPJ
def validar_cnpj(cnpj: str):
    """Valida CNPJ e retorna (é_válido, mensagem)"""
    if not cnpj:
        return False, "CNPJ não informado"
    
    cnpj_clean = re.sub(r'[^0-9]', '', str(cnpj))
    
    if len(cnpj_clean) != 14:
        return False, f"CNPJ deve ter 14 dígitos (encontrado: {len(cnpj_clean)})"
    
    if not validate.validate_cnpj(cnpj_clean):
        return False, "CNPJ inválido (dígitos verificadores incorretos)"
    
    return True, "CNPJ válido"

# Função para validar agência/conta
def validar_agencia_conta(agencia: str, conta: str, digito_conta: str):
    """Valida agência e conta"""
    if not agencia or len(agencia) != 5:
        return False, "Agência deve ter 5 dígitos"
    
    if not conta or len(conta) != 12:
        return False, "Conta deve ter 12 dígitos"
    
    if not digito_conta:
        return False, "Dígito da conta é obrigatório"
    
    return True, "Agência e conta válidas"

# Carregar configuração padrão
config_path = Path(__file__).parent.parent.parent / 'config' / 'bradesco.yaml'

try:
    if st.session_state.config is None:
        config = load_config(str(config_path))
        st.session_state.config = config
    else:
        config = st.session_state.config
except ImportError as e:
    error_msg = str(e)
    if "PyYAML" in error_msg or "yaml" in error_msg.lower():
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
    st.stop()
except FileNotFoundError:
    st.error("❌ Arquivo de configuração não encontrado. Verifique se o arquivo `config/bradesco.yaml` existe.")
    st.stop()
except Exception as e:
    error_msg = str(e)
    if "PyYAML" in error_msg or "yaml" in error_msg.lower():
        st.error("""
        ❌ **Módulo PyYAML não encontrado!**
        
        Por favor, instale as dependências executando:
        ```bash
        pip install -r requirements.txt
        ```
        """)
    else:
        st.error(f"❌ Erro ao carregar configuração: {error_msg}")
    st.stop()

# Formulário de edição
st.divider()
st.subheader("✏️ Editar Configuração")

with st.form("config_form"):
    # Dados da Empresa
    st.markdown("### 🏢 Dados da Empresa")
    
    tipo_inscricao_valor = config.get('empresa', {}).get('tipo_inscricao', 2)
    tipo_inscricao_index = 0 if tipo_inscricao_valor == 1 else 1
    tipo_inscricao = st.selectbox(
        "Tipo de Inscrição *",
        options=[1, 2],
        format_func=lambda x: "CPF" if x == 1 else "CNPJ",
        index=tipo_inscricao_index,
        help="1 = CPF, 2 = CNPJ"
    )
    
    numero_inscricao = st.text_input(
        "Número de Inscrição (CPF/CNPJ) *",
        value=config.get('empresa', {}).get('numero_inscricao', ''),
        help="Apenas números (11 dígitos para CPF, 14 para CNPJ). Pode incluir pontos, traços e barras - serão removidos automaticamente."
    )
    
    nome_empresa = st.text_input(
        "Nome da Empresa *",
        value=config.get('empresa', {}).get('nome', ''),
        max_chars=30,
        help="Máximo 30 caracteres. Será convertido para MAIÚSCULAS automaticamente."
    )
    
    # Validação CNPJ
    if tipo_inscricao == 2:
        cnpj_valido, cnpj_msg = validar_cnpj(numero_inscricao)
        if cnpj_valido:
            st.success(f"✅ {cnpj_msg}")
        else:
            st.warning(f"⚠️ {cnpj_msg}")
    
    st.divider()
    
    # Dados da Conta
    st.markdown("### 🏦 Dados da Conta")
    
    codigo_convenio = st.text_input(
        "Código do Convênio",
        value=config.get('conta', {}).get('codigo_convenio', ''),
        help="Deixe em branco se não tiver código do convênio. Máximo 6 caracteres (será alinhado à esquerda)."
    )
    
    agencia = st.text_input(
        "Agência *",
        value=config.get('conta', {}).get('agencia', ''),
        max_chars=5,
        help="5 dígitos (apenas números). Será preenchido com zeros à esquerda se necessário."
    )
    
    digito_agencia = st.text_input(
        "Dígito da Agência",
        value=config.get('conta', {}).get('digito_agencia', ''),
        max_chars=1,
        help="1 caractere alfanumérico (deixe em branco se não tiver)"
    )
    
    conta = st.text_input(
        "Conta Corrente *",
        value=config.get('conta', {}).get('conta', ''),
        max_chars=12,
        help="12 dígitos (apenas números). Será preenchido com zeros à esquerda se necessário."
    )
    
    digito_conta = st.text_input(
        "Dígito da Conta *",
        value=config.get('conta', {}).get('digito_conta', ''),
        max_chars=1,
        help="1 caractere alfanumérico (obrigatório)"
    )
    
    digito_verificador = st.text_input(
        "Dígito Verificador Ag/Conta",
        value=config.get('conta', {}).get('digito_verificador', ''),
        max_chars=1,
        help="Opcional - 1 caractere alfanumérico"
    )
    
    # Validação agência/conta
    agencia_conta_valida, agencia_conta_msg = validar_agencia_conta(agencia, conta, digito_conta)
    if agencia_conta_valida:
        st.success(f"✅ {agencia_conta_msg}")
    else:
        st.warning(f"⚠️ {agencia_conta_msg}")
    
    st.divider()
    
    # Parâmetros do Arquivo
    st.markdown("### 📄 Parâmetros do Arquivo")
    
    sequencial_inicial = st.number_input(
        "Sequencial Inicial",
        min_value=1,
        value=config.get('arquivo', {}).get('sequencial_inicial', 1),
        help="Número sequencial inicial do arquivo"
    )
    
    data_gravacao = st.date_input(
        "Data de Gravação",
        value=datetime.now().date(),
        help="Data de gravação do arquivo (padrão: hoje)"
    )
    
    layout_arquivo = st.number_input(
        "Layout do Arquivo",
        min_value=1,
        value=config.get('arquivo', {}).get('layout_arquivo', 80),
        help="080 para TED/DOC, 089 para PIX"
    )
    
    layout_lote = st.number_input(
        "Layout do Lote",
        min_value=1,
        value=config.get('arquivo', {}).get('layout_lote', 12),
        help="012 para PIX, 040 para TED/DOC"
    )

    st.markdown("#### 🧾 Parâmetros TED (convênio)")
    forma_lancamento_ted = st.text_input(
        "Forma de Lançamento TED (pos. 12-13)",
        value=str(config.get('arquivo', {}).get('forma_lancamento_ted', '41')),
        max_chars=2,
        help="Código de 2 dígitos exigido pelo Bradesco para TED neste convênio. Ex.: 41 = TED outra titularidade."
    )
    layout_lote_ted = st.number_input(
        "Layout do Lote TED (pos. 14-16)",
        min_value=1,
        value=int(config.get('arquivo', {}).get('layout_lote_ted', 45)),
        help="Versão do layout do lote para TED neste convênio. Ex.: 45 = '045' (default do manual)."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        submitted = st.form_submit_button("💾 Salvar na Memória", width="stretch")
    
    with col2:
        salvar_arquivo = st.form_submit_button("💾 Salvar no Arquivo YAML", width="stretch", type="primary")
    
    if submitted or salvar_arquivo:
        # Validações antes de salvar
        erros = []
        
        # Valida CNPJ se tipo_inscricao = 2
        if tipo_inscricao == 2:
            cnpj_clean = re.sub(r'[^0-9]', '', numero_inscricao)
            if len(cnpj_clean) != 14:
                erros.append("CNPJ deve ter 14 dígitos")
            elif not validate.validate_cnpj(cnpj_clean):
                erros.append("CNPJ inválido (dígitos verificadores incorretos)")
        
        # Valida agência
        agencia_clean = re.sub(r'[^0-9]', '', agencia)
        if len(agencia_clean) != 5:
            erros.append("Agência deve ter 5 dígitos")
        
        # Valida conta
        conta_clean = re.sub(r'[^0-9]', '', conta)
        if len(conta_clean) != 12:
            erros.append("Conta deve ter 12 dígitos")
        
        # Valida dígito da conta
        if not digito_conta:
            erros.append("Dígito da conta é obrigatório")
        
        if erros:
            for erro in erros:
                st.error(f"❌ {erro}")
        else:
            # Prepara configuração
            nova_config = {
                'empresa': {
                    'tipo_inscricao': int(tipo_inscricao),
                    'numero_inscricao': re.sub(r'[^0-9]', '', numero_inscricao),
                    'nome': nome_empresa.upper()[:30]  # Máximo 30 caracteres
                },
                'conta': {
                    'codigo_convenio': codigo_convenio.strip(),
                    'agencia': agencia_clean.zfill(5),
                    'digito_agencia': digito_agencia.strip(),
                    'conta': conta_clean.zfill(12),
                    'digito_conta': digito_conta.strip(),
                    'digito_verificador': digito_verificador.strip()
                },
                'arquivo': {
                    'sequencial_inicial': int(sequencial_inicial),
                    'layout_arquivo': int(layout_arquivo),
                    'layout_lote': int(layout_lote),
                    # Parâmetros TED (convênio)
                    'forma_lancamento_ted': str(forma_lancamento_ted).zfill(2)[:2],
                    'layout_lote_ted': int(layout_lote_ted),
                    # Default do manual para DOC/TED (quando aplicável)
                    'layout_lote_doc_ted': int(config.get('arquivo', {}).get('layout_lote_doc_ted', 45)),
                }
            }
            
            # Salva na memória (sempre)
            st.session_state.config = nova_config
            st.session_state.data_gravacao = data_gravacao
            
            # Se clicou em "Salvar no Arquivo YAML", salva no disco
            if salvar_arquivo:
                try:
                    # Prepara conteúdo YAML formatado
                    yaml_content = f"""# Configuração Bradesco Multipag
# Preencha com os dados da sua empresa e conta
# Arquivo gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

empresa:
  # Tipo de inscrição: 1=CPF, 2=CNPJ
  tipo_inscricao: {nova_config['empresa']['tipo_inscricao']}
  # Número de inscrição (CPF ou CNPJ, apenas números)
  numero_inscricao: "{nova_config['empresa']['numero_inscricao']}"
  # Nome da empresa (máximo 30 caracteres)
  nome: "{nova_config['empresa']['nome']}"

conta:
  # Código do convênio (máximo 20 caracteres)
  # Se não tiver código do convênio, deixar vazio (será preenchido com espaços)
  # Formato: 6 primeiros dígitos (033-038) alinhados à esquerda + 14 espaços (039-052)
  codigo_convenio: "{nova_config['conta']['codigo_convenio']}"
  # Agência (5 dígitos, apenas números)
  agencia: "{nova_config['conta']['agencia']}"
  # Dígito da agência (1 caractere alfanumérico)
  digito_agencia: "{nova_config['conta']['digito_agencia']}"
  # Conta corrente (12 dígitos, apenas números, zero-fill à esquerda)
  conta: "{nova_config['conta']['conta']}"
  # Dígito da conta (1 caractere alfanumérico)
  digito_conta: "{nova_config['conta']['digito_conta']}"
  # Dígito verificador Agência/Conta (opcional)
  digito_verificador: "{nova_config['conta']['digito_verificador']}"

# Parâmetros do arquivo
arquivo:
  # Número sequencial inicial (será incrementado automaticamente)
  sequencial_inicial: {nova_config['arquivo']['sequencial_inicial']}
  # Layout do Arquivo (conforme manual Bradesco Multipag)
  # Para TED/DOC deve ser 080 (não 089)
  layout_arquivo: {nova_config['arquivo']['layout_arquivo']}
  # Layout do Lote (conforme manual Bradesco Multipag)
  layout_lote: {nova_config['arquivo']['layout_lote']}
  # Convênio TED (conforme orientação/validador Bradesco)
  forma_lancamento_ted: "{nova_config['arquivo']['forma_lancamento_ted']}"
  layout_lote_ted: {nova_config['arquivo']['layout_lote_ted']}
  # Default do manual (Header de Lote)
  layout_lote_doc_ted: {nova_config['arquivo']['layout_lote_doc_ted']}
"""
                    
                    # Salva no arquivo
                    with open(config_path, 'w', encoding='utf-8') as f:
                        f.write(yaml_content)
                    
                    st.success("✅ Configuração salva com sucesso no arquivo YAML!")
                    st.info(f"📁 Arquivo salvo em: `{config_path}`")
                    
                except Exception as e:
                    st.error(f"❌ Erro ao salvar arquivo: {str(e)}")
            else:
                st.success("✅ Configuração salva na memória!")
            
            st.rerun()

# Exibir configuração atual
st.divider()
st.subheader("📋 Configuração Atual")

if st.session_state.config:
    with st.expander("Ver configuração completa", expanded=False):
        st.json(st.session_state.config)
        
        # Status de validação
        st.markdown("### Status de Validação")
        
        status_items = []
        
        # Valida CNPJ
        if st.session_state.config.get('empresa', {}).get('tipo_inscricao') == 2:
            cnpj = st.session_state.config.get('empresa', {}).get('numero_inscricao', '')
            cnpj_valido, cnpj_msg = validar_cnpj(cnpj)
            status_items.append(("CNPJ", cnpj_valido, cnpj_msg))
        
        # Valida agência/conta
        agencia = st.session_state.config.get('conta', {}).get('agencia', '')
        conta = st.session_state.config.get('conta', {}).get('conta', '')
        digito_conta = st.session_state.config.get('conta', {}).get('digito_conta', '')
        agencia_conta_valida, agencia_conta_msg = validar_agencia_conta(agencia, conta, digito_conta)
        status_items.append(("Agência/Conta", agencia_conta_valida, agencia_conta_msg))
        
        # Exibe status
        for item, valido, msg in status_items:
            if valido:
                st.markdown(f"✅ **{item}**: {msg}")
            else:
                st.markdown(f"⚠️ **{item}**: {msg}")

