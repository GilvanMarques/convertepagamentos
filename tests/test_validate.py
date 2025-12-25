"""
Testes para validações
"""
import unittest
from datetime import datetime, timedelta
from src.cnab240 import validate


class TestValidate(unittest.TestCase):
    """Testes para validações"""
    
    def test_validate_cpf(self):
        """Testa validação de CPF"""
        # CPF válido (exemplo)
        self.assertTrue(validate.validate_cpf('11144477735'))
        # CPF inválido
        self.assertFalse(validate.validate_cpf('12345678901'))
        self.assertFalse(validate.validate_cpf('11111111111'))
        self.assertFalse(validate.validate_cpf(''))
    
    def test_validate_cnpj(self):
        """Testa validação de CNPJ"""
        # CNPJ válido (exemplo)
        self.assertTrue(validate.validate_cnpj('11222333000181'))
        # CNPJ inválido
        self.assertFalse(validate.validate_cnpj('12345678000190'))
        self.assertFalse(validate.validate_cnpj('11111111111111'))
        self.assertFalse(validate.validate_cnpj(''))
    
    def test_validate_email(self):
        """Testa validação de e-mail"""
        self.assertTrue(validate.validate_email('teste@example.com'))
        self.assertTrue(validate.validate_email('user.name@domain.co.uk'))
        self.assertFalse(validate.validate_email('invalid'))
        self.assertFalse(validate.validate_email('@example.com'))
        self.assertFalse(validate.validate_email(''))
    
    def test_validate_phone(self):
        """Testa validação de telefone"""
        self.assertTrue(validate.validate_phone('11999999999'))
        self.assertTrue(validate.validate_phone('+5511999999999'))
        self.assertTrue(validate.validate_phone('(11) 99999-9999'))
        self.assertFalse(validate.validate_phone('123'))
        self.assertFalse(validate.validate_phone(''))
    
    def test_validate_pix_key(self):
        """Testa validação de chave PIX"""
        # CPF
        self.assertTrue(validate.validate_pix_key('11144477735', 'CPF'))
        # CNPJ
        self.assertTrue(validate.validate_pix_key('11222333000181', 'CNPJ'))
        # Email
        self.assertTrue(validate.validate_pix_key('teste@example.com', 'EMAIL'))
        # Telefone
        self.assertTrue(validate.validate_pix_key('11999999999', 'TELEFONE'))
        # Aleatória (UUID)
        self.assertTrue(validate.validate_pix_key('123e4567-e89b-12d3-a456-426614174000', 'ALEATORIA'))
    
    def test_validate_date(self):
        """Testa validação de data"""
        hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Data válida
        is_valid, msg = validate.validate_date('2024-12-31')
        self.assertTrue(is_valid)
        
        # Data inválida
        is_valid, msg = validate.validate_date('invalid')
        self.assertFalse(is_valid)
        
        # Data no passado (se configurado)
        past_date = (hoje.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
        is_valid, msg = validate.validate_date(past_date, min_date=hoje)
        self.assertFalse(is_valid)
    
    def test_validate_pagamento(self):
        """Testa validação de pagamento"""
        # Pagamento válido
        pagamento = {
            'id_pagamento': '001',
            'data_pagamento': '2024-12-31',
            'valor': 100.50,
            'nome_favorecido': 'João Silva',
            'tipo_pessoa': 'F',
            'cpf_cnpj': '11144477735',
            'tipo_chave_pix': 'CPF',
            'chave_pix': '11144477735',
            'aviso_favorecido': 0,
        }
        is_valid, errors = validate.validate_pagamento(pagamento)
        self.assertTrue(is_valid)
        
        # Pagamento inválido (sem valor)
        pagamento_invalido = pagamento.copy()
        pagamento_invalido['valor'] = 0
        is_valid, errors = validate.validate_pagamento(pagamento_invalido)
        self.assertFalse(is_valid)


if __name__ == '__main__':
    unittest.main()

