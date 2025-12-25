# Estrutura do Excel - Suporte a PIX, TED e Boletos

## Colunas Obrigatórias (Todos os Tipos)

| Coluna | Obrigatório | Descrição | Exemplo | Observações |
|--------|-------------|-----------|---------|-------------|
| **tipo_pagamento** | ✅ SIM | PIX, TED, DOC ou BOLETO | PIX | **NOVO - Obrigatório** |
| **id_pagamento** | ✅ SIM | Identificador único | 001 | Já existe |
| **data_pagamento** | ✅ SIM | Data do pagamento | 2024-12-31 | Já existe |
| **valor** | ✅ SIM | Valor (2 decimais) | 100.50 | Já existe |
| **nome_favorecido** | ✅ SIM | Nome do favorecido | João Silva | Já existe |
| **tipo_pessoa** | ✅ SIM | F (Física) ou J (Jurídica) | F | Já existe |
| **cpf_cnpj** | ✅ SIM | CPF (11) ou CNPJ (14) | 12345678901 | Já existe |

---

## Colunas Específicas por Tipo

### Para PIX (já implementado)

| Coluna | Obrigatório | Descrição | Exemplo | Observações |
|--------|-------------|-----------|---------|-------------|
| **tipo_chave_pix** | ✅ SIM (se PIX) | CPF, CNPJ, EMAIL, TELEFONE, ALEATORIA | CPF | Já existe |
| **chave_pix** | ✅ SIM (se PIX) | Chave PIX conforme tipo | 12345678901 | Já existe |
| **txid** | ⚪ Opcional | Identificador transação | E123456789... | Já existe (gerado se vazio) |
| **descricao_pagamento** | ⚪ Opcional | Descrição | Pagamento serviços | Já existe |
| **aviso_favorecido** | ⚪ Opcional | 0 ou 1 | 0 | Já existe |

### Para TED/DOC (NOVO - necessário implementar)

| Coluna | Obrigatório | Descrição | Exemplo | Observações |
|--------|-------------|-----------|---------|-------------|
| **banco_favorecido** | ✅ SIM (se TED/DOC) | Código do banco (3 dígitos) | 001 | Banco do Brasil = 001, Itau = 341, etc |
| **agencia_favorecido** | ✅ SIM (se TED/DOC) | Agência do favorecido | 1234 | Apenas números |
| **digito_agencia_favorecido** | ⚪ Opcional | Dígito da agência | 5 | Se houver |
| **conta_favorecido** | ✅ SIM (se TED/DOC) | Conta corrente do favorecido | 123456789 | Apenas números |
| **digito_conta_favorecido** | ✅ SIM (se TED/DOC) | Dígito da conta | 7 | Obrigatório para TED/DOC |
| **tipo_conta** | ✅ SIM (se TED/DOC) | 1=Corrente, 2=Poupança, 3=Salário | 1 | Código do tipo de conta |
| **endereco_favorecido** | ⚪ Opcional | Endereço completo | Rua das Flores, 123 | Para Segmento B |
| **numero_endereco** | ⚪ Opcional | Número do endereço | 123 | Para Segmento B |
| **complemento_endereco** | ⚪ Opcional | Complemento | Apto 45 | Para Segmento B |
| **bairro_favorecido** | ⚪ Opcional | Bairro | Centro | Para Segmento B |
| **cidade_favorecido** | ⚪ Opcional | Cidade | São Paulo | Para Segmento B |
| **cep_favorecido** | ⚪ Opcional | CEP (8 dígitos) | 01234567 | Para Segmento B |
| **estado_favorecido** | ⚪ Opcional | UF (2 letras) | SP | Para Segmento B |
| **finalidade_ted** | ⚪ Opcional | Código finalidade TED | 01 | Conforme tabela do banco |
| **aviso_favorecido** | ⚪ Opcional | 0 ou 1 | 0 | Já existe |

### Para BOLETO (NOVO - necessário implementar)

