"""
Página de Fornecedores (Cadastro) - Excel como "banco de dados"
"""

from __future__ import annotations

import streamlit as st
from pathlib import Path
from datetime import datetime, date
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd

from src.suppliers_db import (
    load_suppliers,
    save_suppliers,
    upsert_supplier,
    delete_supplier,
    SUPPLIER_COLUMNS,
)
from src.validators import normalize_doc, validate_cpf_cnpj, validate_pix, validate_ted_fields
from src.cnab240 import validate as cnab_validate


st.title("📒 Fornecedores (Cadastro)")
st.markdown("Cadastro de fornecedores a partir do arquivo `data/fornecedores.xlsx` (sem upload).")


def _default_suppliers_path() -> Path:
    base = Path(__file__).parent.parent.parent
    p1 = base / "data" / "fornecedores.xlsx"
    p2 = base / "data" / "Fornecedores.xlsx"
    if p1.exists():
        return p1
    if p2.exists():
        return p2
    return p1


SUPPLIERS_PATH = _default_suppliers_path()


@st.cache_data(show_spinner=False)
def _cached_load(path_str: str, mtime: float) -> pd.DataFrame:
    # mtime entra só pra invalidar cache quando o arquivo muda
    _ = mtime
    return load_suppliers(path_str)


def _get_mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def _mask_value(v: str, keep_last: int = 4) -> str:
    s = str(v or "").strip()
    if not s:
        return ""
    if len(s) <= keep_last:
        return "*" * len(s)
    return ("*" * (len(s) - keep_last)) + s[-keep_last:]


df = _cached_load(str(SUPPLIERS_PATH), _get_mtime(SUPPLIERS_PATH))

st.caption(f"Fonte: `{SUPPLIERS_PATH}` • Registros: {len(df)}")

col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
with col_f1:
    q_nome = st.text_input("Pesquisar por nome (contém)", value="")
with col_f2:
    q_doc = st.text_input("Pesquisar por CPF/CNPJ (igual)", value="", help="Ignora pontuação.")
with col_f3:
    q_tipo = st.selectbox("Tipo", options=["Todos", "PIX", "TED"], index=0)

fdf = df.copy()
if q_nome.strip():
    fdf = fdf[fdf["nome_favorecido"].astype(str).str.contains(q_nome.strip(), case=False, na=False)]
if q_doc.strip():
    doc_norm = normalize_doc(q_doc)
    fdf = fdf[fdf["cpf_cnpj"].map(normalize_doc) == doc_norm]
if q_tipo != "Todos":
    fdf = fdf[fdf["tipo_pgto"].astype(str).str.upper() == q_tipo]

st.divider()
st.subheader("📋 Lista (mascarada)")

display = fdf.copy()
display["cpf_cnpj"] = display["cpf_cnpj"].map(lambda x: _mask_value(normalize_doc(x), 4))
display["chave_pix"] = display["chave_pix"].map(lambda x: _mask_value(str(x), 6))
display["conta_favorecido"] = display["conta_favorecido"].map(lambda x: _mask_value(normalize_doc(x), 3))

st.dataframe(
    display[["nome_favorecido", "tipo_pgto", "cpf_cnpj", "chave_pix", "banco_favorecido", "agencia_favorecido", "conta_favorecido"]],
    width="stretch",
    hide_index=True,
)

st.divider()
st.subheader("✏️ Seleção / Edição")

choices = fdf.apply(lambda r: f"{r['nome_favorecido']} • {r['cpf_cnpj']}", axis=1).tolist()
choice = st.selectbox("Fornecedor", options=["(Novo fornecedor)"] + choices, index=0)

is_new = choice == "(Novo fornecedor)"
selected = None
if not is_new and len(fdf) > 0:
    selected = fdf.iloc[choices.index(choice)].to_dict()


def _record_from_form() -> dict:
    return {
        "nome_favorecido": nome_favorecido,
        "tipo_pessoa": tipo_pessoa,
        "cpf_cnpj": cpf_cnpj,
        "tipo_pgto": tipo_pgto,
        "tipo_chave_pix": tipo_chave_pix,
        "chave_pix": chave_pix,
        "banco_favorecido": banco_favorecido,
        "agencia_favorecido": agencia_favorecido,
        "conta_favorecido": conta_favorecido,
        "digito_conta_favorecido": digito_conta_favorecido,
        "tipo_conta": tipo_conta,
    }


nome_favorecido = st.text_input("Nome do favorecido", value=(selected or {}).get("nome_favorecido", ""))
tipo_pessoa = st.selectbox("Tipo pessoa", options=["F", "J"], index=0 if (selected or {}).get("tipo_pessoa", "F") == "F" else 1)
cpf_cnpj = st.text_input("CPF/CNPJ", value=(selected or {}).get("cpf_cnpj", ""))
tipo_pgto = st.selectbox("Tipo pagamento", options=["PIX", "TED"], index=0 if (selected or {}).get("tipo_pgto", "PIX") == "PIX" else 1)

st.markdown("**PIX**")
tipo_chave_pix = st.selectbox("Tipo chave PIX", options=["", "CPF", "CNPJ", "EMAIL", "TELEFONE", "ALEATORIA"], index=0)
if selected and (selected.get("tipo_chave_pix") or "") in ["CPF", "CNPJ", "EMAIL", "TELEFONE", "ALEATORIA"]:
    tipo_chave_pix = selected.get("tipo_chave_pix")
