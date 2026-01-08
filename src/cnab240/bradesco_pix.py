"""
Geração de arquivo CNAB 240 para PIX Bradesco Multipag
Utiliza Segmento J e J-52 (não Segmento A/B)
"""
import uuid
from datetime import datetime
from typing import List, Dict
from . import fields
from .config import load_config


# Mapeamento de tipos de chave PIX
PIX_KEY_TYPE_MAP = {
    'CPF': '1',
    'CNPJ': '2',
    'EMAIL': '3',
    'TELEFONE': '4',
    'ALEATORIA': '5',
}


class BradescoPIXGenerator:
    """Gerador de arquivo CNAB 240 para PIX Bradesco"""
    
    def __init__(self, config_path: str | None = None):
        """
        Inicializa o gerador com a configuração.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config = load_config(config_path)
        self.records = []
        self.sequence = 0
        self.detail_count = 0
        self.total_amount = 0.0
        
    def _get_sequence(self) -> int:
        """Retorna próximo número sequencial"""
        self.sequence += 1
        return self.sequence
    
    def _reset_sequence(self):
        """Reseta o contador sequencial"""
        self.sequence = 0
    
    def generate_header_arquivo(self, file_date: datetime, file_seq: int) -> str:
        """
        Gera registro Header Arquivo (Registro 0).
        
        Args:
            file_date: Data de geração do arquivo
            file_seq: Número sequencial do arquivo
        
        Returns:
            Linha do header arquivo (240 caracteres)
        """
        empresa = self.config['empresa']
        conta = self.config['conta']
        arquivo_config = self.config.get('arquivo', {})
        # Layout do Arquivo para PIX Multipag: 089 (conforme especificação)
        # O sistema Bradesco Multipag exige 089 para arquivos de pagamento
        # SEMPRE usar 089 para Multipag, independente do config
        layout_arquivo = 89  # Multipag exige 089 (forçado)
        
        line = ''
        line += fields.format_numeric(237, 3)  # Código do Banco
        line += fields.format_numeric(0, 4)  # Lote de Serviço (0000)
        line += fields.format_numeric(0, 1)  # Tipo de Registro
        line += fields.format_alphanumeric('', 9)  # Filler
        line += fields.format_numeric(empresa['tipo_inscricao'], 1)  # Tipo de Inscrição
        line += fields.format_numeric(empresa['numero_inscricao'], 14)  # Número de Inscrição
        line += fields.format_alphanumeric(conta['codigo_convenio'], 20)  # Código do Convênio
        line += fields.format_numeric(conta['agencia'], 5)  # Agência Mantenedora
        line += fields.format_alphanumeric(conta['digito_agencia'], 1)  # Dígito da Agência
        line += fields.format_numeric(conta['conta'], 12)  # Conta Corrente
        line += fields.format_alphanumeric(conta['digito_conta'], 1)  # Dígito da Conta
        line += fields.format_alphanumeric(conta.get('digito_verificador', ''), 1)  # DV Ag/Conta
        line += fields.format_alphanumeric(empresa['nome'], 30)  # Nome da Empresa
        line += fields.format_alphanumeric('BRADESCO', 30)  # Nome do Banco
        line += fields.format_alphanumeric('', 10)  # Filler
        line += fields.format_numeric(1, 1)  # Código Remessa/Retorno (1=Remessa)
        line += fields.format_date(file_date)  # Data de Geração
        line += fields.format_time(file_date)  # Hora de Geração
        line += fields.format_numeric(file_seq, 6)  # Número Sequencial
        line += fields.format_numeric(layout_arquivo, 3)  # Layout do Arquivo (089)
        line += fields.format_numeric(1600, 5)  # Densidade (01600)
        line += fields.format_alphanumeric('', 20)  # Reservado Banco
        line += fields.format_alphanumeric('', 20)  # Reservado Empresa
        line += fields.format_alphanumeric('', 6)  # Versão Aplicativo
        line += fields.format_alphanumeric('', 23)  # Filler
        
        return fields.ensure_length_240(line)
    
    def generate_header_lote(self, file_date: datetime, remessa_seq: int) -> str:
        """
        Gera registro Header Lote (Registro 1).
        
        Args:
            file_date: Data de geração do arquivo
            remessa_seq: Número sequencial da remessa
        
        Returns:
            Linha do header lote (240 caracteres)
        """
        empresa = self.config['empresa']
        conta = self.config['conta']
        arquivo_config = self.config.get('arquivo', {})
        layout_lote = arquivo_config.get('layout_lote', 12)  # Padrão 012
        # Garante que seja tratado como número (pode vir como string do YAML)
        if isinstance(layout_lote, str):
            layout_lote = int(layout_lote)
        
        line = ''
        line += fields.format_numeric(237, 3)  # Código do Banco
        line += fields.format_numeric(1, 4)  # Lote de Serviço (0001)
        line += fields.format_numeric(1, 1)  # Tipo de Registro
        line += fields.format_alphanumeric('C', 1)  # Tipo de Operação
        line += fields.format_numeric(20, 2)  # Tipo de Serviço (20=Pagamentos)
        line += fields.format_numeric(41, 2)  # Forma de Lançamento (41=PIX)
        line += fields.format_numeric(layout_lote, 3)  # Layout do Lote (012)
        line += fields.format_alphanumeric('', 1)  # Filler
        line += fields.format_numeric(empresa['tipo_inscricao'], 1)  # Tipo de Inscrição
        line += fields.format_numeric(empresa['numero_inscricao'], 14)  # Número de Inscrição
        line += fields.format_alphanumeric(conta['codigo_convenio'], 20)  # Código do Convênio
        line += fields.format_numeric(conta['agencia'], 5)  # Agência Mantenedora
        line += fields.format_alphanumeric(conta['digito_agencia'], 1)  # Dígito da Agência
        line += fields.format_numeric(conta['conta'], 12)  # Conta Corrente
        line += fields.format_alphanumeric(conta['digito_conta'], 1)  # Dígito da Conta
        line += fields.format_alphanumeric(conta.get('digito_verificador', ''), 1)  # DV Ag/Conta
        line += fields.format_alphanumeric(empresa['nome'], 30)  # Nome da Empresa
        line += fields.format_alphanumeric('', 40)  # Mensagem 1
        line += fields.format_alphanumeric('', 40)  # Mensagem 2
        line += fields.format_numeric(remessa_seq, 9)  # Número Remessa/Retorno
        line += fields.format_date(file_date)  # Data de Gravação
        line += fields.format_alphanumeric('', 8)  # Data de Crédito (brancos)
        line += fields.format_alphanumeric('', 33)  # Filler
        
        return fields.ensure_length_240(line)
    
    def generate_segmento_j(self, pagamento: Dict, seq: int) -> str:
        """
        Gera registro Segmento J (Detalhe) para PIX.
        
        Args:
            pagamento: Dicionário com dados do pagamento
            seq: Número sequencial no lote
        
        Returns:
            Linha do segmento J (240 caracteres)
        """
        line = ''
        line += fields.format_numeric(237, 3)  # Código do Banco
        line += fields.format_numeric(1, 4)  # Lote de Serviço
        line += fields.format_numeric(3, 1)  # Tipo de Registro
        line += fields.format_numeric(seq, 5)  # Número Sequencial
        line += fields.format_alphanumeric('J', 1)  # Código Segmento
        line += fields.format_numeric(0, 1)  # Tipo de Movimento (0=Inclusão)
        line += fields.format_numeric(0, 2)  # Código da Instrução
        line += fields.format_alphanumeric('BRL', 3)  # Tipo da Moeda
        line += fields.format_numeric(0, 15)  # Quantidade de Moeda
        line += fields.format_amount(pagamento.get('valor'), 15)  # Valor do Pagamento
        line += fields.format_date(pagamento.get('data_pagamento'))  # Data do Vencimento
        line += fields.format_amount(pagamento.get('valor'), 15)  # Valor do Documento
        line += fields.format_numeric(0, 15)  # Valor do Desconto
        line += fields.format_numeric(0, 15)  # Valor da Multa
        line += fields.format_numeric(0, 15)  # Valor do Juros
        line += fields.format_date(pagamento.get('data_pagamento'))  # Data de Pagamento
        line += fields.format_numeric(0, 15)  # Quantidade de Moeda
        line += fields.format_alphanumeric(str(pagamento.get('id_pagamento', '')), 20)  # Número do Documento
        line += fields.format_alphanumeric('', 20)  # Número do Documento Atribuído
        line += fields.format_alphanumeric('', 20)  # Nosso Número
        line += fields.format_alphanumeric('', 33)  # Código de Barras
        line += fields.format_alphanumeric('', 6)  # Uso Exclusivo FEBRABAN
        
        return fields.ensure_length_240(line)
    
    def generate_segmento_j52(self, pagamento: Dict, seq: int) -> str:
        """
        Gera registro Segmento J-52 (Complemento PIX).
        OBRIGATÓRIO para cada pagamento PIX.
        Conforme documentação: posições conforme layout_pix_bradesco.md
        
        Args:
            pagamento: Dicionário com dados do pagamento
            seq: Número sequencial no lote
        
        Returns:
            Linha do segmento J-52 (240 caracteres)
        """
        empresa = self.config['empresa']
        
        # Mapeia tipo de pessoa do favorecido
        tipo_pessoa = pagamento.get('tipo_pessoa', 'F').upper()
        tipo_inscricao_fav = '1' if tipo_pessoa == 'F' else '2'
        
        # CPF/CNPJ do favorecido (apenas dígitos, zero-fill até 15)
        cpf_cnpj_fav = pagamento.get('cpf_cnpj', '')
        cpf_cnpj_fav_clean = ''.join(filter(str.isdigit, str(cpf_cnpj_fav)))
        
        # Chave PIX (posições 132-210, 79 caracteres)
        chave_pix = pagamento.get('chave_pix', '')
        if len(chave_pix) > 79:
            chave_pix = chave_pix[:79]
        
        # Gera TXID (posições 211-240, 30 caracteres)
        txid = pagamento.get('txid', '')
        if not txid:
            # Gera UUID sem hífens, maiúsculo, limitado a 30 caracteres
            txid = str(uuid.uuid4()).replace('-', '').upper()[:30]
        else:
            txid = str(txid).strip()[:30]
        
        # Código do movimento remessa (parametrizável, padrão 01)
        arquivo_config = self.config.get('arquivo', {})
        codigo_movimento = arquivo_config.get('codigo_movimento_remessa', 1)
        
        line = ''
        line += fields.format_numeric(237, 3)  # 1-3: Código do Banco
        line += fields.format_numeric(1, 4)  # 4-7: Lote de Serviço
        line += fields.format_numeric(3, 1)  # 8-8: Tipo de Registro
        line += fields.format_numeric(seq, 5)  # 9-13: Número Sequencial
        line += fields.format_alphanumeric('J', 1)  # 14-14: Código Segmento
        line += fields.format_alphanumeric('', 1)  # 15-15: CNAB (branco)
        line += fields.format_numeric(codigo_movimento, 2)  # 16-17: Código do Movimento Remessa
        line += fields.format_numeric(52, 2)  # 18-19: Identificação do Registro Opcional (52)
        
        # Devedor (empresa pagadora)
        line += fields.format_numeric(empresa['tipo_inscricao'], 1)  # 20-20: Devedor - Tipo de Inscrição
        devedor_inscricao = ''.join(filter(str.isdigit, str(empresa['numero_inscricao'])))
        line += fields.format_numeric(devedor_inscricao, 15)  # 21-35: Devedor - Número de Inscrição (15 posições)
        line += fields.format_alphanumeric(empresa['nome'], 40)  # 36-75: Devedor - Nome (40 posições)
        
        # Favorecido
        line += fields.format_numeric(tipo_inscricao_fav, 1)  # 76-76: Favorecido - Tipo de Inscrição
        line += fields.format_numeric(cpf_cnpj_fav_clean, 15)  # 77-91: Favorecido - Número de Inscrição (15 posições)
        nome_fav = pagamento.get('nome_favorecido', '')
        if len(nome_fav) > 40:
            nome_fav = nome_fav[:40]
        line += fields.format_alphanumeric(nome_fav, 40)  # 92-131: Favorecido - Nome (40 posições)
        
        # Chave PIX e TXID
        line += fields.format_alphanumeric(chave_pix, 79)  # 132-210: URL/Chave de Endereçamento (79 posições)
        line += fields.format_alphanumeric(txid, 30)  # 211-240: TXID (30 posições)
        
        return fields.ensure_length_240(line)
    
    def generate_trailer_lote(self, total_registros: int, total_titulos: int, total_valor: float) -> str:
        """
        Gera registro Trailer Lote (Registro 5).
        
        Args:
            total_registros: Total de registros no lote (incluindo header e trailer)
            total_titulos: Total de títulos/pagamentos
            total_valor: Soma dos valores dos pagamentos
        
        Returns:
            Linha do trailer lote (240 caracteres)
        """
        line = ''
        line += fields.format_numeric(237, 3)  # Código do Banco
        line += fields.format_numeric(1, 4)  # Lote de Serviço
        line += fields.format_numeric(5, 1)  # Tipo de Registro
        line += fields.format_alphanumeric('', 9)  # CNAB Reservado (9-17)
        line += fields.format_numeric(total_registros, 6)  # Quantidade de Registros (18-23)
        line += fields.format_amount(total_valor, 18)  # Somatória dos Valores (24-41, 18 posições)
        line += fields.format_alphanumeric('', 199)  # CNAB Reservado (42-240)
        
        return fields.ensure_length_240(line)
    
    def generate_trailer_arquivo(self, total_registros: int) -> str:
        """
        Gera registro Trailer Arquivo (Registro 9).
        
        Args:
            total_registros: Total de registros no arquivo
        
        Returns:
            Linha do trailer arquivo (240 caracteres)
        """
        line = ''
        line += fields.format_numeric(237, 3)  # Código do Banco
        line += fields.format_numeric(9999, 4)  # Lote de Serviço (9999)
        line += fields.format_numeric(9, 1)  # Tipo de Registro
        line += fields.format_alphanumeric('', 9)  # Filler
        line += fields.format_numeric(1, 6)  # Quantidade de Lotes (000001)
        line += fields.format_numeric(total_registros, 6)  # Quantidade de Registros
        line += fields.format_numeric(1, 6)  # Quantidade de Contas (000001)
        line += fields.format_alphanumeric('', 205)  # Filler
        
        return fields.ensure_length_240(line)
    
    def generate_file(self, pagamentos: List[Dict], file_date: datetime | None = None, 
                     file_seq: int = 1) -> List[str]:
        """
        Gera arquivo CNAB 240 completo usando Segmento J e J-52 para PIX.
        
        Args:
            pagamentos: Lista de dicionários com dados dos pagamentos
            file_date: Data de geração (usa data atual se None)
            file_seq: Número sequencial do arquivo
        
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
        lines.append(self.generate_header_lote(file_date, file_seq))
        
        # Detalhes (Segmento J + Segmento J-52 para cada pagamento PIX)
        seq_detail = 1
        for pagamento in pagamentos:
            # Segmento J
            seq_j = seq_detail
            lines.append(self.generate_segmento_j(pagamento, seq_j))
            seq_detail += 1
            
            # Segmento J-52 (OBRIGATÓRIO para PIX)
            seq_j52 = seq_detail
            lines.append(self.generate_segmento_j52(pagamento, seq_j52))
            seq_detail += 1
            
            # Atualiza contadores
            self.detail_count += 1
            valor = float(pagamento.get('valor', 0))
            self.total_amount += valor
        
        # Trailer Lote
        # Total de registros no lote: Header Lote (1) + Detalhes (2 por pagamento: J + J-52) + Trailer Lote (1)
        total_registros_lote = 1 + (self.detail_count * 2) + 1
        lines.append(self.generate_trailer_lote(
            total_registros_lote,
            self.detail_count,
            self.total_amount
        ))
        
        # Trailer Arquivo
        # Total de registros no arquivo: Header Arquivo (1) + registros do lote + Trailer Arquivo (1)
        total_registros_arquivo = 1 + total_registros_lote + 1
        lines.append(self.generate_trailer_arquivo(total_registros_arquivo))
        
        return lines
