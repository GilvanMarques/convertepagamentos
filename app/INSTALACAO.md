# Instalação das Dependências

## ⚠️ Erro: ModuleNotFoundError

Se você está vendo o erro `ModuleNotFoundError: No module named 'yaml'` ou similar, significa que as dependências não estão instaladas.

## ✅ Solução

Execute o seguinte comando no terminal:

```bash
pip install -r requirements.txt
```

Ou instale as dependências individualmente:

```bash
pip install pandas>=2.0.0
pip install openpyxl>=3.1.0
pip install PyYAML>=6.0
pip install streamlit>=1.28.0
```

## 🔍 Verificar Instalação

Para verificar se as dependências estão instaladas:

```bash
pip list | grep -E "pandas|openpyxl|PyYAML|streamlit"
```

## 🚀 Executar a Aplicação

Após instalar as dependências:

```bash
streamlit run app/streamlit_app.py
```

## 💡 Usando Ambiente Virtual (Recomendado)

É recomendado usar um ambiente virtual:

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# No macOS/Linux:
source venv/bin/activate
# No Windows:
# venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app/streamlit_app.py
```

