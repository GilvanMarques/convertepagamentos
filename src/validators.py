"""
Validadores e normalizadores usados pela UI de fornecedores (Excel como "DB").
"""

from __future__ import annotations

import re
from typing import Tuple, Dict, Any


def normalize_doc(value: str | None) -> str:
    """Remove qualquer pontuação e retorna apenas dígitos."""
    if not value:
        return ""
    return re.sub(r"[^0-9]", "", str(value))


def _cpf_is_valid(cpf: str) -> bool:
    cpf = normalize_doc(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calc_digit(base: str, weights: list[int]) -> str:
        s = sum(int(d) * w for d, w in zip(base, weights))
        r = (s * 10) % 11
        return "0" if r == 10 else str(r)

    d1 = calc_digit(cpf[:9], list(range(10, 1, -1)))
    d2 = calc_digit(cpf[:9] + d1, list(range(11, 1, -1)))
    return cpf[-2:] == d1 + d2


def _cnpj_is_valid(cnpj: str) -> bool:
    cnpj = normalize_doc(cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def calc_digit(base: str, weights: list[int]) -> str:
        s = sum(int(d) * w for d, w in zip(base, weights))
        r = s % 11
        return "0" if r < 2 else str(11 - r)

    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    w2 = [6] + w1
    d1 = calc_digit(cnpj[:12], w1)
    d2 = calc_digit(cnpj[:12] + d1, w2)
    return cnpj[-2:] == d1 + d2


def validate_cpf_cnpj(doc: str | None) -> Tuple[bool, str]:
    doc_norm = normalize_doc(doc)
    if not doc_norm:
        return False, "CPF/CNPJ é obrigatório."
    if len(doc_norm) == 11:
        return (_cpf_is_valid(doc_norm), "CPF inválido." if not _cpf_is_valid(doc_norm) else "")
    if len(doc_norm) == 14:
        return (_cnpj_is_valid(doc_norm), "CNPJ inválido." if not _cnpj_is_valid(doc_norm) else "")
    return False, "CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos."


def validate_pix(record: Dict[str, Any]) -> Tuple[bool, str]:
    if str(record.get("tipo_pgto", "")).upper() != "PIX":
        return True, ""

    tipo = str(record.get("tipo_chave_pix", "")).strip().upper()
    chave = str(record.get("chave_pix", "")).strip()
    if not tipo or not chave:
        return False, "PIX: tipo_chave_pix e chave_pix são obrigatórios."

    if tipo in {"CPF", "CNPJ"}:
        doc = normalize_doc(chave)
        if tipo == "CPF" and len(doc) != 11:
            return False, "PIX: chave CPF deve ter 11 dígitos."
        if tipo == "CNPJ" and len(doc) != 14:
            return False, "PIX: chave CNPJ deve ter 14 dígitos."
    elif tipo == "TELEFONE":
        if not normalize_doc(chave):
            return False, "PIX: chave TELEFONE deve conter dígitos."
    elif tipo == "EMAIL":
        if "@" not in chave:
            return False, "PIX: chave EMAIL inválida."
    elif tipo == "ALEATORIA":
        # aceita 32/36 chars normalmente; não bloqueia por contrato
        pass
    else:
        return False, "PIX: tipo_chave_pix inválido (CPF/CNPJ/EMAIL/TELEFONE/ALEATORIA)."

    return True, ""


def validate_ted_fields(record: Dict[str, Any]) -> Tuple[bool, str]:
    if str(record.get("tipo_pgto", "")).upper() != "TED":
        return True, ""

    required = [
        ("banco_favorecido", "banco_favorecido"),
        ("agencia_favorecido", "agencia_favorecido"),
        ("conta_favorecido", "conta_favorecido"),
        ("digito_conta_favorecido", "digito_conta_favorecido"),
    ]
    missing = [label for key, label in required if not str(record.get(key, "")).strip()]
    if missing:
        return False, f"TED: campos obrigatórios ausentes: {', '.join(missing)}."

    return True, ""


