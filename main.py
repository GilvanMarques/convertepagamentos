#!/usr/bin/env python3
"""
Gerador de REMESSA CNAB 240 para PAGAMENTO PIX via Bradesco Multipag
"""
import sys
import os
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

try:
    import pandas as pd
except ImportError:
    print("Instalando pandas...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import pandas as pd

from src.cnab240.bradesco_pix import BradescoPIXGenerator
from src.cnab240.bradesco_ted import BradescoTEDGenerator
from src.cnab240 import validate
from src.cnab240.fields import sanitize_text

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def read_excel(file_path: str) -> List[Dict]:
    """
    Lê arquivo Excel e retorna lista de pagamentos.
    
    Args:
        file_path: Caminho para o arquivo Excel
    
    Returns:
        Lista de dicionários com dados dos pagamentos
    """
    try:
        # Lê a primeira aba
        df = pd.read_excel(file_path, sheet_name=0)
        
        # Normaliza nomes das colunas (remove espaços, converte para minúsculas)
        df.columns = df.columns.str.strip().str.lower()
        
        # Mapeia colunas esperadas
        pagamentos = []
        for index, row in df.iterrows():
            # Trata data_pagamento (pode vir como datetime do Excel)
            data_pagamento = row.get('data_pagamento', '')
            if pd.notna(data_pagamento):
                if isinstance(data_pagamento, datetime):
                    # Se for datetime, converte para string no formato YYYY-MM-DD
                    data_pagamento = data_pagamento.strftime('%Y-%m-%d')
                else:
                    data_pagamento = str(data_pagamento).strip()
            else:
                data_pagamento = ''
            
            # Trata data_vencimento (para boleto)
            data_vencimento = row.get('data_vencimento', '')
            if pd.notna(data_vencimento):
                if isinstance(data_vencimento, datetime):
                    data_vencimento = data_vencimento.strftime('%Y-%m-%d')
                else:
                    data_vencimento = str(data_vencimento).strip()
            else:
                data_vencimento = ''
            
            # Limpa valores numéricos que podem vir como float
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
                'tipo_conta': clean_numeric(row.get('tipo_conta', '')),
                'endereco_favorecido': str(row.get('endereco_favorecido', '')).strip() if pd.notna(row.get('endereco_favorecido')) else '',
                'numero_endereco': str(row.get('numero_endereco', '')).strip() if pd.notna(row.get('numero_endereco')) else '',
                'complemento_endereco': str(row.get('complemento_endereco', '')).strip() if pd.notna(row.get('complemento_endereco')) else '',
                'bairro_favorecido': str(row.get('bairro_favorecido', '')).strip() if pd.notna(row.get('bairro_favorecido')) else '',
                'cidade_favorecido': str(row.get('cidade_favorecido', '')).strip() if pd.notna(row.get('cidade_favorecido')) else '',
                'cep_favorecido': clean_numeric(row.get('cep_favorecido', '')),
                'estado_favorecido': str(row.get('estado_favorecido', '')).strip().upper() if pd.notna(row.get('estado_favorecido')) else '',
                'finalidade_ted': clean_numeric(row.get('finalidade_ted', '')),
                # Campos BOLETO
                'nosso_numero': clean_numeric(row.get('nosso_numero', '')),
                'data_vencimento': data_vencimento,
                'valor_titulo': float(row.get('valor_titulo', row.get('valor', 0))) if pd.notna(row.get('valor_titulo', row.get('valor'))) else float(row.get('valor', 0)),
                'valor_desconto': float(row.get('valor_desconto', 0)) if pd.notna(row.get('valor_desconto')) else 0.0,
                'valor_multa': float(row.get('valor_multa', 0)) if pd.notna(row.get('valor_multa')) else 0.0,
                'valor_juros': float(row.get('valor_juros', 0)) if pd.notna(row.get('valor_juros')) else 0.0,
                'codigo_barras': str(row.get('codigo_barras', '')).strip() if pd.notna(row.get('codigo_barras')) else '',
                'linha_digitavel': str(row.get('linha_digitavel', '')).strip() if pd.notna(row.get('linha_digitavel')) else '',
                'sacado_nome': str(row.get('sacado_nome', '')).strip() if pd.notna(row.get('sacado_nome')) else '',
                'sacado_tipo_pessoa': str(row.get('sacado_tipo_pessoa', 'F')).strip().upper() if pd.notna(row.get('sacado_tipo_pessoa')) else 'F',
                'sacado_cpf_cnpj': clean_numeric(row.get('sacado_cpf_cnpj', '')),
                'sacado_endereco': str(row.get('sacado_endereco', '')).strip() if pd.notna(row.get('sacado_endereco')) else '',
                'sacado_cidade': str(row.get('sacado_cidade', '')).strip() if pd.notna(row.get('sacado_cidade')) else '',
                'sacado_cep': clean_numeric(row.get('sacado_cep', '')),
                'sacado_estado': str(row.get('sacado_estado', '')).strip().upper() if pd.notna(row.get('sacado_estado')) else '',
                'instrucoes': str(row.get('instrucoes', '')).strip() if pd.notna(row.get('instrucoes')) else '',
                'especie_titulo': str(row.get('especie_titulo', '')).strip() if pd.notna(row.get('especie_titulo')) else '',
                # Campos comuns
                'descricao_pagamento': str(row.get('descricao_pagamento', '')).strip() if pd.notna(row.get('descricao_pagamento')) else '',
                'aviso_favorecido': int(row.get('aviso_favorecido', 0)) if pd.notna(row.get('aviso_favorecido')) else 0,
            }
            pagamentos.append(pagamento)
        
        logger.info(f"Lidos {len(pagamentos)} pagamentos do arquivo Excel")
        return pagamentos
    
    except Exception as e:
        logger.error(f"Erro ao ler arquivo Excel: {e}")
        raise


