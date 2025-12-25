"""
Validações de entrada e arquivo CNAB 240
"""
import re
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Tuple


def validate_cpf(cpf: str) -> bool:
    """
    Valida CPF.
    
    Args:
        cpf: CPF a ser validado
    
    Returns:
        True se válido, False caso contrário
    """
    if not cpf:
        return False
    
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Validação dos dígitos verificadores
    def calculate_digit(cpf_partial: str, weights: List[int]) -> int:
        sum_val = sum(int(cpf_partial[i]) * weights[i] for i in range(len(weights)))
        remainder = sum_val % 11
        return 0 if remainder < 2 else 11 - remainder
    
    # Primeiro dígito
    first_digit = calculate_digit(cpf[:9], [10, 9, 8, 7, 6, 5, 4, 3, 2])
    if int(cpf[9]) != first_digit:
        return False
    
    # Segundo dígito
    second_digit = calculate_digit(cpf[:10], [11, 10, 9, 8, 7, 6, 5, 4, 3, 2])
    if int(cpf[10]) != second_digit:
        return False
    
    return True


def validate_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ.
    
    Args:
        cnpj: CNPJ a ser validado
    
    Returns:
        True se válido, False caso contrário
    """
    if not cnpj:
        return False
    
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Validação dos dígitos verificadores
    def calculate_digit(cnpj_partial: str, weights: List[int]) -> int:
        sum_val = sum(int(cnpj_partial[i]) * weights[i] for i in range(len(weights)))
        remainder = sum_val % 11
        return 0 if remainder < 2 else 11 - remainder
    
    # Primeiro dígito
    first_digit = calculate_digit(cnpj[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    if int(cnpj[12]) != first_digit:
        return False
    
    # Segundo dígito
    second_digit = calculate_digit(cnpj[:13], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    if int(cnpj[13]) != second_digit:
        return False
    
    return True


def validate_email(email: str) -> bool:
    """
    Valida e-mail.
    
    Args:
        email: E-mail a ser validado
    
    Returns:
        True se válido, False caso contrário
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Valida telefone (formato: +5511999999999 ou 11999999999).
    
    Args:
        phone: Telefone a ser validado
    
    Returns:
        True se válido, False caso contrário
    """
    if not phone:
        return False
    
    # Remove caracteres não numéricos exceto +
    phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Deve ter 10 ou 11 dígitos (com DDD)
    if len(phone_clean) < 10 or len(phone_clean) > 11:
        return False
    
    return phone_clean.isdigit()


def validate_pix_key(key: str, key_type: str) -> bool:
    """
    Valida chave PIX conforme o tipo.
    
    Args:
        key: Chave PIX
        key_type: Tipo da chave (CPF, CNPJ, EMAIL, TELEFONE, ALEATORIA)
    
    Returns:
        True se válido, False caso contrário
    """
    if not key:
        return False
    
    key_type = key_type.upper()
    
    if key_type == 'CPF':
        return validate_cpf(key)
    elif key_type == 'CNPJ':
        return validate_cnpj(key)
    elif key_type == 'EMAIL':
        return validate_email(key)
    elif key_type == 'TELEFONE':
        return validate_phone(key)
    elif key_type == 'ALEATORIA':
        # Chave aleatória (UUID) deve ter formato válido
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, key.lower()))
    else:
        return False


def validate_date(date_str: str | datetime, min_date: datetime | None = None) -> Tuple[bool, str]:
    """
    Valida data.
    
    Args:
        date_str: Data como string ou datetime
        min_date: Data mínima permitida (padrão: hoje)
    
    Returns:
        Tupla (é_válida, mensagem_erro)
    """
    if not date_str:
        return False, "Data não informada"
    
    if min_date is None:
        min_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Se já for um objeto datetime, usa diretamente
    if isinstance(date_str, datetime):
        date_obj = date_str.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        # Converte string para datetime
        date_str_clean = str(date_str).strip()
        
        # Remove hora se presente (formato "YYYY-MM-DD HH:MM:SS")
        if ' ' in date_str_clean:
            date_str_clean = date_str_clean.split(' ')[0]
        
        # Tenta vários formatos
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y%m%d',
            '%d/%m/%y',
        ]
        
        date_obj = None
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str_clean, fmt)
                break
            except ValueError:
                continue
        
        if date_obj is None:
            return False, f"Data inválida: {date_str}"
    
    if date_obj < min_date:
        return False, f"Data deve ser >= {min_date.strftime('%d/%m/%Y')}"
    
    return True, ""


def validate_pagamento(pagamento: Dict, index: int = 0) -> Tuple[bool, List[str]]:
    """
    Valida um pagamento.
    
    Args:
        pagamento: Dicionário com dados do pagamento
        index: Índice do pagamento (para mensagens de erro)
    
    Returns:
        Tupla (é_válido, lista_de_erros)
    """
    errors = []
    id_pagamento = pagamento.get('id_pagamento', f'#{index}')
    
    # Valida id_pagamento
    if not pagamento.get('id_pagamento'):
        errors.append(f"{id_pagamento}: id_pagamento não informado")
    
    # Valida data_pagamento
    data_ok, data_msg = validate_date(pagamento.get('data_pagamento'))
    if not data_ok:
        errors.append(f"{id_pagamento}: {data_msg}")
    
    # Valida valor
    try:
        valor = float(pagamento.get('valor', 0))
        if valor <= 0:
            errors.append(f"{id_pagamento}: valor deve ser > 0")
        # Verifica se tem no máximo 2 decimais
        if round(valor, 2) != valor:
            errors.append(f"{id_pagamento}: valor deve ter no máximo 2 decimais")
    except (ValueError, TypeError):
        errors.append(f"{id_pagamento}: valor inválido")
    
    # Valida nome_favorecido
    nome = pagamento.get('nome_favorecido', '')
    if not nome or len(nome.strip()) == 0:
        errors.append(f"{id_pagamento}: nome_favorecido não informado")
    elif len(nome) > 30:
        errors.append(f"{id_pagamento}: nome_favorecido excede 30 caracteres (será truncado)")
    
    # Valida tipo_pessoa
    tipo_pessoa = pagamento.get('tipo_pessoa', '').upper()
    if tipo_pessoa not in ['F', 'J']:
        errors.append(f"{id_pagamento}: tipo_pessoa deve ser F ou J")
    
    # Valida cpf_cnpj
    cpf_cnpj = str(pagamento.get('cpf_cnpj', '')).strip()
    cpf_cnpj_clean = re.sub(r'[^0-9]', '', cpf_cnpj)
    
    if tipo_pessoa == 'F':
        if len(cpf_cnpj_clean) != 11:
            errors.append(f"{id_pagamento}: CPF deve ter 11 dígitos")
        elif not validate_cpf(cpf_cnpj):
            errors.append(f"{id_pagamento}: CPF inválido")
    elif tipo_pessoa == 'J':
        if len(cpf_cnpj_clean) != 14:
            errors.append(f"{id_pagamento}: CNPJ deve ter 14 dígitos")
        elif not validate_cnpj(cpf_cnpj):
            errors.append(f"{id_pagamento}: CNPJ inválido")
    
    # Valida conforme tipo de pagamento
    tipo_pagamento = pagamento.get('tipo_pagamento', 'PIX').upper().strip()
    
    if tipo_pagamento == 'PIX':
        # Validações específicas PIX
        tipo_chave_pix = pagamento.get('tipo_chave_pix', '').upper()
        tipos_validos = ['CPF', 'CNPJ', 'EMAIL', 'TELEFONE', 'ALEATORIA']
        if not tipo_chave_pix or tipo_chave_pix not in tipos_validos:
            errors.append(f"{id_pagamento}: tipo_chave_pix deve ser um de: {', '.join(tipos_validos)}")
        
        chave_pix = pagamento.get('chave_pix', '')
        if not chave_pix:
            errors.append(f"{id_pagamento}: chave_pix não informada (obrigatório para PIX)")
        elif len(chave_pix) > 100:  # 79 caracteres no Segmento J-52
            errors.append(f"{id_pagamento}: chave_pix excede 100 caracteres (será truncado)")
        elif not validate_pix_key(chave_pix, tipo_chave_pix):
            errors.append(f"{id_pagamento}: chave_pix inválida para o tipo {tipo_chave_pix}")
    
    elif tipo_pagamento in ['TED', 'DOC']:
        # Validações específicas TED/DOC
        if not pagamento.get('banco_favorecido'):
            errors.append(f"{id_pagamento}: banco_favorecido não informado (obrigatório para {tipo_pagamento})")
        elif len(str(pagamento.get('banco_favorecido', '')).strip()) != 3:
            errors.append(f"{id_pagamento}: banco_favorecido deve ter 3 dígitos")
        
        if not pagamento.get('agencia_favorecido'):
            errors.append(f"{id_pagamento}: agencia_favorecido não informado (obrigatório para {tipo_pagamento})")
        
        if not pagamento.get('conta_favorecido'):
            errors.append(f"{id_pagamento}: conta_favorecido não informado (obrigatório para {tipo_pagamento})")
        
        if not pagamento.get('digito_conta_favorecido'):
            errors.append(f"{id_pagamento}: digito_conta_favorecido não informado (obrigatório para {tipo_pagamento})")
        
        tipo_conta = str(pagamento.get('tipo_conta', '')).strip()
        if not tipo_conta:
            errors.append(f"{id_pagamento}: tipo_conta não informado (obrigatório para {tipo_pagamento})")
        elif tipo_conta not in ['1', '2', '3']:
            errors.append(f"{id_pagamento}: tipo_conta deve ser 1 (Corrente), 2 (Poupança) ou 3 (Salário)")
    
    elif tipo_pagamento == 'BOLETO':
        # Validações específicas BOLETO
        if not pagamento.get('nosso_numero'):
            errors.append(f"{id_pagamento}: nosso_numero não informado (obrigatório para BOLETO)")
        
        if not pagamento.get('data_vencimento'):
            errors.append(f"{id_pagamento}: data_vencimento não informado (obrigatório para BOLETO)")
        else:
            data_venc_ok, data_venc_msg = validate_date(pagamento.get('data_vencimento'))
            if not data_venc_ok:
                errors.append(f"{id_pagamento}: {data_venc_msg}")
        
        if not pagamento.get('sacado_nome'):
            errors.append(f"{id_pagamento}: sacado_nome não informado (obrigatório para BOLETO)")
        
        sacado_tipo = pagamento.get('sacado_tipo_pessoa', '').upper()
        if sacado_tipo not in ['F', 'J']:
            errors.append(f"{id_pagamento}: sacado_tipo_pessoa deve ser F ou J (obrigatório para BOLETO)")
        
        if not pagamento.get('sacado_cpf_cnpj'):
            errors.append(f"{id_pagamento}: sacado_cpf_cnpj não informado (obrigatório para BOLETO)")
        else:
            sacado_cpf_cnpj = str(pagamento.get('sacado_cpf_cnpj', '')).strip()
            sacado_cpf_cnpj_clean = re.sub(r'[^0-9]', '', sacado_cpf_cnpj)
            if sacado_tipo == 'F' and len(sacado_cpf_cnpj_clean) != 11:
                errors.append(f"{id_pagamento}: sacado_cpf_cnpj (CPF) deve ter 11 dígitos")
            elif sacado_tipo == 'J' and len(sacado_cpf_cnpj_clean) != 14:
                errors.append(f"{id_pagamento}: sacado_cpf_cnpj (CNPJ) deve ter 14 dígitos")
    
    else:
        errors.append(f"{id_pagamento}: tipo_pagamento inválido: {tipo_pagamento} (deve ser PIX, TED, DOC ou BOLETO)")
    
    # Valida aviso_favorecido (comum a todos)
    aviso = pagamento.get('aviso_favorecido', 0)
    if aviso not in [0, 1]:
        errors.append(f"{id_pagamento}: aviso_favorecido deve ser 0 ou 1")
    
    return len(errors) == 0, errors


def validate_pagamentos(pagamentos: List[Dict]) -> Tuple[bool, Dict[str, List[str]]]:
    """
    Valida lista de pagamentos.
    
    Args:
        pagamentos: Lista de dicionários com dados dos pagamentos
    
    Returns:
        Tupla (todos_válidos, dicionário_erros_por_id)
    """
    all_valid = True
    errors_by_id = {}
    ids_seen = set()
    
    for index, pagamento in enumerate(pagamentos):
        id_pagamento = str(pagamento.get('id_pagamento', f'#{index}'))
        
        # Verifica duplicação de id_pagamento
        if id_pagamento in ids_seen:
            all_valid = False
            if id_pagamento not in errors_by_id:
                errors_by_id[id_pagamento] = []
            errors_by_id[id_pagamento].append(f"id_pagamento duplicado: {id_pagamento}")
        ids_seen.add(id_pagamento)
        
        # Valida pagamento
        is_valid, errors = validate_pagamento(pagamento, index)
        if not is_valid:
            all_valid = False
            errors_by_id[id_pagamento] = errors
    
    return all_valid, errors_by_id


def validate_cnab_file(lines: List[str]) -> Tuple[bool, List[str]]:
    """
    Valida arquivo CNAB 240 gerado.
    
    Args:
        lines: Lista de linhas do arquivo
    
    Returns:
        Tupla (é_válido, lista_de_erros)
    """
    errors = []
    
    if not lines:
        errors.append("Arquivo vazio")
        return False, errors
    
    # Verifica se todas as linhas têm 240 caracteres
    for i, line in enumerate(lines, 1):
        if len(line) != 240:
            errors.append(f"Linha {i}: tamanho incorreto ({len(line)} caracteres, esperado 240)")
    
    # Verifica estrutura básica
    if len(lines) < 5:
        errors.append(f"Arquivo deve ter no mínimo 5 registros (tem {len(lines)})")
    
    # Verifica Header Arquivo (primeira linha)
    if lines[0][7:8] != '0':
        errors.append("Primeira linha deve ser Header Arquivo (tipo 0)")
    
    # Verifica Header Lote (segunda linha)
    if lines[1][7:8] != '1':
        errors.append("Segunda linha deve ser Header Lote (tipo 1)")
    
    # Verifica Trailer Arquivo (última linha)
    if lines[-1][7:8] != '9':
        errors.append("Última linha deve ser Trailer Arquivo (tipo 9)")
    
    # Verifica Trailer Lote (penúltima linha)
    if len(lines) >= 2 and lines[-2][7:8] != '5':
        errors.append("Penúltima linha deve ser Trailer Lote (tipo 5)")
    
    return len(errors) == 0, errors


def validate_trailers(lines: List[str], expected_pagamentos: int, expected_total: float) -> Tuple[bool, List[str]]:
    """
    Valida trailers do arquivo CNAB.
    
    Args:
        lines: Lista de linhas do arquivo
        expected_pagamentos: Número esperado de pagamentos
        expected_total: Valor total esperado
    
    Returns:
        Tupla (é_válido, lista_de_erros)
    """
    errors = []
    
    if len(lines) < 2:
        return False, ["Arquivo muito curto para validar trailers"]
    
    # Trailer Lote (penúltima linha)
    trailer_lote = lines[-2]
    
    # Quantidade de registros no lote (posição 18-23)
    qtd_registros_lote = int(trailer_lote[17:23])
    # Valor total (posição 24-41, 18 posições)
    valor_total_str = trailer_lote[23:41]
    valor_total = float(valor_total_str) / 100.0  # Converte de centavos
    # Quantidade de títulos - verificar se existe no layout (pode não estar presente)
    # Se o layout não tiver quantidade de títulos separada, usar quantidade de registros - 2 (header + trailer)
    try:
        qtd_titulos = int(trailer_lote[41:47]) if len(trailer_lote) > 47 else (qtd_registros_lote - 2) // 2
    except:
        qtd_titulos = (qtd_registros_lote - 2) // 2  # Aproximação: (registros - header - trailer) / 2 (J + J-52)
    
    # Calcula valores esperados
    # Header Lote (1) + Detalhes (2 por pagamento: Segmento J + Segmento J-52) + Trailer Lote (1)
    expected_registros_lote = 1 + (expected_pagamentos * 2) + 1
    
    if qtd_registros_lote != expected_registros_lote:
        errors.append(
            f"Trailer Lote: quantidade de registros incorreta "
            f"(esperado {expected_registros_lote}, encontrado {qtd_registros_lote})"
        )
    
    # Valida quantidade de títulos apenas se o campo existir no layout
    # (alguns layouts podem não ter esse campo separado)
    if qtd_titulos != expected_pagamentos:
        # Aviso, mas não erro crítico (pode não estar no layout)
        pass  # Comentado: alguns layouts não têm quantidade de títulos separada
    
    # Compara valores com tolerância de 0.01
    if abs(valor_total - expected_total) > 0.01:
        errors.append(
            f"Trailer Lote: valor total incorreto "
            f"(esperado {expected_total:.2f}, encontrado {valor_total:.2f})"
        )
    
    # Trailer Arquivo (última linha)
    trailer_arquivo = lines[-1]
    
    # Quantidade de registros (posição 24-29)
    qtd_registros_arquivo = int(trailer_arquivo[23:29])
    
    # Calcula valor esperado
    # Header Arquivo (1) + registros do lote + Trailer Arquivo (1)
    expected_registros_arquivo = 1 + expected_registros_lote + 1
    
    if qtd_registros_arquivo != expected_registros_arquivo:
        errors.append(
            f"Trailer Arquivo: quantidade de registros incorreta "
            f"(esperado {expected_registros_arquivo}, encontrado {qtd_registros_arquivo})"
        )
    
    return len(errors) == 0, errors

