#!/usr/bin/env python3
"""
Script de teste rápido para validar o gerador CNAB 240
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.cnab240.bradesco_pix import BradescoPIXGenerator
from src.cnab240 import validate
from src.cnab240.fields import ensure_length_240

def test_basic_generation():
    """Testa geração básica de arquivo CNAB"""
    print("=" * 60)
    print("TESTE RÁPIDO - Gerador CNAB 240 PIX Bradesco")
    print("=" * 60)
    
    # Dados de teste
    pagamentos_teste = [
        {
            'id_pagamento': '001',
            'data_pagamento': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'valor': 100.50,
            'nome_favorecido': 'João Silva',
            'tipo_pessoa': 'F',
            'cpf_cnpj': '11144477735',  # CPF válido para teste
            'tipo_chave_pix': 'CPF',
            'chave_pix': '11144477735',
            'descricao_pagamento': 'Teste de pagamento',
            'aviso_favorecido': 0,
        }
    ]
    
    print(f"\n1. Validando {len(pagamentos_teste)} pagamento(s)...")
    all_valid, errors_by_id = validate.validate_pagamentos(pagamentos_teste)
    
    if not all_valid:
        print("   ❌ ERROS ENCONTRADOS:")
        for id_pag, errors in errors_by_id.items():
            print(f"      {id_pag}:")
            for error in errors:
                print(f"        - {error}")
        return False
    else:
        print("   ✅ Validação OK")
    
    print("\n2. Gerando arquivo CNAB 240...")
    try:
        config_path = Path(__file__).parent / 'config' / 'bradesco.yaml'
        generator = BradescoPIXGenerator(str(config_path))
        
        file_date = datetime.now()
        lines = generator.generate_file(pagamentos_teste, file_date, 1)
        
        print(f"   ✅ Arquivo gerado com {len(lines)} registros")
        
    except Exception as e:
        print(f"   ❌ Erro ao gerar arquivo: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n3. Validando estrutura do arquivo...")
    file_valid, file_errors = validate.validate_cnab_file(lines)
    
    if not file_valid:
        print("   ❌ ERROS NA ESTRUTURA:")
        for error in file_errors:
            print(f"      - {error}")
        return False
    else:
        print("   ✅ Estrutura OK")
    
    print("\n4. Validando tamanho das linhas...")
    all_240 = True
    for i, line in enumerate(lines, 1):
        line_clean = line.rstrip('\r\n')
        if len(line_clean) != 240:
            print(f"   ❌ Linha {i}: {len(line_clean)} caracteres (esperado 240)")
            all_240 = False
    
    if all_240:
        print(f"   ✅ Todas as {len(lines)} linhas têm 240 caracteres")
    
    print("\n5. Validando trailers...")
    total_pagamentos = len(pagamentos_teste)
    total_valor = sum(float(p.get('valor', 0)) for p in pagamentos_teste)
    
    trailers_valid, trailer_errors = validate.validate_trailers(lines, total_pagamentos, total_valor)
    
    if not trailers_valid:
        print("   ❌ ERROS NOS TRAILERS:")
        for error in trailer_errors:
            print(f"      - {error}")
        return False
    else:
        print("   ✅ Trailers OK")
    
    print("\n6. Exibindo estrutura do arquivo:")
    print(f"   Linha 1: {lines[0][:50]}... (Header Arquivo)")
    print(f"   Linha 2: {lines[1][:50]}... (Header Lote)")
    print(f"   Linha 3: {lines[2][:50]}... (Segmento J)")
    print(f"   Linha 4: {lines[3][:50]}... (Segmento J-52)")
    print(f"   Linha {len(lines)-1}: {lines[-2][:50]}... (Trailer Lote)")
    print(f"   Linha {len(lines)}: {lines[-1][:50]}... (Trailer Arquivo)")
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print(f"\nResumo:")
    print(f"  - Total de pagamentos: {total_pagamentos}")
    print(f"  - Total de registros: {len(lines)}")
    print(f"  - Valor total: R$ {total_valor:,.2f}")
    print(f"  - Todas as linhas têm 240 caracteres: {'Sim' if all_240 else 'Não'}")
    print(f"  - Trailers conferem: {'Sim' if trailers_valid else 'Não'}")
    
    return True

if __name__ == '__main__':
    success = test_basic_generation()
    sys.exit(0 if success else 1)