def truncate_fields(pagamentos: List[Dict]) -> List[Dict]:
    """
    Trunca campos que excedem o tamanho permitido e registra no log.
    
    Args:
        pagamentos: Lista de pagamentos
    
    Returns:
        Lista de pagamentos com campos truncados
    """
    for pagamento in pagamentos:
        id_pag = pagamento.get('id_pagamento', '')
        
        # Trunca nome_favorecido (máximo 30 caracteres)
        nome = pagamento.get('nome_favorecido', '')
        if len(nome) > 30:
            nome_original = nome
            nome = nome[:30]
            pagamento['nome_favorecido'] = nome
            logger.warning(f"{id_pag}: nome_favorecido truncado de {len(nome_original)} para 30 caracteres")
        
        # Trunca chave_pix (máximo 100 caracteres - 5 campos de 20 no Segmento J-52)
        chave = pagamento.get('chave_pix', '')
        if len(chave) > 100:
            chave_original = chave
            chave = chave[:100]
            pagamento['chave_pix'] = chave
            logger.warning(f"{id_pag}: chave_pix truncada de {len(chave_original)} para 100 caracteres")
    
    return pagamentos


def generate_report(pagamentos: List[Dict], errors_by_id: Dict[str, List[str]], 
                   output_dir: Path) -> str:
    """
    Gera relatório de validação em CSV.
    
    Args:
        pagamentos: Lista de pagamentos
        errors_by_id: Dicionário com erros por id_pagamento
        output_dir: Diretório de saída
    
    Returns:
        Caminho do arquivo de relatório gerado
    """
    report_path = output_dir / 'relatorio_validacao.csv'
    
    with open(report_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['id_pagamento', 'status', 'erros'])
        
        for pagamento in pagamentos:
            id_pag = str(pagamento.get('id_pagamento', ''))
            if id_pag in errors_by_id:
                status = 'ERRO'
                erros = ' | '.join(errors_by_id[id_pag])
            else:
                status = 'OK'
                erros = ''
            
            writer.writerow([id_pag, status, erros])
    
    logger.info(f"Relatório de validação salvo em: {report_path}")
    return str(report_path)