chave_pix = st.text_input("Chave PIX", value=(selected or {}).get("chave_pix", ""))

st.markdown("**TED**")
banco_favorecido = st.text_input("Banco (3 dígitos)", value=(selected or {}).get("banco_favorecido", ""))
agencia_favorecido = st.text_input("Agência", value=(selected or {}).get("agencia_favorecido", ""))
conta_favorecido = st.text_input("Conta", value=(selected or {}).get("conta_favorecido", ""))
digito_conta_favorecido = st.text_input("Dígito da conta", value=(selected or {}).get("digito_conta_favorecido", ""))
tipo_conta = st.selectbox("Tipo conta", options=["", "1", "2"], index=0)
if selected and (selected.get("tipo_conta") or "") in ["1", "2"]:
    tipo_conta = str(selected.get("tipo_conta"))

col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
with col_b1:
    if st.button("💾 Salvar alterações", type="primary", width="stretch"):
        record = _record_from_form()
        # validações
        ok, msg = validate_cpf_cnpj(record["cpf_cnpj"])
        if not ok:
            st.error(msg)
        else:
            ok, msg = validate_pix(record)
            if not ok:
                st.error(msg)
            else:
                ok, msg = validate_ted_fields(record)
                if not ok:
                    st.error(msg)
                else:
                    try:
                        new_df = upsert_supplier(df, record)
                        save_suppliers(new_df, SUPPLIERS_PATH)
                        st.cache_data.clear()
                        st.success("✅ Fornecedor salvo.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Falha ao salvar: {e}")

with col_b2:
    if (not is_new) and st.button("🗑️ Excluir", width="stretch"):
        try:
            new_df = delete_supplier(df, (selected or {}).get("cpf_cnpj", ""))
            save_suppliers(new_df, SUPPLIERS_PATH)
            st.cache_data.clear()
            st.success("✅ Fornecedor excluído.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Falha ao excluir: {e}")

with col_b3:
    if st.button("➕ Novo fornecedor", width="stretch"):
        st.rerun()

st.divider()
st.subheader("🧾 Aplicar fornecedor no pagamento")

valor = st.number_input("Valor (R$)", min_value=0.0, value=0.0, step=0.01, format="%.2f")
data_pag = st.date_input("Data do pagamento", value=date.today())
descricao = st.text_input("Descrição (opcional)", value="")

if st.button("✅ Aplicar fornecedor selecionado no pagamento", width="stretch", disabled=is_new and not nome_favorecido.strip()):
    record = _record_from_form()
    doc_norm = normalize_doc(record.get("cpf_cnpj", ""))
    # validação básica antes de aplicar
    ok, msg = validate_cpf_cnpj(doc_norm)
    if not ok:
        st.error(msg)
    else:
        # cria pagamento padronizado (não duplica lógica do gerador)
        pagamento = {
            "id_pagamento": str(int(datetime.now().timestamp())),
            "tipo_pagamento": record["tipo_pgto"].upper(),
            "valor": float(valor),
            "data_pagamento": data_pag.strftime("%Y-%m-%d"),
            "nome_favorecido": record["nome_favorecido"],
            "tipo_pessoa": record["tipo_pessoa"],
            "cpf_cnpj": doc_norm,
            "descricao_pagamento": descricao.strip(),
            # defaults usados no restante do app
            "finalidade_ted": "00001",
            "aviso_favorecido": 0,
        }
        if record["tipo_pgto"].upper() == "PIX":
            pagamento.update(
                {
                    "tipo_chave_pix": record.get("tipo_chave_pix", "").upper(),
                    "chave_pix": record.get("chave_pix", ""),
                    "txid": "",
                }
            )
        else:
            pagamento.update(
                {
                    "banco_favorecido": record.get("banco_favorecido", ""),
                    "agencia_favorecido": record.get("agencia_favorecido", ""),
                    "digito_agencia_favorecido": "",
                    "conta_favorecido": record.get("conta_favorecido", ""),
                    "digito_conta_favorecido": record.get("digito_conta_favorecido", ""),
                    "tipo_conta": record.get("tipo_conta", "1"),
                }
            )

        st.session_state.pagamentos = st.session_state.get("pagamentos") or []
        st.session_state.pagamentos.append(pagamento)

        # revalida automaticamente para liberar geração
        erros, avisos, validos = [], [], []
        for idx, p in enumerate(st.session_state.pagamentos):
            is_valid, errors = cnab_validate.validate_pagamento(p, idx)
            if is_valid:
                validos.append({"id_pagamento": p.get("id_pagamento", f"#{idx}"), "status": "OK", "mensagem": "Pagamento válido"})
            else:
                for err in errors:
                    (avisos if ("será truncado" in err.lower() or "será ajustado" in err.lower()) else erros).append(
                        {"id_pagamento": p.get("id_pagamento", f"#{idx}"), "status": "ERRO" if err in errors else "AVISO", "mensagem": err}
                    )

        st.session_state.validacao_resultado = {
            "erros": erros,
            "avisos": avisos,
            "validos": validos,
            "total": len(st.session_state.pagamentos),
            "total_erros": len(erros),
            "total_avisos": len(avisos),
            "total_validos": len(validos),
        }

        if erros:
            st.error("❌ Pagamento aplicado, mas há erros. Corrija os dados do fornecedor/pagamento.")
        else:
            st.success("✅ Pagamento aplicado e validado. Vá para **Gerar CNAB**.")

st.caption("Dica: você pode aplicar mais de um pagamento (ele será acumulado na sessão).")


