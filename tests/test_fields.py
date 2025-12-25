"""
Testes para formatadores de campos
"""
import unittest
from datetime import datetime
from src.cnab240 import fields


class TestFields(unittest.TestCase):
    """Testes para formatadores de campos"""
    
    def test_format_numeric(self):
        """Testa formatação numérica"""
        self.assertEqual(fields.format_numeric(123, 5), '00123')
        self.assertEqual(fields.format_numeric('456', 5), '00456')
        self.assertEqual(fields.format_numeric(None, 5), '00000')
        self.assertEqual(fields.format_numeric('', 5), '00000')
    
    def test_format_alphanumeric(self):
        """Testa formatação alfanumérica"""
        self.assertEqual(fields.format_alphanumeric('ABC', 5), 'ABC  ')
        self.assertEqual(fields.format_alphanumeric('ABC', 2), 'AB')
        self.assertEqual(fields.format_alphanumeric(None, 5), '     ')
        self.assertEqual(fields.format_alphanumeric('', 5), '     ')
    
    def test_format_amount(self):
        """Testa formatação de valores monetários"""
        self.assertEqual(fields.format_amount(123.45, 15), '000000000001234')
        self.assertEqual(fields.format_amount(0.01, 15), '000000000000001')
        self.assertEqual(fields.format_amount(1000.00, 15), '000000000100000')
        self.assertEqual(fields.format_amount(None, 15), '000000000000000')
        self.assertEqual(fields.format_amount('123.45', 15), '000000000001234')
    
    def test_format_date(self):
        """Testa formatação de datas"""
        dt = datetime(2024, 1, 15)
        self.assertEqual(fields.format_date(dt), '20240115')
        self.assertEqual(fields.format_date('2024-01-15'), '20240115')
        self.assertEqual(fields.format_date('15/01/2024'), '20240115')
        self.assertEqual(fields.format_date(None), '00000000')
        self.assertEqual(fields.format_date(''), '00000000')
    
    def test_format_time(self):
        """Testa formatação de hora"""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        self.assertEqual(fields.format_time(dt), '143045')
    
    def test_sanitize_text(self):
        """Testa sanitização de texto"""
        self.assertEqual(fields.sanitize_text('José'), 'Jose')
        self.assertEqual(fields.sanitize_text('São Paulo'), 'Sao Paulo')
        self.assertEqual(fields.sanitize_text('Açúcar'), 'Acucar')
        self.assertEqual(fields.sanitize_text(''), '')
        self.assertEqual(fields.sanitize_text(None), '')
    
    def test_ensure_length_240(self):
        """Testa garantia de tamanho 240"""
        short_line = 'ABC'
        self.assertEqual(len(fields.ensure_length_240(short_line)), 240)
        
        long_line = 'A' * 300
        self.assertEqual(len(fields.ensure_length_240(long_line)), 240)
        
        exact_line = 'A' * 240
        self.assertEqual(len(fields.ensure_length_240(exact_line)), 240)


if __name__ == '__main__':
    unittest.main()

