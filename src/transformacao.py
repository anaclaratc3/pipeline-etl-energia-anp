from pathlib import Path
import pandas as pd
from extracao import carregar_dados_brutos

# Define os caminhos para os arquivos de dados processados
PASTA_RAIZ = Path(__file__).parent.parent
PASTA_DADOS_PROCESSADOS = PASTA_RAIZ / "dados" / "processados"


def limpar_string_numerica(serie: pd.Series) -> pd.Series:
    """Converte valores com vírgula brasileira para float no padrão internacional (ponto)"""
    def converter_valor(val):
        s = str(val).strip()
        if not s or s.lower() in ["nan", "none", "null"]:
            return 0.0

        s = s.replace(".", "").replace(",", ".")

        try:
            return float(s)
        except ValueError:
            return 0.0

    return serie.apply(converter_valor)


def transformar_dados(dataframes: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Padroniza, limpa, consolida e gera métricas analíticas."""
    dfs_tratados = []

    print("=== INICIANDO ETAPA DE TRANSFORMAÇÃO ===\n")

    mapeamento_colunas = {
        "ANO": "ano",
        "MÊS": "mes",
        "PRODUTO": "produto",
        "OPERAÇÃO COMERCIAL": "operacao_comercial",
        "IMPORTADO": "volume_m3",
        "IMPORTADO / EXPORTADO": "volume_m3",
        "DISPÊNDIO": "valor_dolar",
        "DISPÊNDIO / RECEITA": "valor_dolar",
    }

    meses_map = {
        "JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4, "MAI": 5, "JUN": 6,
        "JUL": 7, "AGO": 8, "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12,
        "JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3, "ABRIL": 4, "MAIO": 5, "JUNHO": 6,
        "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12
    }

    for chave, df in dataframes.items():
        df_temp = df.copy()

        # Padroniza nomes das colunas
        df_temp = df_temp.rename(columns=mapeamento_colunas)

        # Mapeia a coluna mes para numero
        df_temp["mes"] = df_temp["mes"].astype(str).str.strip().str.upper().map(meses_map)

        # Identifica a categoria do combustível
        df_temp["categoria"] = chave.replace("_", " ").title()

        dfs_tratados.append(df_temp)

    # Unifica todos os DataFrames tratados em um unico DataFrame consolidado
    df_consolidado = pd.concat(dfs_tratados, ignore_index=True)

    # Converte Ano e Mes para numeros inteiros
    df_consolidado["ano"] = pd.to_numeric(df_consolidado["ano"], errors="coerce").astype("Int64")
    df_consolidado["mes"] = pd.to_numeric(df_consolidado["mes"], errors="coerce").astype("Int64")

    # Converte Volume e Valor Financeiro para float
    df_consolidado["volume_m3"] = limpar_string_numerica(df_consolidado["volume_m3"])
    df_consolidado["valor_dolar"] = limpar_string_numerica(df_consolidado["valor_dolar"])

    # Padroniza strings de texto
    df_consolidado["produto"] = df_consolidado["produto"].astype(str).str.strip()
    df_consolidado["operacao_comercial"] = df_consolidado["operacao_comercial"].astype(str).str.strip()

    # Remove registros com volume e valor nulos ou zero
    df_consolidado = df_consolidado[
        (df_consolidado["volume_m3"] > 0) | (df_consolidado["valor_dolar"] > 0)
    ].copy()

    # Cria uma data de referencia para cada registro no formato YYYY-MM-01
    df_consolidado["data_referencia"] = pd.to_datetime(
        df_consolidado["ano"].astype(str) + "-" + df_consolidado["mes"].astype(str).str.zfill(2) + "-01"
    )

    # Calcula preço médio por m3
    df_consolidado["preco_medio_m3"] = (
        (df_consolidado["valor_dolar"] / df_consolidado["volume_m3"])
        .replace([float("inf"), float("-inf")], 0.0)
        .fillna(0.0)
    )

    # Padroniza flag de Fluxo Comercial
    df_consolidado["tipo_fluxo"] = df_consolidado["operacao_comercial"].apply(
        lambda x: "IMPORTAÇÃO" if "IMPORTA" in str(x).upper() else ("EXPORTAÇÃO" if "EXPORTA" in str(x).upper() else "OUTROS")
    )

    print("Transformação dos dados concluída com sucesso!")
    print(f"Total de registros finais: {len(df_consolidado)} linhas")
    print("Novas colunas analíticas adicionadas: ['data_referencia', 'preco_medio_m3', 'tipo_fluxo']")
    print(f"Lista de colunas finais: {list(df_consolidado.columns)}\n")

    return df_consolidado


def salvar_dados_processados(df: pd.DataFrame) -> None:
    """Salva o DataFrame tratado na pasta dados/processados em formatos CSV e Parquet."""
    PASTA_DADOS_PROCESSADOS.mkdir(parents=True, exist_ok=True)

    caminho_csv = PASTA_DADOS_PROCESSADOS / "comercio_exterior_combustiveis.csv"
    caminho_parquet = PASTA_DADOS_PROCESSADOS / "comercio_exterior_combustiveis.parquet"

    df.to_csv(caminho_csv, index=False, encoding="utf-8")
    df.to_parquet(caminho_parquet, index=False)

    print("Arquivos salvos com sucesso em dados/processados/:")
    print(f"{caminho_csv.name}")
    print(f"{caminho_parquet.name}\n")


if __name__ == "__main__":
    dfs_brutos = carregar_dados_brutos()
    df_final = transformar_dados(dfs_brutos)
    salvar_dados_processados(df_final)