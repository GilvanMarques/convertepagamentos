# Gerador de REMESSA CNAB 240 - PIX Bradesco Multipag

Sistema para geração de arquivos de remessa CNAB 240 para pagamentos PIX via Bradesco Multipag.

## Estrutura do Projeto

```
ConversorPagamentos/
├── src/
│   └── cnab240/
│       ├── __init__.py
│       ├── bradesco_pix.py      # Geração de registros CNAB 240
│       ├── fields.py             # Formatadores de campos
│       ├── validate.py           # Validações
│       └── config.py             # Carregamento de configuração
├── config/
│   └── bradesco.yaml             # Configuração da empresa/conta
├── docs/
│   └── layout_pix_bradesco.md    # Documentação do layout
├── tests/
│   ├── test_fields.py            # Testes dos formatadores
│   └── test_validate.py          # Testes das validações
├── output/                       # Arquivos gerados
├── main.py                       # Script principal
├── requirements.txt              # Dependências Python
└── README.md                     # Este arquivo
```

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure o arquivo `config/bradesco.yaml` com os dados da sua empresa e conta:
```yaml
empresa:
  tipo_inscricao: 2  # 1=CPF, 2=CNPJ
  numero_inscricao: "12345678000190"
  nome: "SUA EMPRESA LTDA"

conta:
  codigo_convenio: "12345678901234567890"
  agencia: "1234"
  digito_agencia: "5"
  conta: "123456789012"
  digito_conta: "7"
  digito_verificador: ""
```

## Uso

1. Prepare o arquivo Excel `Pagamentos_Excel.xlsx` na raiz do projeto com as seguintes colunas na primeira aba:

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| id_pagamento | Identificador único do pagamento | 001 |
| data_pagamento | Data do pagamento (YYYY-MM-DD ou DD/MM/YYYY) | 2024-12-31 |
| valor | Valor do pagamento (2 decimais) | 100.50 |
| nome_favorecido | Nome do favorecido (máx 30 caracteres) | João Silva |
| tipo_pessoa | F (Física) ou J (Jurídica) | F |
| cpf_cnpj | CPF (11 dígitos) ou CNPJ (14 dígitos) | 12345678901 |
| tipo_chave_pix | CPF, CNPJ, EMAIL, TELEFONE ou ALEATORIA | CPF |
| chave_pix | Chave PIX conforme o tipo (máx 100 caracteres) | 12345678901 |
| descricao_pagamento | Descrição do pagamento (opcional) | Pagamento de serviços |
| aviso_favorecido | 0 (não avisar) ou 1 (avisar) | 0 |
| txid | Identificador único da transação (opcional, gerado automaticamente se não fornecido) | E1234567890123456789012345678 |

2. Execute o script:
```bash
python main.py
```

3. Os arquivos serão gerados em `output/`:
   - `BRADESCO_PIX_REMESSA_YYYYMMDD_NNNNNN.txt` - Arquivo CNAB 240
   - `relatorio_validacao.csv` - Relatório de validação

## Validações

O sistema realiza as seguintes validações:

### Validações de Entrada
- `id_pagamento` único
- `data_pagamento` válida e >= hoje
- `valor` > 0 com no máximo 2 decimais
- `cpf_cnpj` numérico com 11 dígitos (CPF) ou 14 dígitos (CNPJ)
- `chave_pix` válida conforme `tipo_chave_pix`
- Truncamento automático de campos que excedem tamanho (com log)

### Validações de Arquivo CNAB
- Todas as linhas com exatamente 240 caracteres
- Estrutura correta (Header, Lote, Detalhes, Trailers)
- Trailers conferem com totais calculados

## Formato do Arquivo CNAB 240

O arquivo gerado segue o layout CNAB 240 do Bradesco Multipag para PIX:

1. **Header Arquivo** (Registro 0) - Layout 089
2. **Header Lote** (Registro 1) - Layout 012
3. **Detalhes** (Registro 3):
   - **Segmento J** (dados do pagamento)
   - **Segmento J-52** (complemento PIX com chave e TXID) - OBRIGATÓRIO
4. **Trailer Lote** (Registro 5)
5. **Trailer Arquivo** (Registro 9)

**IMPORTANTE**: Para PIX no Bradesco Multipag, utiliza-se **Segmento J e J-52** (não Segmento A/B).
O Segmento A/B é usado apenas para TED/DOC, não para PIX.

Cada registro tem exatamente 240 caracteres + CRLF (\r\n).

Para detalhes completos do layout, consulte `docs/layout_pix_bradesco.md`.

## Tipos de Chave PIX

| Tipo | Código CNAB | Descrição |
|------|-------------|-----------|
| CPF | 1 | CPF do favorecido |
| CNPJ | 2 | CNPJ do favorecido |
| EMAIL | 3 | E-mail do favorecido |
| TELEFONE | 4 | Telefone do favorecido |
| ALEATORIA | 5 | Chave aleatória (UUID) |

## Testes

### Teste Rápido

Para um teste rápido sem precisar do Excel:

```bash
python test_quick.py
```

Este script:
- Cria dados de teste válidos
- Valida os pagamentos
- Gera o arquivo CNAB
- Verifica estrutura, tamanhos e trailers
- Exibe resumo dos resultados

### Testes Unitários

Execute os testes unitários:
```bash
python -m unittest discover tests
```

### Teste Completo com Excel

1. Prepare o arquivo `Pagamentos_Excel.xlsx` (veja seção "Uso" acima)
2. Execute:
```bash
python main.py
```

Para mais detalhes, consulte `TESTE.md`.

## Logs

O sistema gera logs detalhados no console informando:
- Total de pagamentos processados
- Total de registros gerados
- Soma dos valores
- Confirmação de validações
- Erros e avisos

## Observações Importantes

1. **Layout do PDF**: O sistema foi implementado baseado no padrão CNAB 240 Bradesco Multipag para PIX. **VALIDE** o arquivo `jun-19-layout-multipag.pdf` e ajuste os campos em `src/cnab240/bradesco_pix.py` e documente em `docs/layout_pix_bradesco.md` se houver diferenças.

2. **Versões de Layout**: 
   - Layout do Arquivo: **089** (configurável em `config/bradesco.yaml`)
   - Layout do Lote: **012** (configurável em `config/bradesco.yaml`)

3. **Segmento J e J-52**: O sistema utiliza **Segmento J** (detalhe) + **Segmento J-52** (complemento PIX) para cada pagamento. O Segmento J-52 é **OBRIGATÓRIO** e contém a chave PIX e o TXID.

4. **Campos não mapeados**: Se o layout exigir campos específicos que não estão na planilha, adicione-os no `config/bradesco.yaml` e documente no README.

5. **Validação de CPF/CNPJ**: O sistema valida dígitos verificadores. Certifique-se de que os CPFs/CNPJs estão corretos.

6. **Encoding**: O arquivo CNAB é gerado em ASCII. Caracteres especiais são removidos automaticamente.

7. **TXID**: O sistema gera automaticamente um TXID (identificador único) para cada transação PIX. Se necessário, pode ser fornecido no Excel através da coluna `txid`.

## Suporte

Para dúvidas ou problemas, consulte:
- `docs/layout_pix_bradesco.md` - Documentação completa do layout
- Logs gerados durante a execução
- Relatório de validação em CSV

