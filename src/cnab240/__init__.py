"""
Módulo CNAB 240 para PIX Bradesco Multipag
"""
from .bradesco_pix import BradescoPIXGenerator
from . import fields
from . import validate
from . import config

__all__ = ['BradescoPIXGenerator', 'fields', 'validate', 'config']




