# Layout CNAB 240 - Bradesco Multipag PIX

**IMPORTANTE**: Este documento descreve o layout de **PIX** no Bradesco Multipag (CNAB 240) usando **Segmento J + J-52**.
Se houver divergência entre este documento e o PDF do Bradesco, prevalece o PDF.

## Estrutura do Arquivo

O arquivo CNAB 240 é composto por:

1. Header de Arquivo (Registro 0)
2. Header de Lote (Registro 1)
3. Detalhe Segmento J (Registro 3 - Segmento J)
4. Detalhe Complementar Segmento J-52 (Registro 3 - Segmento J-52) **OBRIGATÓRIO para PIX**
5. Trailer de Lote (Registro 5)
6. Trailer de Arquivo (Registro 9)

---

## 1. HEADER ARQUIVO (Registro 0)

| Campo | Descrição | Posição | Tamanho | Tipo | Preenchimento | Fonte | Referência PDF |
|-------|-----------|---------|---------|------|---------------|-------|----------------|
| Código do Banco | Código do Bradesco | 1-3 | 3 | N | 237 | Fixo | Validar no PDF |
| Lote de Serviço | Número do lote | 4-7 | 4 | N | 0000 | Fixo | Validar no PDF |
| Tipo de Registro | Tipo do registro | 8-8 | 1 | N | 0 | Fixo | Validar no PDF |
| CNAB | Reservado | 9-17 | 9 | AN | Branco | Fixo | Validar no PDF |
| Tipo de Inscrição da Empresa | 1=CPF, 2=CNPJ | 18-18 | 1 | N | Config | Config | Validar no PDF |
| Número de Inscrição da Empresa | CPF/CNPJ | 19-32 | 14 | N | Zeros à esquerda | Config | Validar no PDF |
| Convênio / Código do Convênio | Código convênio | 33-52 | 20 | AN | Brancos à direita | Config | Validar no PDF |
| Agência / Conta | Dados conta | 53-72 | 20 | AN | Brancos/zeros conforme manual | Config | Validar no PDF |
| Nome da Empresa | Razão Social | 73-102 | 30 | AN | Brancos à direita | Config | Validar no PDF |
| Nome do Banco | Nome do banco | 103-132 | 30 | AN | Brancos à direita | Fixo | Validar no PDF |
| CNAB | Reservado | 133-142 | 10 | AN | Branco | Fixo | Validar no PDF |
| Código Remessa/Retorno | 1=Remessa | 143-143 | 1 | N | 1 | Fixo | Validar no PDF |
| Data de Geração | AAAAMMDD | 144-151 | 8 | N | Data | Sistema | Validar no PDF |
| Hora de Geração | HHMMSS | 152-157 | 6 | N | Hora | Sistema | Validar no PDF |
| Número Sequencial do Arquivo | Sequencial | 158-166 | 9 | N | Zeros à esquerda | Config/Sistema | Validar no PDF |
| Layout do Arquivo | Versão do layout | 164-166 | 3 | N | **089** | Config | Validar no PDF |
| CNAB | Reservado | 167-240 | 74 | AN | Branco | Fixo | Validar no PDF |

---

## 2. HEADER LOTE (Registro 1)

| Campo | Descrição | Posição | Tamanho | Tipo | Preenchimento | Fonte | Referência PDF |
|-------|-----------|---------|---------|------|---------------|-------|----------------|
| Código do Banco | Código do Bradesco | 1-3 | 3 | N | 237 | Fixo | Validar no PDF |
| Lote de Serviço | Número do lote | 4-7 | 4 | N | 0001 | Sistema/Config | Validar no PDF |
| Tipo de Registro | Tipo do registro | 8-8 | 1 | N | 1 | Fixo | Validar no PDF |
| Tipo de Operação | C=Crédito | 9-9 | 1 | AN | C | Fixo | Validar no PDF |
| Tipo de Serviço | Pagamentos | 10-11 | 2 | N | 20 | Fixo (PIX) | Validar no PDF |
| Forma de Lançamento | Conforme contrato | 12-13 | 2 | N | Config | Config | Validar no PDF |
| Layout do Lote | Versão do layout | 14-16 | 3 | N | **012** | Config | Validar no PDF |
| CNAB | Reservado | 17-17 | 1 | AN | Branco | Fixo | Validar no PDF |
| Tipo de Inscrição da Empresa | 1=CPF, 2=CNPJ | 18-18 | 1 | N | Config | Config | Validar no PDF |
| Número de Inscrição da Empresa | CPF/CNPJ | 19-32 | 14 | N | Zeros à esquerda | Config | Validar no PDF |
| Convênio / Código do Convênio | Código convênio | 33-52 | 20 | AN | Brancos | Config | Validar no PDF |
| Agência / Conta | Dados conta | 53-72 | 20 | AN | Conforme manual | Config | Validar no PDF |
| Nome da Empresa | Razão Social | 73-102 | 30 | AN | Brancos | Config | Validar no PDF |
| Informações | Reservado/Informativo | 103-240 | 138 | AN | Brancos | Fixo/Config | Validar no PDF |