| Coluna | Obrigatório | Descrição | Exemplo | Observações |
|--------|-------------|-----------|---------|-------------|
| **nosso_numero** | ✅ SIM (se BOLETO) | Nosso número do boleto | 123456789012 | Número atribuído pelo banco |
| **numero_documento** | ✅ SIM (se BOLETO) | Número do documento | DOC001 | Número do documento |
| **data_vencimento** | ✅ SIM (se BOLETO) | Data de vencimento | 2024-12-31 | Pode ser diferente de data_pagamento |
| **valor_titulo** | ✅ SIM (se BOLETO) | Valor do título | 100.50 | Geralmente igual a valor |
| **valor_desconto** | ⚪ Opcional | Valor de desconto | 0.00 | Para Segmento P |
| **valor_multa** | ⚪ Opcional | Valor de multa | 0.00 | Para Segmento P |
| **valor_juros** | ⚪ Opcional | Valor de juros | 0.00 | Para Segmento P |
| **codigo_barras** | ⚪ Opcional | Código de barras | 23791... | Se disponível |
| **linha_digitavel** | ⚪ Opcional | Linha digitável | 23791... | Se disponível |
| **sacado_nome** | ✅ SIM (se BOLETO) | Nome do sacado (pagador) | Empresa XYZ | Para Segmento Q |
| **sacado_tipo_pessoa** | ✅ SIM (se BOLETO) | F ou J | J | Para Segmento Q |
| **sacado_cpf_cnpj** | ✅ SIM (se BOLETO) | CPF/CNPJ do sacado | 12345678000190 | Para Segmento Q |
| **sacado_endereco** | ⚪ Opcional | Endereço do sacado | Rua ABC, 456 | Para Segmento Q |
| **sacado_cidade** | ⚪ Opcional | Cidade do sacado | São Paulo | Para Segmento Q |
| **sacado_cep** | ⚪ Opcional | CEP do sacado | 01234567 | Para Segmento Q |
| **sacado_estado** | ⚪ Opcional | UF do sacado | SP | Para Segmento Q |
| **instrucoes** | ⚪ Opcional | Instruções do boleto | Não receber após vencimento | Para Segmento P |
| **especie_titulo** | ⚪ Opcional | Espécie do título | DM (Duplicata Mercantil) | Para Segmento P |

---

## Exemplo de Planilha Completa

### Aba 1: Pagamentos

| tipo_pagamento | id_pagamento | data_pagamento | valor | nome_favorecido | tipo_pessoa | cpf_cnpj | tipo_chave_pix | chave_pix | banco_favorecido | agencia_favorecido | conta_favorecido | digito_conta_favorecido | tipo_conta | nosso_numero | data_vencimento | descricao_pagamento | aviso_favorecido |
|----------------|--------------|----------------|-------|-----------------|-------------|----------|----------------|-----------|------------------|-------------------|------------------|------------------------|------------|--------------|-----------------|---------------------|------------------|
| PIX | 001 | 2024-12-31 | 100.50 | João Silva | F | 12345678901 | CPF | 12345678901 | | | | | | | | Pagamento PIX | 0 |
| TED | 002 | 2024-12-31 | 200.00 | Maria Santos | F | 98765432100 | | | 001 | 1234 | 5 | 123456789 | 7 | 1 | | | Pagamento TED | 0 |
| BOLETO | 003 | 2024-12-31 | 300.00 | Empresa XYZ | J | 12345678000190 | | | | | | | | 123456789012 | 2025-01-15 | Pagamento Boleto | 0 |

---

## Regras de Validação por Tipo

### PIX
- ✅ `tipo_chave_pix` obrigatório
- ✅ `chave_pix` obrigatório
- ✅ Validar chave conforme tipo
- ❌ Campos de banco/agência/conta não são usados

### TED/DOC
- ✅ `banco_favorecido` obrigatório (3 dígitos)
- ✅ `agencia_favorecido` obrigatório
- ✅ `conta_favorecido` obrigatório
- ✅ `digito_conta_favorecido` obrigatório
- ✅ `tipo_conta` obrigatório (1, 2 ou 3)
- ❌ Campos de chave PIX não são usados

### BOLETO
- ✅ `nosso_numero` obrigatório
- ✅ `data_vencimento` obrigatório
- ✅ `sacado_nome` obrigatório
- ✅ `sacado_tipo_pessoa` obrigatório
- ✅ `sacado_cpf_cnpj` obrigatório
- ❌ Campos de banco/agência/conta do favorecido não são usados
- ❌ Campos de chave PIX não são usados

