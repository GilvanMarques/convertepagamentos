# Guia de Validação Manual - PIX Bradesco Multipag

## 📋 Checklist de Validação

Use este guia para validar manualmente o arquivo gerado contra os manuais do Bradesco.

## Arquivos Necessários

1. **Manual Principal**: `Manuais/Multipag_Bradesco_PIX_240_posicoes.pdf`
2. **Arquivo Gerado**: `output/BRADESCO_PIX_REMESSA_*.txt`
3. **Documentação**: `docs/layout_pix_bradesco.md`

---

## Passo 1: Validar Header Arquivo (Linha 1)

Abra o PDF `Multipag_Bradesco_PIX_240_posicoes.pdf` e localize a seção **"Header de Arquivo"** ou **"Registro 0"**.

### Campos a Verificar:

| Posição | Campo | Valor Esperado | Status |
|---------|-------|----------------|--------|
| 1-3 | Código do Banco | 237 | ⬜ |
| 4-7 | Lote de Serviço | 0000 | ⬜ |
| 8 | Tipo de Registro | 0 | ⬜ |
| 164-166 | Layout do Arquivo | 089 | ⬜ |
| 143-151 | Data de Geração | AAAAMMDD | ⬜ |

**Ação**: Compare cada posição do arquivo gerado com a tabela do PDF.

---

## Passo 2: Validar Header Lote (Linha 2)

Localize a seção **"Header de Lote"** ou **"Registro 1"** no PDF.

### Campos Críticos:

| Posição | Campo | Valor Esperado | Status |
|---------|-------|----------------|--------|
| 1-3 | Código do Banco | 237 | ⬜ |
| 4-7 | Lote de Serviço | 0001 | ⬜ |
| 8 | Tipo de Registro | 1 | ⬜ |
| 9 | Tipo de Operação | C | ⬜ |
| 10-11 | Tipo de Serviço | 20 | ⬜ |
| 12-13 | Forma de Lançamento | 41 (PIX) | ⬜ |
| **14-16** | **Layout do Lote** | **012** | ⬜ ⚠️ |

**Ação**: Confirme especialmente o **Layout do Lote (012)** nas posições 14-16.

---

## Passo 3: Validar Segmento J (Linha 3)

Localize a seção **"Segmento J"** ou **"Registro 3 - Segmento J"** no PDF.

### Campos a Verificar:

| Posição | Campo | Observação |
|---------|-------|------------|
| 1-3 | Código do Banco | 237 |
| 4-7 | Lote de Serviço | 0001 |
| 8 | Tipo de Registro | 3 |
| 9-13 | Número Sequencial | Incremental |
| 14 | Código Segmento | J |
| (ver PDF) | Valor do Pagamento | Em centavos |
| (ver PDF) | Data de Pagamento | AAAAMMDD |

**Ação**: 
- Anote as posições exatas dos campos no PDF
- Compare com o arquivo gerado
- Verifique se o valor está na posição correta

---

## Passo 4: Validar Segmento J-52 (Linha 4) ⚠️ CRÍTICO

Localize a seção **"Segmento J-52"** ou **"Registro Opcional 52"** no PDF.

### Campos OBRIGATÓRIOS a Verificar:

| Posição | Campo | Valor/Formato | Status |
|---------|-------|---------------|--------|
| 1-3 | Código do Banco | 237 | ⬜ |
| 4-7 | Lote de Serviço | 0001 | ⬜ |
| 8 | Tipo de Registro | 3 | ⬜ |
| 9-13 | Número Sequencial | Incremental | ⬜ |
| 14 | Código Segmento | J | ⬜ |
| **15** | **CNAB** | **Branco** | ⬜ ⚠️ |
| **16-17** | **Código Movimento** | **01 (ou conforme PDF)** | ⬜ ⚠️ |
| **18-19** | **Registro Opcional** | **52** | ⬜ ⚠️ |
| **20** | **Devedor - Tipo Inscrição** | **1 ou 2** | ⬜ |
| **21-35** | **Devedor - CPF/CNPJ** | **15 posições, zero-fill** | ⬜ |
| **36-75** | **Devedor - Nome** | **40 posições** | ⬜ |
| **76** | **Favorecido - Tipo Inscrição** | **1 ou 2** | ⬜ |
| **77-91** | **Favorecido - CPF/CNPJ** | **15 posições, zero-fill** | ⬜ |
| **92-131** | **Favorecido - Nome** | **40 posições** | ⬜ |
| **132-210** | **Chave PIX** | **79 posições** | ⬜ ⚠️ |
| **211-240** | **TXID** | **30 posições** | ⬜ ⚠️ |

**Ação CRÍTICA**: 
1. Abra o PDF na página do Segmento J-52
2. Anote **EXATAMENTE** as posições de cada campo
3. Compare campo a campo com o arquivo gerado
4. Verifique especialmente:
   - Se a posição 15 é realmente branco
   - Se "52" está nas posições 18-19
   - Se a Chave PIX está nas posições 132-210 (79 caracteres)
   - Se o TXID está nas posições 211-240 (30 caracteres)

