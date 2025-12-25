"""
Formatadores de campos para CNAB 240
"""
import re
from datetime import datetime
from decimal import Decimal, ROUND_DOWN


def format_numeric(value: str | int | None, length: int, fill_char: str = '0') -> str:
    """
    Formata campo numérico preenchendo com zeros à esquerda.
    
    Args:
        value: Valor a ser formatado
        length: Tamanho total do campo
        fill_char: Caractere de preenchimento (padrão: '0')
    
    Returns:
        String formatada com o tamanho especificado
    """
    if value is None:
        value = ''
    
    # Remove caracteres não numéricos
    value_str = re.sub(r'[^0-9]', '', str(value))
    
    if not value_str:
        value_str = '0'
    
    # Preenche com zeros à esquerda
    return value_str.zfill(length)[:length]


def format_alphanumeric(value: str | None, length: int, fill_char: str = ' ') -> str:
    """
    Formata campo alfanumérico preenchendo com espaços à direita.
    
    Args:
        value: Valor a ser formatado
        length: Tamanho total do campo
        fill_char: Caractere de preenchimento (padrão: ' ')
    
    Returns:
        String formatada com o tamanho especificado
    """
    if value is None:
        value = ''
    
    # Remove caracteres especiais que não são permitidos em CNAB
    value_str = str(value)
    # Remove acentos e caracteres especiais, mantém apenas ASCII
    value_str = sanitize_text(value_str)
    
    # Trunca se necessário
    value_str = value_str[:length]
    
    # Preenche com espaços à direita
    return value_str.ljust(length, fill_char)


def format_amount(value: float | Decimal | str | None, length: int = 15) -> str:
    """
    Formata valor monetário (15 posições, 2 decimais, zeros à esquerda).
    
    Exemplo: 123.45 -> 000000000001234
    
    Args:
        value: Valor monetário
        length: Tamanho total do campo (padrão: 15)
    
    Returns:
        String formatada sem ponto decimal, zeros à esquerda
    """
    if value is None or value == '':
        return '0' * length
    
    try:
        # Converte para Decimal para precisão
        if isinstance(value, str):
            # Remove formatação de moeda
            value = value.replace('R$', '').replace('$', '').replace(',', '.').strip()
        decimal_value = Decimal(str(value))
        
        # Arredonda para 2 decimais (trunca)
        decimal_value = decimal_value.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        
        # Multiplica por 100 para remover decimais
        cents = int(decimal_value * 100)
        
        # Formata com zeros à esquerda
        return str(cents).zfill(length)
    except (ValueError, TypeError):
        return '0' * length


def format_date(date: str | datetime | None, format_str: str = '%Y%m%d') -> str:
    """
    Formata data no formato AAAAMMDD.
    
    Args:
        date: Data como string (vários formatos) ou datetime
        format_str: Formato de saída (padrão: '%Y%m%d')
    
    Returns:
        String formatada como AAAAMMDD ou zeros se inválida
    """
    if date is None or date == '':
        return '0' * 8
    
    try:
        if isinstance(date, datetime):
            return date.strftime(format_str)
        
        if isinstance(date, str):
            # Tenta vários formatos comuns
            formats = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%Y%m%d',
                '%d/%m/%y',
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date.strip(), fmt)
                    return dt.strftime(format_str)
                except ValueError:
                    continue
            
            # Se nenhum formato funcionou, retorna zeros
            return '0' * 8
    except (ValueError, TypeError):
        return '0' * 8
    
    return '0' * 8


def format_time(dt: datetime | None = None) -> str:
    """
    Formata hora no formato HHMMSS.
    
    Args:
        dt: datetime (usa hora atual se None)
    
    Returns:
        String formatada como HHMMSS
    """
    if dt is None:
        dt = datetime.now()
    
    return dt.strftime('%H%M%S')


def sanitize_text(text: str) -> str:
    """
    Remove acentos e caracteres especiais, mantém apenas ASCII.
    
    Args:
        text: Texto a ser sanitizado
    
    Returns:
        Texto sem acentos e caracteres especiais
    """
    if not text:
        return ''
    
    # Mapeamento de acentos
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c',
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C',
    }
    
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    # Remove caracteres não ASCII restantes
    result = result.encode('ascii', 'ignore').decode('ascii')
    
    # Remove caracteres especiais não permitidos em CNAB
    # Mantém apenas letras, números, espaços e alguns caracteres básicos
    result = re.sub(r'[^a-zA-Z0-9\s\.\-\/]', '', result)
    
    return result


def ensure_length_240(line: str) -> str:
    """
    Garante que a linha tenha exatamente 240 caracteres.
    
    Args:
        line: Linha a ser ajustada
    
    Returns:
        Linha com exatamente 240 caracteres
    """
    if len(line) > 240:
        return line[:240]
    elif len(line) < 240:
        return line.ljust(240, ' ')
    return line