---

## Adaptações Necessárias no Código

### 1. Leitura do Excel (`main.py`)

```python
# Adicionar leitura da coluna tipo_pagamento
tipo_pagamento = str(row.get('tipo_pagamento', '')).strip().upper()

# Ler campos específicos conforme tipo
if tipo_pagamento == 'PIX':
    # Campos PIX (já implementado)
elif tipo_pagamento in ['TED', 'DOC']:
    # Campos TED/DOC
    banco_favorecido = row.get('banco_favorecido', '')
    agencia_favorecido = row.get('agencia_favorecido', '')
    # ... etc
elif tipo_pagamento == 'BOLETO':
    # Campos Boleto
    nosso_numero = row.get('nosso_numero', '')
    # ... etc
```

### 2. Validações (`validate.py`)

```python
def validate_pagamento(pagamento):
    tipo = pagamento.get('tipo_pagamento', '').upper()
    
    if tipo == 'PIX':
        # Validações PIX (já existe)
    elif tipo in ['TED', 'DOC']:
        # Validações TED/DOC
        if not pagamento.get('banco_favorecido'):
            errors.append("banco_favorecido obrigatório para TED/DOC")
        # ... etc
    elif tipo == 'BOLETO':
        # Validações Boleto
        if not pagamento.get('nosso_numero'):
            errors.append("nosso_numero obrigatório para BOLETO")
        # ... etc
```

### 3. Geração de Arquivo

- Agrupar pagamentos por tipo
- Gerar lotes separados ou arquivos separados
- Usar gerador correto (PIX, TED ou Boleto)

---

## Template de Planilha Sugerido

### Estrutura Recomendada

**Coluna A**: tipo_pagamento  
**Coluna B**: id_pagamento  
**Coluna C**: data_pagamento  
**Coluna D**: valor  
**Coluna E**: nome_favorecido  
**Coluna F**: tipo_pessoa  
**Coluna G**: cpf_cnpj  

**Colunas PIX (H-J)**:
- H: tipo_chave_pix
- I: chave_pix
- J: txid (opcional)

**Colunas TED/DOC (K-P)**:
- K: banco_favorecido
- L: agencia_favorecido
- M: digito_agencia_favorecido
- N: conta_favorecido
- O: digito_conta_favorecido
- P: tipo_conta

**Colunas BOLETO (Q-AA)**:
- Q: nosso_numero
- R: data_vencimento
- S: valor_titulo
- T: sacado_nome
- U: sacado_tipo_pessoa
- V: sacado_cpf_cnpj
- W: sacado_endereco
- X: sacado_cidade
- Y: sacado_cep
- Z: sacado_estado
- AA: instrucoes

**Colunas Comuns (AB-AC)**:
- AB: descricao_pagamento
- AC: aviso_favorecido

---

## Observações Importantes

1. **Campos Condicionais**: Campos específicos de cada tipo só são obrigatórios quando `tipo_pagamento` corresponde
2. **Validação**: O código deve validar apenas os campos relevantes para cada tipo
3. **Flexibilidade**: Campos opcionais podem ficar vazios
4. **Compatibilidade**: Planilhas antigas (só PIX) continuam funcionando se `tipo_pagamento` não for informado (assumir PIX)

---

## Exemplo Prático de Uso

### Linha 1 - PIX
```
tipo_pagamento=PIX, id_pagamento=001, valor=100.50, tipo_chave_pix=CPF, chave_pix=12345678901
(banco_favorecido, agencia_favorecido, etc. ficam vazios)
```

### Linha 2 - TED
```
tipo_pagamento=TED, id_pagamento=002, valor=200.00, banco_favorecido=001, agencia_favorecido=1234, conta_favorecido=123456789, digito_conta_favorecido=7, tipo_conta=1
(tipo_chave_pix, chave_pix ficam vazios)
```

### Linha 3 - BOLETO
```
tipo_pagamento=BOLETO, id_pagamento=003, valor=300.00, nosso_numero=123456789012, data_vencimento=2025-01-15, sacado_nome=Empresa XYZ, sacado_tipo_pessoa=J, sacado_cpf_cnpj=12345678000190
(tipo_chave_pix, banco_favorecido, etc. ficam vazios)
```