def main():
    """Função principal"""
    # Configura caminhos
    base_dir = Path(__file__).parent
    excel_path = base_dir / 'Pagamentos_Excel.xlsx'
    config_path = base_dir / 'config' / 'bradesco.yaml'
    output_dir = base_dir / 'output'
    
    # Cria diretório de saída se não existir
    output_dir.mkdir(exist_ok=True)
    
    # Verifica se arquivo Excel existe
    if not excel_path.exists():
        logger.error(f"Arquivo Excel não encontrado: {excel_path}")
        sys.exit(1)
    
    # Verifica se arquivo de configuração existe
    if not config_path.exists():
        logger.error(f"Arquivo de configuração não encontrado: {config_path}")
        logger.error("Por favor, crie o arquivo config/bradesco.yaml com os dados da empresa e conta")
        sys.exit(1)
    
    try:
        # Lê pagamentos do Excel
        logger.info(f"Lendo arquivo Excel: {excel_path}")
        pagamentos = read_excel(str(excel_path))
        
        if not pagamentos:
            logger.error("Nenhum pagamento encontrado no arquivo Excel")
            sys.exit(1)
        
        # Trunca campos que excedem tamanho
        pagamentos = truncate_fields(pagamentos)
        
        # Valida pagamentos
        logger.info("Validando pagamentos...")
        all_valid, errors_by_id = validate.validate_pagamentos(pagamentos)
        
        # Gera relatório de validação
        generate_report(pagamentos, errors_by_id, output_dir)
        
        if not all_valid:
            logger.warning("Foram encontrados erros na validação. Verifique o relatório.")
            logger.warning("O arquivo CNAB será gerado apenas com os pagamentos válidos.")
            # Filtra apenas pagamentos válidos
            pagamentos = [p for p in pagamentos if str(p.get('id_pagamento', '')) not in errors_by_id]
        
        if not pagamentos:
            logger.error("Nenhum pagamento válido para processar")
            sys.exit(1)
        
        # Agrupa pagamentos por tipo
        pagamentos_por_tipo = {}
        for pagamento in pagamentos:
            tipo = pagamento.get('tipo_pagamento', 'PIX').upper().strip()
            if tipo not in pagamentos_por_tipo:
                pagamentos_por_tipo[tipo] = []
            pagamentos_por_tipo[tipo].append(pagamento)
        
        logger.info(f"Pagamentos agrupados por tipo: {dict((k, len(v)) for k, v in pagamentos_por_tipo.items())}")
        
        file_date = datetime.now()
        arquivos_gerados = []
        
        # Processa cada tipo de pagamento
        for tipo, pagamentos_tipo in pagamentos_por_tipo.items():
            logger.info(f"\nProcessando {len(pagamentos_tipo)} pagamento(s) do tipo {tipo}...")
            
            if tipo == 'PIX':
                # Gera arquivo PIX
                generator = BradescoPIXGenerator(str(config_path))
                file_seq = generator.config.get('arquivo', {}).get('sequencial_inicial', 1)
                lines = generator.generate_file(pagamentos_tipo, file_date, file_seq)
                tipo_arquivo = 'PIX'
            
            elif tipo in ['TED', 'DOC']:
                # Gera arquivo TED/DOC
                generator = BradescoTEDGenerator(str(config_path))
                file_seq = generator.config.get('arquivo', {}).get('sequencial_inicial', 1)
                lines = generator.generate_file(pagamentos_tipo, file_date, file_seq, tipo)
                tipo_arquivo = tipo
            
            else:
                logger.warning(f"Tipo de pagamento '{tipo}' ainda não implementado. Pulando...")
                continue
            
            # Valida arquivo gerado
            logger.info(f"Validando arquivo CNAB 240 para {tipo}...")
            file_valid, file_errors = validate.validate_cnab_file(lines)
            
            if not file_valid:
                logger.error(f"Erros na validação do arquivo CNAB para {tipo}:")
                for error in file_errors:
                    logger.error(f"  - {error}")
                continue
            
            # Valida trailers
            total_pagamentos_tipo = len(pagamentos_tipo)
            total_valor_tipo = sum(float(p.get('valor', 0)) for p in pagamentos_tipo)
            
            trailers_valid, trailer_errors = validate.validate_trailers(lines, total_pagamentos_tipo, total_valor_tipo)
            
            if not trailers_valid:
                logger.error(f"Erros na validação dos trailers para {tipo}:")
                for error in trailer_errors:
                    logger.error(f"  - {error}")
                continue
            
            # Salva arquivo
            filename = f"BRADESCO_{tipo_arquivo}_REMESSA_{file_date.strftime('%Y%m%d')}_{file_seq:06d}.txt"
            file_path = output_dir / filename
            
            with open(file_path, 'w', encoding='ascii') as f:
                for line in lines:
                    f.write(line + '\r\n')  # CRLF
            
            arquivos_gerados.append({
                'tipo': tipo,
                'arquivo': file_path,
                'pagamentos': total_pagamentos_tipo,
                'registros': len(lines),
                'valor': total_valor_tipo
            })
            
            logger.info(f"✅ Arquivo {tipo} gerado: {file_path}")
            logger.info(f"   Pagamentos: {total_pagamentos_tipo}, Registros: {len(lines)}, Valor: R$ {total_valor_tipo:,.2f}")
        
        # Log de resumo final
        logger.info("\n" + "=" * 60)
        logger.info("PROCESSAMENTO CONCLUÍDO")
        logger.info("=" * 60)
        logger.info(f"Total de arquivos gerados: {len(arquivos_gerados)}")
        for info in arquivos_gerados:
            logger.info(f"  - {info['tipo']}: {info['arquivo'].name}")
            logger.info(f"    {info['pagamentos']} pagamento(s), {info['registros']} registro(s), R$ {info['valor']:,.2f}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Erro ao processar: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