---

## Passo 5: Validar Trailers

### Trailer Lote (Linha 5)

| Posição | Campo | Verificação |
|---------|-------|-------------|
| 1-3 | Código do Banco | 237 |
| 4-7 | Lote de Serviço | 0001 |
| 8 | Tipo de Registro | 5 |
| 18-23 | Quantidade de Registros | Deve ser 4 (Header + J + J-52 + Trailer) |
| 24-29 | Quantidade de Títulos | Deve ser 1 (ou número de pagamentos) |
| 30-46 | Valor Total | Deve somar todos os valores |

### Trailer Arquivo (Linha 6)

| Posição | Campo | Verificação |
|---------|-------|-------------|
| 1-3 | Código do Banco | 237 |
| 4-7 | Lote de Serviço | 9999 |
| 8 | Tipo de Registro | 9 |
| 18-23 | Quantidade de Lotes | Deve ser 1 |
| 24-29 | Quantidade de Registros | Deve ser 6 (Header Arquivo + 4 do lote + Trailer Arquivo) |

---

## Passo 6: Validação de Tamanho

✅ Todas as linhas devem ter **exatamente 240 caracteres** (sem contar CRLF)

Para verificar:
```bash
python3 -c "
with open('output/BRADESCO_PIX_REMESSA_*.txt', 'r') as f:
    for i, line in enumerate(f, 1):
        line = line.rstrip('\r\n')
        if len(line) != 240:
            print(f'ERRO Linha {i}: {len(line)} caracteres')
        else:
            print(f'OK Linha {i}: 240 caracteres')
"
```

---

## Passo 7: Comparação Campo a Campo

### Método Recomendado:

1. **Abra o PDF** `Multipag_Bradesco_PIX_240_posicoes.pdf`
2. **Localize a tabela do Segmento J-52**
3. **Abra o arquivo gerado** em um editor de texto
4. **Para cada campo na tabela do PDF**:
   - Anote a posição inicial e final
   - Extraia o campo do arquivo gerado
   - Compare com o esperado
   - Marque ✅ ou ❌

### Exemplo de Comparação:

```
PDF diz: Posição 132-210 = Chave PIX (79 caracteres)
Arquivo gerado linha 4, posição 132-210: "79981297987                    ..."
✅ Campo está na posição correta
✅ Tamanho está correto (79 caracteres)
```

---

## ⚠️ Pontos de Atenção Especiais

### 1. Layout do Lote
- **Verificar**: PDF deve confirmar que é "012" (não "010" ou outro valor)
- **Posição**: 14-16 no Header Lote

### 2. Segmento J-52 - Posição 15
- **Verificar**: PDF deve confirmar que deve ser branco
- **Atual**: Implementado como branco

### 3. Segmento J-52 - Posição 18-19
- **Verificar**: PDF deve confirmar que deve ser "52"
- **Atual**: Implementado como "52"

### 4. Chave PIX
- **Verificar**: PDF deve confirmar posições 132-210 (79 caracteres)
- **Atual**: Implementado nas posições 132-210

### 5. TXID
- **Verificar**: PDF deve confirmar posições 211-240 (30 caracteres)
- **Verificar**: PDF deve dizer se pode ser branco ou se é obrigatório
- **Atual**: Implementado nas posições 211-240, gerado automaticamente se não fornecido

---

## 📝 Template de Anotação

Use esta tabela para anotar divergências encontradas:

| Campo | Posição no PDF | Posição no Código | Divergência? | Ação Necessária |
|-------|----------------|-------------------|--------------|-----------------|
| Layout Lote | 14-16 | 14-16 | ⬜ | |
| J-52 Pos 15 | 15 | 15 | ⬜ | |
| J-52 Pos 18-19 | 18-19 | 18-19 | ⬜ | |
| Chave PIX | ?-? | 132-210 | ⬜ | |
| TXID | ?-? | 211-240 | ⬜ | |

---

## ✅ Conclusão da Validação

Após completar a validação:

- [ ] Todas as posições conferem com o PDF
- [ ] Todos os códigos fixos estão corretos
- [ ] Todos os tamanhos de campo estão corretos
- [ ] Trailers conferem
- [ ] Arquivo está pronto para homologação

**Se encontrar divergências**:
1. Anote exatamente qual campo
2. Anote a posição no PDF vs posição no código
3. Corrija o código
4. Atualize a documentação
5. Regenere o arquivo e valide novamente

---

## 🚀 Próximo Passo Após Validação

Se tudo estiver correto:
1. Gerar arquivo de teste com dados reais (mas valores pequenos)
2. Enviar para homologação no Bradesco
3. Acompanhar retorno
4. Ajustar conforme feedback do banco

