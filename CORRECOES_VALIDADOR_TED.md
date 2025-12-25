# Correções Aplicadas - Validador Bradesco TED

## ✅ Correções Implementadas

### 1. **Segmento A - Código da Câmara (colunas 018-020)**
**Erro:** "Informado 000-Crédito em conta Bradesco, inválido para banco diferente de 237"

**Correção:**
- Agora verifica se o banco favorecido é 237 (Bradesco)
- Se for 237, usa código 000
- Se for outro banco, usa código 018 (TED)

### 2. **Segmento A - Data Real e Valor Real (colunas 155-177)**
**Erro:** "Data real efetivação do pagamento em branco. Informar zeros."
**Erro:** "Valor real efetivação do pagamento em branco. Informar zeros."

**Correção:**
- Data Real: agora preenche com zeros (8 posições) ao invés de brancos
- Valor Real: agora preenche com zeros (15 posições) ao invés de brancos

### 3. **Segmento A - Campo SIAPE (colunas 178-217)**
**Erro:** "Campo destinado para informações SIAPE. Vide descrição G031 do layout técnico."

**Correção:**
- Campo SIAPE (40 posições) agora é preenchido com zeros quando não usado

### 4. **Segmento A - Código Aviso ao Favorecido (coluna 230)**
**Erro:** "Código aviso ao favorecido inválido"

**Correção:**
- Validação adicionada: só aceita 0 ou 1
- Se não informado ou inválido, usa 0 como padrão

### 5. **Segmento B - Código Aviso ao Favorecido (coluna 226)**
**Erro:** "Código aviso ao favorecido não informado"

**Correção:**
- Campo adicionado no Segmento B
- Validação: só aceita 0 ou 1
- Se não informado, usa 0 como padrão

### 6. **Segmento B - Data de Vencimento (colunas 128-135)**
**Erro:** "Data de vencimento (nominal) inválida"

**Correção:**
- Agora usa `data_vencimento` se informado, senão usa `data_pagamento`
- Garante que sempre há uma data válida

### 7. **Trailer Lote - Somatório de Moedas (colunas 042-059)**
**Erro:** "Somatório de quantidade de moedas inválido. Informar zeros."

**Correção:**
- Campo agora preenchido com zeros (18 posições) ao invés de brancos

### 8. **Trailer Lote - Número Aviso de Débito (colunas 060-065)**
**Erro:** "Número aviso de débito inválido. Informar zeros."

**Correção:**
- Campo agora preenchido com zeros (6 posições) ao invés de brancos

### 9. **Trailer Arquivo - Quantidade de Contas (colunas 030-035)**
**Erro:** "Quantidade de contas exclusivo para conciliação bancária. Informar zeros."

**Correção:**
- Campo agora preenchido com zeros (6 posições) ao invés de 1

## ⚠️ Erros que Precisam Ajuste no Config/Excel

### Header Arquivo e Header Lote

Os seguintes erros são relacionados aos **dados de configuração** (`config/bradesco.yaml`) ou **formatação**:

1. **CNPJ inválido (colunas 019-032)**
   - Verificar se o CNPJ está correto no `config/bradesco.yaml`
   - Deve ter 14 dígitos (apenas números)

2. **Código do convênio/Perfil incorreto (colunas 033-052)**
   - Deve estar alinhado à esquerda
   - Verificar se está correto no `config/bradesco.yaml`

3. **Dígito da agência inválido (coluna 058)**
   - Verificar `digito_agencia` no `config/bradesco.yaml`
   - Deve ser um único caractere alfanumérico

4. **Número da conta inválido (colunas 059-071)**
   - Verificar `conta` no `config/bradesco.yaml`
   - Deve ter 12 dígitos (apenas números)

5. **Dígito da conta-corrente inválido (coluna 071)**
   - Verificar `digito_conta` no `config/bradesco.yaml`
   - Deve ser um único caractere alfanumérico

6. **Data de gravação inválida (colunas 144-151)**
   - Verificar se a data está sendo gerada corretamente
   - Formato deve ser AAAAMMDD

## ⚠️ Erro Pendente - Layout do Lote

**Erro:** "Nº versão do layout inválida para forma de lançamento 03-DOC/TED (colunas 014-016)"

**Status:** O código está usando layout 040, mas o validador está rejeitando.

**Possíveis causas:**
1. O layout correto pode ser outro (ex: 041, 042, etc.)
2. Pode ser necessário verificar no manual do Bradesco qual layout usar para TED/DOC

**Ação necessária:**
- Consultar o manual do Bradesco para confirmar o layout do lote correto para TED/DOC
- Verificar se há alguma configuração específica necessária

## 📋 Próximos Passos

1. **Verificar dados no `config/bradesco.yaml`:**
   - CNPJ correto (14 dígitos)
   - Código do convênio correto
   - Agência e conta corretos
   - Dígitos corretos

2. **Verificar layout do lote:**
   - Consultar manual do Bradesco
   - Confirmar qual layout usar para TED/DOC (pode não ser 040)

3. **Testar novamente no validador:**
   - Após corrigir os dados de configuração
   - Verificar se os erros foram resolvidos

## ✅ Resumo

- ✅ **9 correções de código aplicadas**
- ⚠️ **6 erros relacionados a dados de configuração** (precisam ajuste manual)
- ⚠️ **1 erro de layout do lote** (precisa verificar no manual)

