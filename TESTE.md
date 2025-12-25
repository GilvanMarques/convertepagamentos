# Guia de Teste - Gerador CNAB 240 PIX Bradesco

## Pré-requisitos

1. Python 3.8 ou superior instalado
2. Dependências instaladas

## Passo 1: Instalar Dependências

```bash
pip install -r requirements.txt
```

## Passo 2: Configurar o Arquivo de Configuração

Edite o arquivo `config/bradesco.yaml` com os dados da sua empresa:

```yaml
empresa:
  tipo_inscricao: 2  # 1=CPF, 2=CNPJ
  numero_inscricao: "12345678000190"  # Seu CPF/CNPJ
  nome: "SUA EMPRESA LTDA"  # Nome da empresa

conta:
  codigo_convenio: "12345678901234567890"  # Código do convênio
  agencia: "1234"  # Agência
  digito_agencia: "5"  # Dígito da agência
  conta: "123456789012"  # Conta corrente
  digito_conta: "7"  # Dígito da conta
  digito_verificador: ""  # DV Ag/Conta (se houver)

arquivo:
  sequencial_inicial: 1
  layout_arquivo: 089
  layout_lote: 012
```

## Passo 3: Preparar o Arquivo Excel

O arquivo `Pagamentos_Excel.xlsx` deve estar na raiz do projeto com as seguintes colunas na **primeira aba**:

| Coluna | Exemplo | Observação |
|--------|---------|------------|
| id_pagamento | 001 | Identificador único |
| data_pagamento | 2024-12-31 | Data futura (>= hoje) |
| valor | 100.50 | Valor com 2 decimais |
| nome_favorecido | João Silva | Máx 30 caracteres |
| tipo_pessoa | F | F ou J |
| cpf_cnpj | 12345678901 | 11 dígitos (CPF) ou 14 (CNPJ) |
| tipo_chave_pix | CPF | CPF, CNPJ, EMAIL, TELEFONE ou ALEATORIA |
| chave_pix | 12345678901 | Chave PIX conforme tipo |
| descricao_pagamento | Pagamento teste | Opcional |
| aviso_favorecido | 0 | 0 ou 1 |
| txid | E1234567890123456789012345678 | Opcional (gerado automaticamente se não fornecido) |

**Exemplo mínimo de dados válidos:**
- id_pagamento: 001
- data_pagamento: 2024-12-31
- valor: 100.50
- nome_favorecido: João Silva
- tipo_pessoa: F
- cpf_cnpj: 11144477735 (CPF válido para teste)
- tipo_chave_pix: CPF
- chave_pix: 11144477735
- aviso_favorecido: 0

## Passo 4: Executar o Script Principal

```bash
python main.py
```

## Passo 5: Verificar os Resultados

### Arquivos Gerados

1. **Arquivo CNAB 240**: `output/BRADESCO_PIX_REMESSA_YYYYMMDD_NNNNNN.txt`
   - Verifique se todas as linhas têm exatamente 240 caracteres
   - Verifique se termina com CRLF (\r\n)

2. **Relatório de Validação**: `output/relatorio_validacao.csv`
   - Verifique quais pagamentos foram processados com sucesso (status OK)
   - Verifique quais tiveram erros (status ERRO)

### Logs no Console

O script exibe:
- Total de pagamentos processados
- Total de registros gerados
- Valor total
- Confirmação de validações

## Passo 6: Validar o Arquivo CNAB

### Validação Manual

1. **Tamanho das linhas**: Cada linha deve ter exatamente 240 caracteres
   ```bash
   # No Linux/Mac
   while IFS= read -r line; do echo "${#line}"; done < output/BRADESCO_PIX_REMESSA_*.txt
   
   # Ou use Python
   python -c "
   with open('output/BRADESCO_PIX_REMESSA_*.txt', 'r') as f:
       for i, line in enumerate(f, 1):
           line = line.rstrip('\r\n')
           if len(line) != 240:
               print(f'Linha {i}: {len(line)} caracteres')
   "
   ```

2. **Estrutura do arquivo**:
   - Linha 1: Header Arquivo (tipo 0)
   - Linha 2: Header Lote (tipo 1)
   - Linhas 3+: Detalhes (Segmento J e J-52)
   - Penúltima linha: Trailer Lote (tipo 5)
   - Última linha: Trailer Arquivo (tipo 9)

3. **Trailers**:
   - Quantidade de registros deve conferir
   - Valor total deve conferir

### Validação Programática

Execute os testes unitários:

```bash
python -m unittest discover tests
```

## Passo 7: Testar Casos Especiais

### Teste 1: Múltiplos Pagamentos

Adicione vários pagamentos no Excel e verifique se todos são processados.

### Teste 2: Chaves PIX Longas

Teste com chave PIX de até 100 caracteres (será truncada se maior).

### Teste 3: Validação de Erros

Teste com dados inválidos:
- CPF/CNPJ inválido
- Data no passado
- Valor zero ou negativo
- Chave PIX inválida

### Teste 4: TXID Personalizado

Forneça um TXID no Excel e verifique se é usado ao invés do gerado automaticamente.

## Passo 8: Verificar Conformidade com o PDF

1. Abra o arquivo `jun-19-layout-multipag.pdf`
2. Compare os campos gerados com o manual
3. Verifique especialmente:
   - Posições dos campos no Segmento J-52
   - Formato da chave PIX
   - Posição do TXID
   - Versões de layout (089 e 012)

## Troubleshooting

### Erro: "Arquivo Excel não encontrado"
- Verifique se `Pagamentos_Excel.xlsx` está na raiz do projeto
- Verifique se o nome do arquivo está correto

### Erro: "Arquivo de configuração não encontrado"
- Verifique se `config/bradesco.yaml` existe
- Verifique se os dados estão preenchidos

### Erro: "Nenhum pagamento válido"
- Verifique o relatório de validação em CSV
- Corrija os erros indicados

### Arquivo gerado com tamanho incorreto
- Verifique os logs para truncamentos
- Verifique se há caracteres especiais que precisam ser sanitizados

## Exemplo de Teste Rápido

Crie um arquivo Excel mínimo com 1 pagamento válido e execute:

```bash
python main.py
```

Verifique:
1. ✅ Arquivo gerado em `output/`
2. ✅ Todas as linhas com 240 caracteres
3. ✅ Relatório de validação mostra status OK
4. ✅ Logs mostram totais corretos

