"""
Carregamento de configuração do arquivo YAML
"""
import os
from pathlib import Path


def load_config(config_path: str | None = None) -> dict:
    """
    Carrega configuração do arquivo YAML.
    
    Args:
        config_path: Caminho para o arquivo de configuração
    
    Returns:
        Dicionário com as configurações
    
    Raises:
        ImportError: Se o PyYAML não estiver instalado
        FileNotFoundError: Se o arquivo de configuração não for encontrado
    """
    # Importação lazy do yaml (só importa quando necessário)
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "Módulo PyYAML não encontrado. "
            "Instale com: pip install PyYAML ou pip install -r requirements.txt"
        )
    
    if config_path is None:
        # Tenta encontrar o arquivo de config no diretório config/
        base_dir = Path(__file__).parent.parent.parent
        config_path = base_dir / 'config' / 'bradesco.yaml'
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config




