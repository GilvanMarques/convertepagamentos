# Template de Planilha Excel - PIX, TED e Boletos

## Estrutura Simplificada (Recomendada)

### Colunas Mínimas Obrigatórias

| Coluna | Obrigatório Para | Descrição | Exemplo |
|--------|------------------|-----------|---------|
| **tipo_pagamento** | TODOS | PIX, TED, DOC ou BOLETO | PIX |
| **id_pagamento** | TODOS | Identificador único | 001 |
| **data_pagamento** | TODOS | Data do pagamento | 2024-12-31 |
| **valor** | TODOS | Valor (2 decimais) | 100.50 |
| **nome_favorecido** | TODOS | Nome do favorecido | João Silva |
| **tipo_pessoa** | TODOS | F ou J | F |
| **cpf_cnpj** | TODOS | CPF/CNPJ | 12345678901 |

### Colunas Específicas - PIX

| Coluna | Obrigatório | Descrição | Exemplo |
|--------|-------------|-----------|---------|
| **tipo_chave_pix** | Se PIX | CPF, CNPJ, EMAIL, TELEFONE, ALEATORIA | CPF |
| **chave_pix** | Se PIX | Chave PIX | 12345678901 |

### Colunas Específicas - TED/DOC

| Coluna | Obrigatório | Descrição | Exemplo |
|--------|-------------|-----------|---------|
| **banco_favorecido** | Se TED/DOC | Código banco (3 dígitos) | 001 |
| **agencia_favorecido** | Se TED/DOC | Agência | 1234 |
| **conta_favorecido** | Se TED/DOC | Conta corrente | 123456789 |
| **digito_conta_favorecido** | Se TED/DOC | Dígito da conta | 7 |
| **tipo_conta** | Se TED/DOC | 1=Corrente, 2=Poupança, 3=Salário | 1 |

### Colunas Específicas - BOLETO

| Coluna | Obrigatório | Descrição | Exemplo |
|--------|-------------|-----------|---------|
| **nosso_numero** | Se BOLETO | Nosso número | 123456789012 |
| **data_vencimento** | Se BOLETO | Data vencimento | 2025-01-15 |
| **sacado_nome** | Se BOLETO | Nome do pagador | Empresa XYZ |
| **sacado_tipo_pessoa** | Se BOLETO | F ou J | J |
| **sacado_cpf_cnpj** | Se BOLETO | CPF/CNPJ do pagador | 12345678000190 |

### Colunas Opcionais (Todos)

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| **descricao_pagamento** | Descrição | Pagamento serviços |
| **aviso_favorecido** | 0 ou 1 | 0 |
| **txid** | TXID (PIX) | E123456789... |

---

## Exemplo Visual de Planilha

```
| tipo_pagamento | id_pagamento | data_pagamento | valor | nome_favorecido | tipo_pessoa | cpf_cnpj | tipo_chave_pix | chave_pix | banco_favorecido | agencia_favorecido | conta_favorecido | digito_conta_favorecido | tipo_conta | nosso_numero | data_vencimento | sacado_nome | sacado_tipo_pessoa | sacado_cpf_cnpj | descricao_pagamento |
|----------------|--------------|----------------|-------|-----------------|-------------|----------|----------------|-----------|------------------|---------------------|-------------------|------------------------|------------|--------------|-----------------|-------------|-------------------|----------------|---------------------|
| PIX            | 001          | 2024-12-31     | 100.50| João Silva      | F           | 12345678901 | CPF          | 12345678901 |                  |                     |                   |                        |            |              |                 |             |                   |                | Pagamento PIX       |
| TED            | 002          | 2024-12-31     | 200.00| Maria Santos    | F           | 98765432100 |               |            | 001              | 1234                | 123456789         | 7                      | 1          |              |                 |             |                   |                | Pagamento TED       |
| BOLETO         | 003          | 2024-12-31     | 300.00| Empresa XYZ     | J           | 12345678000190 |             |            |                  |                     |                   |                        |            | 123456789012 | 2025-01-15      | Empresa ABC | J                 | 98765432000100 | Pagamento Boleto   |
```

---

## Regras de Preenchimento

### Para PIX:
- ✅ Preencher: tipo_pagamento, tipo_chave_pix, chave_pix
- ❌ Deixar vazio: banco_favorecido, agencia_favorecido, nosso_numero, etc.

### Para TED/DOC:
- ✅ Preencher: tipo_pagamento, banco_favorecido, agencia_favorecido, conta_favorecido, digito_conta_favorecido, tipo_conta
- ❌ Deixar vazio: tipo_chave_pix, chave_pix, nosso_numero, etc.

### Para BOLETO:
- ✅ Preencher: tipo_pagamento, nosso_numero, data_vencimento, sacado_nome, sacado_tipo_pessoa, sacado_cpf_cnpj
- ❌ Deixar vazio: tipo_chave_pix, chave_pix, banco_favorecido, etc.

---

## Dica de Implementação

**Para manter compatibilidade com planilhas antigas (só PIX)**:
- Se `tipo_pagamento` estiver vazio, assumir "PIX"
- Validar apenas campos relevantes para cada tipo
- Campos de outros tipos podem ficar vazios sem erro