---

## 3. SEGMENTO J - DETALHE (Registro 3 - Segmento J)

> **Observação**: Este segmento deve ser preenchido conforme tabela do PDF do Bradesco (posições/campos exatos podem variar por modalidade).  
> Mantenha os campos críticos (valor, data, identificadores) parametrizados no YAML quando aplicável.

| Campo | Descrição | Posição | Tamanho | Tipo | Preenchimento | Fonte | Referência PDF |
|-------|-----------|---------|---------|------|---------------|-------|----------------|
| Código do Banco | Código do Bradesco | 1-3 | 3 | N | 237 | Fixo | Validar no PDF |
| Lote de Serviço | Número do lote | 4-7 | 4 | N | Zeros à esquerda | Sistema/Config | Validar no PDF |
| Tipo de Registro | Tipo do registro | 8-8 | 1 | N | 3 | Fixo | Validar no PDF |
| Número Sequencial | Sequencial no lote | 9-13 | 5 | N | Zeros à esquerda | Sistema | Validar no PDF |
| Código Segmento | Segmento | 14-14 | 1 | AN | J | Fixo | Validar no PDF |
| Tipo de Movimento | Inclusão etc. | 15-17 | 3 | N | Config/Fixo | Config | Validar no PDF |
| Seu Número | Controle interno | (ver PDF) | — | AN | — | Excel (id_pagamento) | Validar no PDF |
| Data de Pagamento | AAAAMMDD | (ver PDF) | — | N | Zeros | Excel (data_pagamento) | Validar no PDF |
| Valor | Valor do pagamento | (ver PDF) | — | N | Zeros | Excel (valor) | Validar no PDF |
| Nome Favorecido | Nome | (ver PDF) | — | AN | Brancos | Excel (nome_favorecido) | Validar no PDF |
| Complemento/Histórico | Descrição | (ver PDF) | — | AN | Brancos | Excel (descricao_pagamento) | Validar no PDF |

---

## 4. SEGMENTO J-52 - COMPLEMENTO PIX (Registro 3 - Segmento J-52)

**IMPORTANTE**: Segmento J-52 é **OBRIGATÓRIO** para cada pagamento PIX. Deve ser gerado imediatamente após o Segmento J.

| Campo | Descrição | Posição | Tamanho | Tipo | Preenchimento | Fonte | Observações |
|-------|-----------|---------|---------|------|---------------|-------|------------|
| Código do Banco | Código do Bradesco | 1-3 | 3 | N | 237 | Fixo | Bradesco |
| Lote de Serviço | Número do lote | 4-7 | 4 | N | Zeros à esquerda | Sistema/Config | Ex.: 0001 |
| Tipo de Registro | Tipo do registro | 8-8 | 1 | N | 3 | Fixo | Detalhe |
| Número Sequencial | Sequencial no lote | 9-13 | 5 | N | Zeros à esquerda | Sistema | Incremental por registro no lote |
| Código Segmento | Segmento | 14-14 | 1 | AN | J | Fixo | Segmento J |
| CNAB | Uso exclusivo FEBRABAN | 15-15 | 1 | AN | Branco | Fixo | Deve ser branco |
| Código do Movimento Remessa | Código do movimento | 16-17 | 2 | N | Config/Fixo | Config | Parametrizar (pode variar por operação/contrato) |
| Identificação do Registro Opcional | Identifica registro opcional | 18-19 | 2 | N | 52 | Fixo | Deve ser “52” |

| Devedor - Tipo de Inscrição | 1=CPF, 2=CNPJ | 20-20 | 1 | N | — | Config | Pagador (empresa) |
| Devedor - Número de Inscrição | CPF/CNPJ do devedor | 21-35 | 15 | N | Zeros à esquerda | Config | Zero-fill até 15 |
| Devedor - Nome | Nome do devedor | 36-75 | 40 | AN | Brancos à direita | Config | Nome do pagador |

