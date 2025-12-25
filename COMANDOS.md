# Comandos para Executar o Projeto

## Opção 1: Com Ambiente Virtual (Recomendado)

### Passo 1: Criar o ambiente virtual
```bash
cd "/Users/gilvanmarques/Library/Mobile Documents/com~apple~CloudDocs/Programação/ConversorPagamentos"
python3 -m venv venv
```

### Passo 2: Ativar o ambiente virtual

**No macOS/Linux:**
```bash
source venv/bin/activate
```

**No Windows:**
```bash
venv\Scripts\activate
```

### Passo 3: Instalar dependências
```bash
pip install -r requirements.txt
```

### Passo 4: Executar o teste rápido
```bash
python test_quick.py
```

### Passo 5: Executar o script principal (com Excel)
```bash
python main.py
```

### Para desativar o ambiente virtual depois:
```bash
deactivate
```

---

## Opção 2: Sem Ambiente Virtual (Instalação Global)

Se preferir instalar as dependências globalmente:

```bash
cd "/Users/gilvanmarques/Library/Mobile Documents/com~apple~CloudDocs/Programação/ConversorPagamentos"
pip3 install -r requirements.txt
python3 test_quick.py
# ou
python3 main.py
```

---

## Comandos Úteis

### Verificar se as dependências estão instaladas
```bash
python3 -c "import pandas, openpyxl, yaml; print('OK')"
```

### Executar testes unitários
```bash
python3 -m unittest discover tests
```

### Verificar estrutura do arquivo gerado
```bash
# Ver primeiras linhas
head -5 output/BRADESCO_PIX_REMESSA_*.txt

# Verificar tamanho de cada linha
python3 -c "
with open('output/BRADESCO_PIX_REMESSA_*.txt', 'r') as f:
    for i, line in enumerate(f, 1):
        line = line.rstrip('\r\n')
        if len(line) != 240:
            print(f'Linha {i}: {len(line)} caracteres')
        elif i <= 5:
            print(f'Linha {i}: OK ({len(line)} caracteres)')
"
```

---

## Troubleshooting

### Erro: "command not found: python3"
Use `python` ao invés de `python3`:
```bash
python --version
python -m venv venv
```

### Erro: "No module named 'pandas'"
Instale as dependências:
```bash
pip install -r requirements.txt
# ou
pip3 install -r requirements.txt
```

### Erro de permissão ao instalar
Use `--user`:
```bash
pip install --user -r requirements.txt
```

