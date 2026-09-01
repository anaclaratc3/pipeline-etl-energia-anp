import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.types import Date, Float, Integer, String

# Localiza a raiz do projeto e carrega as variáveis do .env
PASTA_RAIZ = Path(__file__).parent.parent
load_dotenv(PASTA_RAIZ / ".env")


def obter_engine_banco():
    """Cria a engine de conexão com o PostgreSQL do Neon usando SQLAlchemy."""
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if not all([host, database, user, password]):
        raise ValueError("Credenciais do banco de dados não encontradas no arquivo .env!")

    # Monta a URL de conexão exigindo criptografia SSL para nuvem
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require"
    return create_engine(db_url, echo=False)


def carregar_dados_banco(df: pd.DataFrame, nome_tabela: str = "fato_comercio_exterior") -> None:
    """Insere os dados no banco PostgreSQL do Neon com tipagem explícita."""
    print("=== INICIANDO ETAPA DE CARGA (POSTGRESQL - NEON) ===\n")
    
    engine = obter_engine_banco()

    # Mapeamento de tipos de dados para criação da tabela no banco
    schema_tipos = {
        "ano": Integer(),
        "mes": Integer(),
        "produto": String(100),
        "operacao_comercial": String(100),
        "volume_m3": Float(),
        "valor_dolar": Float(),
        "categoria": String(50),
        "data_referencia": Date(),
        "preco_medio_m3": Float(),
        "tipo_fluxo": String(20),
    }

    try:
        # Envia o DataFrame para a tabela no banco de dados
        df.to_sql(
            name=nome_tabela,
            con=engine,
            if_exists="replace",  
            index=False,
            dtype=schema_tipos,
            chunksize=1000  
        )
        print("Carga concluída com sucesso!")
        print(f"   Tabela '{nome_tabela}' criada com {len(df)} registros.\n")

    except Exception as e:
        print(f"Erro ao carregar dados no banco de dados: {e}")
        raise


if __name__ == "__main__":
    caminho_parquet = PASTA_RAIZ / "dados" / "processados" / "comercio_exterior_combustiveis.parquet"
    
    if caminho_parquet.exists():
        df_processado = pd.read_parquet(caminho_parquet)
        carregar_dados_banco(df_processado)
    else:
        print("Arquivo Parquet não encontrado")