| Favorecido - Tipo de Inscrição | 1=CPF, 2=CNPJ | 76-76 | 1 | N | — | Excel | Mapear: F→1, J→2 |
| Favorecido - Número de Inscrição | CPF/CNPJ favorecido | 77-91 | 15 | N | Zeros à esquerda | Excel | CPF(11)/CNPJ(14) com zero-fill até 15 |
| Favorecido - Nome | Nome do favorecido | 92-131 | 40 | AN | Brancos à direita | Excel | Truncar se exceder 40 |

| URL/Chave de Endereçamento | Chave PIX / URL / endereçamento | 132-210 | 79 | AN | Brancos à direita | Excel (chave_pix) | Chave PIX sanitizada; truncar com log se >79 |
| TXID | Identificador da transação | 211-240 | 30 | AN | Brancos à direita | Sistema/Excel | Se não houver, preencher com brancos ou gerar conforme regra do banco |

**Notas de implementação (recomendado)**:
- “Código do Movimento Remessa” (16-17) deve ser parametrizado no YAML.
- Para o “Favorecido - Número de Inscrição” (77-91), usar apenas dígitos e zero-fill até 15.
- “URL/Chave de Endereçamento” (132-210) recebe a chave PIX (texto), sem máscara.

---

## 5. TRAILER LOTE (Registro 5)

| Campo | Descrição | Posição | Tamanho | Tipo | Preenchimento | Fonte | Referência PDF |
|-------|-----------|---------|---------|------|---------------|-------|----------------|
| Código do Banco | Código do Bradesco | 1-3 | 3 | N | 237 | Fixo | Validar no PDF |
| Lote de Serviço | Número do lote | 4-7 | 4 | N | Zeros à esquerda | Sistema/Config | Validar no PDF |
| Tipo de Registro | Tipo do registro | 8-8 | 1 | N | 5 | Fixo | Validar no PDF |
| CNAB | Reservado | 9-17 | 9 | AN | Branco | Fixo | Validar no PDF |
| Quantidade de Registros | Total no lote | 18-23 | 6 | N | Zeros à esquerda | Sistema | Validar no PDF |
| Somatória dos Valores | Soma valores | 24-41 | 18 | N | Zeros à esquerda | Sistema | Validar no PDF |
| CNAB | Reservado | 42-240 | 199 | AN | Branco | Fixo | Validar no PDF |

---

## 6. TRAILER ARQUIVO (Registro 9)

| Campo | Descrição | Posição | Tamanho | Tipo | Preenchimento | Fonte | Referência PDF |
|-------|-----------|---------|---------|------|---------------|-------|----------------|
| Código do Banco | Código do Bradesco | 1-3 | 3 | N | 237 | Fixo | Validar no PDF |
| Lote de Serviço | Número do lote | 4-7 | 4 | N | 9999 | Fixo | Validar no PDF |
| Tipo de Registro | Tipo do registro | 8-8 | 1 | N | 9 | Fixo | Validar no PDF |
| CNAB | Reservado | 9-17 | 9 | AN | Branco | Fixo | Validar no PDF |
| Quantidade de Lotes | Total lotes | 18-23 | 6 | N | Zeros à esquerda | Sistema | Validar no PDF |
| Quantidade de Registros | Total registros | 24-29 | 6 | N | Zeros à esquerda | Sistema | Validar no PDF |
| CNAB | Reservado | 30-240 | 211 | AN | Branco | Fixo | Validar no PDF |

---

## Mapeamento de Tipos de Chave PIX

> Observação: o Segmento J-52 (URL/Chave) recebe a chave em texto.  
> O tipo pode ser validado na aplicação (validate.py) conforme regras.

- CPF: 11 dígitos
- CNPJ: 14 dígitos
- EMAIL: contém "@"
- TELEFONE: somente dígitos (preferencialmente com DDI, ex.: 55...)
- ALEATORIA: 32 ou 36 caracteres

---

## Observações Importantes

- Encoding recomendado: evitar UTF-8 com BOM.
- Cada linha deve ter exatamente 240 caracteres + CRLF (\r\n).
- Truncamentos devem ser logados (nome/descrição/chave).

---

## VALIDAÇÃO CONTRA O PDF

- Confirmar no PDF:
  - códigos fixos do Header de Lote para modalidade PIX
  - campos do Segmento J (posições exatas, pois variam conforme o serviço/contrato)
  - regra do TXID (se branco é aceito, se obrigatório, se gerado, etc.)

---

## Escopo

Este documento descreve **somente** o layout de **PIX** no Bradesco Multipag (CNAB 240), utilizando **Segmento J + J-52**.  
Segmentos A/B devem ser tratados em documento separado, caso o projeto seja expandido para TED/DOC.
