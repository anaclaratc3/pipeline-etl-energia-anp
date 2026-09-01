import pandas as pd
from pathlib import Path

# Define os caminhos para os arquivos de dados brutos
PASTA_RAIZ = Path(__file__).parent.parent
PASTA_DADOS_BRUTOS = PASTA_RAIZ / "dados" / "brutos"

# Mapea os nomes dos arquivos CSV para suas respectivas chaves
ARQUIVOS = {
    "gas_natural": "importacao_gas_natural_2000_2025.csv",
    "derivados": "importacao_exportacao_derivados_2000_2025.csv",
    "etanol": "importacao_exportacao_etanol_2012_2025.csv",
    "petroleo": "importacao_exportacao_petroleo_2000_2025.csv"
}
# Le os arquivos CSV da pasta de dados brutos com tratamento de encoding
def carregar_dados_brutos():
    
    dataframes = {}
    
    print("=== INICIANDO EXTRAÇÃO DOS DADOS BRUTOS ===\n")
    
    for chave, nome_arquivo in ARQUIVOS.items():
        caminho_completo = PASTA_DADOS_BRUTOS / nome_arquivo

        # Fallback para tratamento de codificação de caracteres
        try:
            df = pd.read_csv(
                caminho_completo,
                encoding="utf-8-sig",
                sep=None,
                engine="python",
                )
        except UnicodeDecodeError:
            df = pd.read_csv(
                caminho_completo,
                encoding="latin1",
                sep=None,
                engine="python",
                )
            
        dataframes[chave] = df
        
        # Log de confirmação e inspeção
        print(f"Arquivo [{nome_arquivo}] carregado com sucesso!")
        print(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
        print(f"Colunas: {list(df.columns)}\n")
        
    return dataframes

if __name__ == "__main__":
    dfs_brutos = carregar_dados_brutos()