"""
Geração de arquivo CNAB 240 para TED/DOC Bradesco Multipag
Utiliza Segmento A + Segmento B (não Segmento J)
"""
from datetime import datetime
from typing import List, Dict
from . import fields
from .config import load_config


class BradescoTEDGenerator:
    """Gerador de arquivo CNAB 240 para TED/DOC Bradesco"""
    
    def __init__(self, config_path: str | None = None):
        """
        Inicializa o gerador com a configuração.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config = load_config(config_path)
        self.sequence = 0
        self.detail_count = 0
        self.total_amount = 0.0
    
    @staticmethod
    def fmt_date_ddmmyyyy(value: str | datetime | None) -> str:
        """
        Formata data no formato DDMMAAAA (padrão Bradesco Multipag TED/DOC).
        
        Args:
            value: Data como string (vários formatos), datetime ou None
        
        Returns:
            String formatada como DDMMAAAA (8 caracteres) ou data atual se inválida
        """
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return datetime.now().strftime('%d%m%Y')
        
        try:
            if isinstance(value, datetime):
                return value.strftime('%d%m%Y')
            
            if isinstance(value, str):
                # Tenta vários formatos comuns
                formats = [
                    '%Y-%m-%d',
                    '%d/%m/%Y',
                    '%d-%m-%Y',
                    '%Y%m%d',
                    '%d/%m/%y',
                    '%d%m%Y',
                ]
                
                for fmt in formats:
                    try:
                        dt = datetime.strptime(value.strip(), fmt)
                        return dt.strftime('%d%m%Y')
                    except ValueError:
                        continue
                
                # Se nenhum formato funcionou, tenta parsear como YYYYMMDD
                if len(value.strip()) == 8 and value.strip().isdigit():
                    try:
                        dt = datetime.strptime(value.strip(), '%Y%m%d')
                        return dt.strftime('%d%m%Y')
                    except ValueError:
                        pass
        except Exception:
            pass
        
        # Fallback: retorna data atual
        return datetime.now().strftime('%d%m%Y')
        
    def _reset_sequence(self):
        """Reseta o contador sequencial"""
        self.sequence = 0
    
    def generate_header_arquivo(self, file_date: datetime, file_seq: int) -> str:
        """Gera registro Header Arquivo (Registro 0)"""
        empresa = self.config['empresa']
        conta = self.config['conta']
        arquivo_config = self.config.get('arquivo', {})
        # Layout do Arquivo para TED/DOC Multipag: 089 (conforme erro de validação)
        # O sistema Bradesco Multipag exige 089 para arquivos de pagamento
        # SEMPRE usar 089 para Multipag, independente do config
        layout_arquivo = 89  # Multipag exige 089 (forçado)
        
        # Data de gravação (colunas 144-151)
        # IMPORTANTE: Header Arquivo e Header Lote DEVEM usar a MESMA data (data corrente)
        # Para Bradesco Multipag TED/DOC: formato DDMMAAAA (não YYYYMMDD)
        if file_date is None:
            file_date = datetime.now()
        data_gravacao = file_date.strftime('%d%m%Y')  # Formato DDMMAAAA
        
        line = ''
        line += fields.format_numeric(237, 3)  # Código do Banco
        line += fields.format_numeric(0, 4)  # Lote de Serviço (0000)
        line += fields.format_numeric(0, 1)  # Tipo de Registro
        line += fields.format_alphanumeric('', 9)  # CNAB Reservado
        line += fields.format_numeric(empresa['tipo_inscricao'], 1)  # Tipo de Inscrição
        # CNPJ: apenas números, zero-fill à esquerda até 14 posições
        cnpj_clean = ''.join(filter(str.isdigit, str(empresa['numero_inscricao'])))
        line += fields.format_numeric(cnpj_clean, 14)  # Número de Inscrição (14 posições)
        # Código do Convênio: alinhar à esquerda
        # 033-038: 6 caracteres alinhados à esquerda (ou espaços se vazio)
        # 039-052: 14 caracteres em branco (espaços)
        codigo_conv = str(conta.get('codigo_convenio', '')).strip()
        if codigo_conv:
            # Se tiver código, usa primeiros 6 caracteres alinhados à esquerda
            parte1 = codigo_conv[:6].ljust(6)  # 033-038: alinha à esquerda
        else:
            # Se não tiver código, deixa em branco (6 espaços)
            parte1 = ' ' * 6  # 033-038: espaços
        # 039-052: sempre em branco (14 espaços)
        parte2 = ' ' * 14
        line += parte1 + parte2
        line += fields.format_numeric(conta['agencia'], 5)  # Agência Mantenedora
        line += fields.format_alphanumeric(conta['digito_agencia'], 1)  # Dígito da Agência
        line += fields.format_numeric(conta['conta'], 12)  # Conta Corrente
        line += fields.format_alphanumeric(conta['digito_conta'], 1)  # Dígito da Conta
        line += fields.format_alphanumeric(conta.get('digito_verificador', ''), 1)  # DV Ag/Conta
        line += fields.format_alphanumeric(empresa['nome'], 30)  # Nome da Empresa
        line += fields.format_alphanumeric('BRADESCO', 30)  # Nome do Banco
        line += fields.format_alphanumeric('', 10)  # CNAB Reservado
        line += fields.format_numeric(1, 1)  # Código Remessa/Retorno (1=Remessa)
        line += data_gravacao  # Data de Gravação (144-151, 8 posições, DDMMAAAA)
        line += fields.format_time(file_date)  # Hora de Geração
        line += fields.format_numeric(file_seq, 6)  # Número Sequencial
        line += fields.format_numeric(layout_arquivo, 3)  # Layout do Arquivo
        line += fields.format_numeric(1600, 5)  # Densidade
        line += fields.format_alphanumeric('', 20)  # Reservado Banco
        line += fields.format_alphanumeric('', 20)  # Reservado Empresa
        line += fields.format_alphanumeric('', 6)  # Versão Aplicativo
        line += fields.format_alphanumeric('', 23)  # CNAB Reservado
        
        return fields.ensure_length_240(line)
    
    def generate_header_lote(self, file_date: datetime, remessa_seq: int, tipo_servico: str = 'TED') -> str:
        """Gera registro Header Lote (Registro 1)"""
        empresa = self.config['empresa']
        conta = self.config['conta']
        arquivo_config = self.config.get('arquivo', {})
        # IMPORTANTE (Bradesco Multipag):
        # - O validador do banco tem rejeitado "Tipo de Serviço = 30" como se fosse "Pagamento Salários".
        # - Para pagamentos TED/DOC (Segmentos A/B), use "Tipo de Serviço = 20" (Pagamentos/Fornecedor).
        # - A versão do layout do lote (014-016) pode variar por contrato/validador.
        #   No manual Multipag (Versão 08), para "Registro Header de Lote" o default é **045**.
        #   Por isso, é parametrizável em `config/bradesco.yaml`:
        #     arquivo:
        #       layout_lote_doc_ted: 45   # gera "045" (forma 03)
        #       layout_lote_doc: 45       # gera "045" (forma 06, se aplicável)
        #   Se não informado, usamos o default do manual (045).
        # Forma de lançamento (pos. 12-13)
        # Padrão CNAB: 03 = DOC/TED. Porém, alguns convênios/validador do Bradesco podem exigir
        # uma "TED específica" (código diferente de 03). Por isso, é parametrizável no YAML:
        #
        # arquivo:
        #   forma_lancamento_ted: "03"   # substitua pelo código exigido pelo convênio
        #   forma_lancamento_doc: "06"
        #
        if tipo_servico.upper() == 'TED':
            # Default ajustado conforme orientação do validador Bradesco:
            # 41 = TED (outra titularidade) para este convênio
            forma_lancamento = str(arquivo_config.get('forma_lancamento_ted', '41')).zfill(2)[:2]
        else:
            forma_lancamento = str(arquivo_config.get('forma_lancamento_doc', '06')).zfill(2)[:2]

        # Layout do lote (pos. 14-16) - parametrizável
        # Por default, seguimos o manual Multipag (Versão 08): "045".
        # Se o Bradesco exigir outra versão para a "TED específica" do seu convênio (ex.: 031),
        # informe no YAML:
        #
        # arquivo:
        #   layout_lote_ted: 31
        #
        if tipo_servico.upper() == 'TED':
            layout_lote = arquivo_config.get('layout_lote_ted', arquivo_config.get('layout_lote_doc_ted', 45))
        else:
            layout_lote = arquivo_config.get('layout_lote_doc', 45)
        if isinstance(layout_lote, str):
            layout_lote = int(layout_lote)
        layout_lote = int(layout_lote)
        
        # Montagem conforme manual Multipag (Versão 08) - Registro Header de Lote (posições 1-240)
        # Campos críticos para o validador:
        # - 10-11 Tipo de Serviço = 20 (Pagamento/Fornecedor)
        # - 12-13 Forma de Lançamento = 41 (TED outra titularidade)
        # - 14-16 Layout do Lote = 045
        # - 223-224 Indicativo da Forma de Pagamento do Serviço = 01
        line = ''
        line += fields.format_numeric(237, 3)  # 1-3 Banco
        line += fields.format_numeric(1, 4)  # 4-7 Lote
        line += fields.format_numeric(1, 1)  # 8 Registro
        line += fields.format_alphanumeric('C', 1)  # 9 Operação
        line += fields.format_numeric(20, 2)  # 10-11 Tipo de Serviço
        line += fields.format_numeric(forma_lancamento, 2)  # 12-13 Forma de Lançamento
        line += fields.format_numeric(layout_lote, 3)  # 14-16 Layout do Lote
        line += fields.format_alphanumeric('', 1)  # 17 CNAB
        line += fields.format_numeric(empresa['tipo_inscricao'], 1)  # 18 Tipo inscrição empresa
        cnpj_clean = ''.join(filter(str.isdigit, str(empresa['numero_inscricao'])))
        line += fields.format_numeric(cnpj_clean, 14)  # 19-32 Número inscrição empresa
        # 33-52 Convênio (6 à esquerda + 14 espaços)
        codigo_conv = str(conta.get('codigo_convenio', '')).strip()
        parte1 = codigo_conv[:6].ljust(6) if codigo_conv else (' ' * 6)
        parte2 = ' ' * 14
        line += parte1 + parte2
        line += fields.format_numeric(conta['agencia'], 5)  # 53-57 Agência
        line += fields.format_alphanumeric(conta['digito_agencia'], 1)  # 58 DV Agência
        line += fields.format_numeric(conta['conta'], 12)  # 59-70 Conta
        line += fields.format_alphanumeric(conta['digito_conta'], 1)  # 71 DV Conta
        line += fields.format_alphanumeric(conta.get('digito_verificador', ''), 1)  # 72 DV Ag/Conta
        line += fields.format_alphanumeric(empresa['nome'], 30)  # 73-102 Nome Empresa
        line += fields.format_alphanumeric('', 40)  # 103-142 Informação 1 (Mensagem)
        # 143-222 Dados de endereço (não utilizados): preencher conforme manual
        line += fields.format_alphanumeric('', 30)  # 143-172 Logradouro
        line += fields.format_numeric(0, 5)  # 173-177 Número do local
        line += fields.format_alphanumeric('', 15)  # 178-192 Complemento
        line += fields.format_alphanumeric('', 20)  # 193-212 Cidade
        line += fields.format_numeric(0, 5)  # 213-217 CEP (5)
        line += fields.format_alphanumeric('', 3)  # 218-220 Complemento CEP (3)
        line += fields.format_alphanumeric('', 2)  # 221-222 Estado
        line += fields.format_numeric(1, 2)  # 223-224 Indicativo da Forma de Pagamento do Serviço = 01
        line += fields.format_alphanumeric('', 6)  # 225-230 CNAB
        line += fields.format_alphanumeric('', 10)  # 231-240 Ocorrências (branco em remessa)
        
        return fields.ensure_length_240(line)
    
    def generate_segmento_a(self, pagamento: Dict, seq: int, file_date: datetime = None) -> str:
        """Gera registro Segmento A (Detalhe) para TED/DOC"""
        banco_favorecido = pagamento.get('banco_favorecido', '0')
        # Código da Câmara: 000 só é válido para banco 237 (Bradesco)
        # Para outros bancos, usar código apropriado (ex: 018 para TED)
        codigo_camara = '000' if banco_favorecido == '237' else '018'
        
        # Data de gravação do arquivo (para validação)
        if file_date is None:
            file_date = datetime.now()
        data_gravacao_arquivo = file_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        line = ''
        line += fields.format_numeric(237, 3)  # Código do Banco
        line += fields.format_numeric(1, 4)  # Lote de Serviço
        line += fields.format_numeric(3, 1)  # Tipo de Registro
        line += fields.format_numeric(seq, 5)  # Número Sequencial
        line += fields.format_alphanumeric('A', 1)  # Código Segmento
        line += fields.format_numeric(0, 1)  # Tipo de Movimento (0=Inclusão)
        line += fields.format_numeric(0, 2)  # Código da Instrução
        line += fields.format_numeric(codigo_camara, 3)  # Código da Câmara (018=TED, 000=Bradesco)
        line += fields.format_numeric(banco_favorecido, 3)  # Código do Banco Favorecido
        line += fields.format_numeric(pagamento.get('agencia_favorecido', '0'), 5)  # Agência Mantenedora
        line += fields.format_alphanumeric(pagamento.get('digito_agencia_favorecido', ''), 1)  # Dígito da Agência
        line += fields.format_numeric(pagamento.get('conta_favorecido', '0'), 12)  # Conta Corrente
        line += fields.format_alphanumeric(pagamento.get('digito_conta_favorecido', ''), 1)  # Dígito da Conta
        line += fields.format_alphanumeric('', 1)  # Dígito Verificador
        line += fields.format_alphanumeric(pagamento.get('nome_favorecido', ''), 30)  # Nome do Favorecido
        line += fields.format_alphanumeric(str(pagamento.get('id_pagamento', '')), 20)  # Número do Documento
        
        # Data de pagamento: validar e garantir formato DDMMAAAA
        # REGRA: Data de pagamento deve ser >= data de gravação do arquivo e não pode ser futura
        data_pagamento = pagamento.get('data_pagamento', '')
        data_formatada = None
        
        if data_pagamento and data_pagamento.strip():
            # Formata para DDMMAAAA
            data_formatada = self.fmt_date_ddmmyyyy(data_pagamento)
            
            # Valida se a data formatada é válida e >= data de gravação
            try:
                # Parseia a data formatada (DDMMAAAA)
                data_pag_obj = datetime.strptime(data_formatada, '%d%m%Y')
                data_pag_obj = data_pag_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Valida: não pode ser futura
                data_atual = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                if data_pag_obj > data_atual:
                    # Data futura: usar data de gravação do arquivo
                    data_formatada = data_gravacao_arquivo.strftime('%d%m%Y')
                # Valida: deve ser >= data de gravação do arquivo
                elif data_pag_obj < data_gravacao_arquivo:
                    # Data anterior à gravação: usar data de gravação do arquivo
                    data_formatada = data_gravacao_arquivo.strftime('%d%m%Y')
            except ValueError:
                # Data inválida: usar data de gravação do arquivo
                data_formatada = data_gravacao_arquivo.strftime('%d%m%Y')
        else:
            # Se não informada, usar data de gravação do arquivo
            data_formatada = data_gravacao_arquivo.strftime('%d%m%Y')
        
        line += data_formatada  # Data do Pagamento (col 094-101, 8 posições, DDMMAAAA)
        line += fields.format_alphanumeric('BRL', 3)  # Tipo da Moeda
        line += fields.format_numeric(0, 15)  # Quantidade de Moeda
        line += fields.format_amount(pagamento.get('valor'), 15)  # Valor do Pagamento
        line += fields.format_alphanumeric('', 20)  # Número do Documento Atribuído
        line += fields.format_numeric(0, 8)  # Data Real (zeros, não brancos) (155-162)
        line += fields.format_numeric(0, 15)  # Valor Real (zeros, não brancos) (163-177)
        # Campo SIAPE (colunas 178-217, 40 posições) - conforme manual G031
        # Preencher com brancos se não usado para SIAPE
        line += fields.format_alphanumeric('', 40)  # Campo SIAPE (brancos)
        # Tipo de Informação e Código Finalidade (colunas 218-219, 2 posições)
        line += fields.format_numeric(0, 2)  # Tipo de Informação / Código Finalidade
        # Código Finalidade TED (colunas 220-224, 5 posições)
        # Valores válidos conforme manual Bradesco (ex: 00001, 00002, etc.)
        finalidade_ted = str(pagamento.get('finalidade_ted', '00001')).strip()
        if not finalidade_ted or len(finalidade_ted) < 5:
            finalidade_ted = '00001'  # Padrão se não informado
        line += fields.format_numeric(finalidade_ted, 5)  # Código Finalidade TED (5 posições)
        # Código Finalidade Complementar (colunas 225-226, 2 posições)
        # 'CC' para Conta Corrente ou 'PP' para Poupança
        tipo_conta = pagamento.get('tipo_conta', 'CC').upper()
        if tipo_conta not in ['CC', 'PP']:
            tipo_conta = 'CC'  # Padrão: Conta Corrente
        line += fields.format_alphanumeric(tipo_conta, 2)  # Código Finalidade Complementar (225-226, 'CC' ou 'PP')
        # Exclusivo FEBRABAN (colunas 227-229, 3 posições): DEIXAR EM BRANCO
        # O Bradesco exige que essas 3 posições estejam completamente em branco
        line += fields.format_alphanumeric('', 3)  # Exclusivo FEBRABAN (227-229, 3 espaços)
        # Aviso ao favorecido: 0 ou 1 (não pode ser vazio) (230)
        aviso = pagamento.get('aviso_favorecido', 0)
        if aviso not in [0, 1]:
            aviso = 0
        line += fields.format_numeric(aviso, 1)  # Aviso ao Favorecido (230)
        line += fields.format_alphanumeric('', 6)  # Ocorrências (231-236)
        line += fields.format_alphanumeric('', 4)  # CNAB Reservado (237-240)
        
        return fields.ensure_length_240(line)
    
    def generate_segmento_b(self, pagamento: Dict, seq: int, file_date: datetime = None) -> str:
        """Gera registro Segmento B (Detalhe) para TED/DOC"""
        # Data de gravação do arquivo (para usar como fallback)
        if file_date is None:
            file_date = datetime.now()
        data_gravacao_arquivo = file_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Mapeia tipo de pessoa
        tipo_pessoa = pagamento.get('tipo_pessoa', 'F').upper()
        tipo_inscricao = '1' if tipo_pessoa == 'F' else '2'
        
        # Data de vencimento: usar data_pagamento se data_vencimento não informada
        # Formato: DDMMAAAA (mesmo padrão do Segmento A)
        data_vencimento = pagamento.get('data_vencimento') or pagamento.get('data_pagamento')
        if not data_vencimento or str(data_vencimento).strip() == '':
            # Se não informada, usar data de gravação do arquivo
            data_venc_formatada = data_gravacao_arquivo.strftime('%d%m%Y')
        else:
            # Formata para DDMMAAAA
            data_venc_formatada = self.fmt_date_ddmmyyyy(data_vencimento)
            # Valida se a data formatada é válida
            try:
                datetime.strptime(data_venc_formatada, '%d%m%Y')
            except ValueError:
                # Se data inválida, usar data de gravação do arquivo
                data_venc_formatada = data_gravacao_arquivo.strftime('%d%m%Y')
        
        line = ''
        line += fields.format_numeric(237, 3)  # Código do Banco
        line += fields.format_numeric(1, 4)  # Lote de Serviço
        line += fields.format_numeric(3, 1)  # Tipo de Registro
        line += fields.format_numeric(seq, 5)  # Número Sequencial
        line += fields.format_alphanumeric('B', 1)  # Código Segmento
        line += fields.format_alphanumeric('', 3)  # CNAB Reservado
        line += fields.format_numeric(tipo_inscricao, 1)  # Tipo de Inscrição
        line += fields.format_numeric(pagamento.get('cpf_cnpj', ''), 14)  # Número de Inscrição
        line += fields.format_alphanumeric(pagamento.get('endereco_favorecido', ''), 30)  # Endereço
        line += fields.format_alphanumeric(pagamento.get('numero_endereco', ''), 5)  # Número
        line += fields.format_alphanumeric(pagamento.get('complemento_endereco', ''), 15)  # Complemento
        line += fields.format_alphanumeric(pagamento.get('bairro_favorecido', ''), 15)  # Bairro
        line += fields.format_alphanumeric(pagamento.get('cidade_favorecido', ''), 20)  # Cidade
        line += fields.format_numeric(pagamento.get('cep_favorecido', '0'), 8)  # CEP
        line += fields.format_alphanumeric(pagamento.get('estado_favorecido', ''), 2)  # Estado
        line += data_venc_formatada  # Data de Vencimento (nominal) (col 128-135, 8 posições, DDMMAAAA)
        line += fields.format_amount(pagamento.get('valor'), 15)  # Valor do Documento (136-150)
        line += fields.format_numeric(0, 15)  # Valor do Abatimento (151-165)
        line += fields.format_numeric(0, 15)  # Valor do Desconto (166-180)
        line += fields.format_numeric(0, 15)  # Valor da Mora (181-195)
        line += fields.format_numeric(0, 15)  # Valor da Multa (196-210)
        line += fields.format_alphanumeric('', 1)  # Tipo Chave PIX (não usado em TED) (211)
        line += fields.format_alphanumeric('', 14)  # Chave PIX (não usado em TED) (212-225)
        # Código aviso ao favorecido (coluna 226): OBRIGATÓRIO
        # 0 = Não emite aviso, 1 = Emite aviso
        aviso_fav = pagamento.get('aviso_favorecido', 0)
        if aviso_fav not in [0, 1]:
            aviso_fav = 0
        line += fields.format_numeric(aviso_fav, 1)  # Código aviso ao favorecido (226)
        # Uso exclusivo Febraban (colunas 227-240): DEIXAR EM BRANCO
        line += fields.format_alphanumeric('', 14)  # Uso exclusivo Febraban (227-240, 14 posições em branco)
        
        return fields.ensure_length_240(line)
    
    def generate_trailer_lote(self, total_registros: int, total_titulos: int, total_valor: float) -> str:
        """Gera registro Trailer Lote (Registro 5)"""
        line = ''
        line += fields.format_numeric(237, 3)  # Código do Banco
        line += fields.format_numeric(1, 4)  # Lote de Serviço
        line += fields.format_numeric(5, 1)  # Tipo de Registro
        line += fields.format_alphanumeric('', 9)  # CNAB Reservado (9-17)
        line += fields.format_numeric(total_registros, 6)  # Quantidade de Registros (18-23)
        line += fields.format_amount(total_valor, 18)  # Somatória dos Valores (24-41, 18 posições)
        line += fields.format_numeric(0, 18)  # Somatório de quantidade de moedas (zeros, não brancos) (42-59)
        line += fields.format_numeric(0, 6)  # Número aviso de débito (zeros, não brancos) (60-65)
        line += fields.format_alphanumeric('', 175)  # CNAB Reservado (66-240)
        
        return fields.ensure_length_240(line)
    
    def generate_trailer_arquivo(self, total_registros: int) -> str:
        """Gera registro Trailer Arquivo (Registro 9)"""
        line = ''
        line += fields.format_numeric(237, 3)  # Código do Banco
        line += fields.format_numeric(9999, 4)  # Lote de Serviço (9999)
        line += fields.format_numeric(9, 1)  # Tipo de Registro
        line += fields.format_alphanumeric('', 9)  # CNAB Reservado
        line += fields.format_numeric(1, 6)  # Quantidade de Lotes
        line += fields.format_numeric(total_registros, 6)  # Quantidade de Registros
        line += fields.format_numeric(0, 6)  # Quantidade de Contas (zeros para conciliação bancária) (30-35)
        line += fields.format_alphanumeric('', 205)  # CNAB Reservado
        
        return fields.ensure_length_240(line)
    
    def generate_file(self, pagamentos: List[Dict], file_date: datetime | None = None, 
                     file_seq: int = 1, tipo_servico: str = 'TED') -> List[str]:
        """
        Gera arquivo CNAB 240 completo usando Segmento A e B para TED/DOC.
        
        Args:
            pagamentos: Lista de dicionários com dados dos pagamentos
            file_date: Data de geração (usa data atual se None)
            file_seq: Número sequencial do arquivo
            tipo_servico: 'TED' ou 'DOC'
        
        Returns:
            Lista de linhas do arquivo (cada linha com 240 caracteres)
        """
        if file_date is None:
            file_date = datetime.now()
        
        self._reset_sequence()
        self.detail_count = 0
        self.total_amount = 0.0
        lines = []
        
        # Header Arquivo
        lines.append(self.generate_header_arquivo(file_date, file_seq))
        
        # Header Lote
        lines.append(self.generate_header_lote(file_date, file_seq, tipo_servico))
        
        # Detalhes (Segmento A + Segmento B para cada pagamento TED/DOC)
        seq_detail = 1
        for pagamento in pagamentos:
            # Segmento A (passa file_date para validação da data de pagamento)
            seq_a = seq_detail
            lines.append(self.generate_segmento_a(pagamento, seq_a, file_date))
            seq_detail += 1
            
            # Segmento B (passa file_date para garantir consistência de datas)
            seq_b = seq_detail
            lines.append(self.generate_segmento_b(pagamento, seq_b, file_date))
            seq_detail += 1
            
            # Atualiza contadores
            self.detail_count += 1
            valor = float(pagamento.get('valor', 0))
            self.total_amount += valor
        
        # Trailer Lote
        total_registros_lote = 1 + (self.detail_count * 2) + 1
        lines.append(self.generate_trailer_lote(
            total_registros_lote,
            self.detail_count,
            self.total_amount
        ))
        
        # Trailer Arquivo
        total_registros_arquivo = 1 + total_registros_lote + 1
        lines.append(self.generate_trailer_arquivo(total_registros_arquivo))
        
        return lines

