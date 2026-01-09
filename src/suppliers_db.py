"""
Leitura/gravação de fornecedores em Excel (aba "Fornecedores") com lock e escrita atômica.
"""

from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Any

import pandas as pd

from .validators import normalize_doc, validate_cpf_cnpj, validate_pix, validate_ted_fields

DEFAULT_SHEET = "Fornecedores"

SUPPLIER_COLUMNS = [
    "nome_favorecido",
    "tipo_pessoa",
    "cpf_cnpj",
    "tipo_pgto",
    "tipo_chave_pix",
    "chave_pix",
    "banco_favorecido",
    "agencia_favorecido",
    "conta_favorecido",
    "digito_conta_favorecido",
    "tipo_conta",
]


def _pick_existing_sheet(path: Path) -> str | None:
    try:
        xls = pd.ExcelFile(path)
        if DEFAULT_SHEET in xls.sheet_names:
            return DEFAULT_SHEET
        # fallback: primeira aba
        return xls.sheet_names[0] if xls.sheet_names else None
    except Exception:
        return None


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        df = pd.DataFrame()
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    for col in SUPPLIER_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[SUPPLIER_COLUMNS]
    df = df.fillna("")
    # normaliza tipos
    df["tipo_pessoa"] = df["tipo_pessoa"].astype(str).str.strip().str.upper().replace({"": "F"})
    df["tipo_pgto"] = df["tipo_pgto"].astype(str).str.strip().str.upper()
    df["cpf_cnpj"] = df["cpf_cnpj"].astype(str).map(normalize_doc)
    return df


def ensure_suppliers_file(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        return p

    # cria um arquivo vazio com a aba "Fornecedores" e cabeçalhos
    df = pd.DataFrame(columns=SUPPLIER_COLUMNS)
    with pd.ExcelWriter(p, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=DEFAULT_SHEET, index=False)
    return p


def load_suppliers(path: str | Path) -> pd.DataFrame:
    p = ensure_suppliers_file(path)
    sheet = _pick_existing_sheet(p)
    if sheet is None:
        return _normalize_df(pd.DataFrame(columns=SUPPLIER_COLUMNS))
    df = pd.read_excel(p, sheet_name=sheet, dtype=str)
    return _normalize_df(df)


def _read_all_sheets(path: Path) -> Dict[str, pd.DataFrame]:
    try:
        xls = pd.ExcelFile(path)
        out: Dict[str, pd.DataFrame] = {}
        for s in xls.sheet_names:
            out[s] = pd.read_excel(path, sheet_name=s, dtype=str)
        return out
    except Exception:
        return {}


def save_suppliers(df: pd.DataFrame, path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df_norm = _normalize_df(df)

    @contextmanager
    def _file_lock(lock_file: Path):
        """
        Lock simples (best-effort) sem dependências externas.
        - macOS/Linux: fcntl.flock
        - Windows: fallback sem lock (ambiente atual é macOS)
        """
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        fh = None
        try:
            fh = open(lock_file, "a+", encoding="utf-8")
            try:
                import fcntl  # type: ignore

                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            except Exception:
                # Se não conseguir travar (ex.: Windows sem fcntl), segue sem lock.
                pass
            yield
        finally:
            if fh is not None:
                try:
                    try:
                        import fcntl  # type: ignore

                        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
                    except Exception:
                        pass
                finally:
                    fh.close()

    lock_path = str(p) + ".lock"
    with _file_lock(Path(lock_path)):
        other = _read_all_sheets(p) if p.exists() else {}
        # Se o arquivo antigo só tem uma aba padrão (ex.: "Planilha1") e não tem "Fornecedores",
        # não preserva a aba antiga para evitar duplicidade/confusão.
        if other and (DEFAULT_SHEET not in other) and len(other.keys()) == 1:
            other = {}
        # escreve tudo em um arquivo temporário e troca atomicamente
        tmp_dir = p.parent
        fd, tmp_name = tempfile.mkstemp(prefix=p.stem + "_", suffix=".tmp.xlsx", dir=tmp_dir)
        os.close(fd)
        tmp_path = Path(tmp_name)
        try:
            with pd.ExcelWriter(tmp_path, engine="openpyxl") as writer:
                for sheet, sdf in other.items():
                    if sheet == DEFAULT_SHEET:
                        continue
                    sdf.to_excel(writer, sheet_name=sheet, index=False)
                df_norm.to_excel(writer, sheet_name=DEFAULT_SHEET, index=False)
            os.replace(tmp_path, p)
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)


def upsert_supplier(df: pd.DataFrame, record: Dict[str, Any]) -> pd.DataFrame:
    df = _normalize_df(df)
    rec = {k: ("" if record.get(k) is None else str(record.get(k)).strip()) for k in SUPPLIER_COLUMNS}
    rec["tipo_pessoa"] = rec["tipo_pessoa"].upper() or "F"
    rec["tipo_pgto"] = rec["tipo_pgto"].upper()
    rec["cpf_cnpj"] = normalize_doc(rec["cpf_cnpj"])

    # validações
    ok, msg = validate_cpf_cnpj(rec["cpf_cnpj"])
    if not ok:
        raise ValueError(msg)
    ok, msg = validate_pix(rec)
    if not ok:
        raise ValueError(msg)
    ok, msg = validate_ted_fields(rec)
    if not ok:
        raise ValueError(msg)

    key = rec["cpf_cnpj"]
    if not key:
        raise ValueError("CPF/CNPJ é obrigatório.")

    # unicidade por cpf_cnpj
    existing = df["cpf_cnpj"].map(normalize_doc)
    matches = existing == key
    if matches.sum() > 1:
        raise ValueError("CPF/CNPJ duplicado no cadastro.")

    if matches.any():
        idx = matches.idxmax()
        for k in SUPPLIER_COLUMNS:
            df.at[idx, k] = rec[k]
    else:
        df = pd.concat([df, pd.DataFrame([rec])], ignore_index=True)

    return _normalize_df(df)


def delete_supplier(df: pd.DataFrame, cpf_cnpj: str) -> pd.DataFrame:
    df = _normalize_df(df)
    key = normalize_doc(cpf_cnpj)
    if not key:
        return df
    df = df[df["cpf_cnpj"].map(normalize_doc) != key].copy()
    return _normalize_df(df)


