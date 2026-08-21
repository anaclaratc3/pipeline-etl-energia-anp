# Pipeline de Dados: Comercio Exterior de Combustiveis (ANP)

Projeto focado no desenvolvimento de um pipeline ETL end-to-end com Python e SQL, transformando dados brutos da ANP sobre importacoes e exportacoes em um modelo estrela otimizado para consultas analiticas e dashboards.

## Tecnologias
* Python - Extracao e tratamento
* SQL - Modelagem dimensional (Star Schema)
* Power BI & Looker Studio - Visualizacao de dados

## Etapas do Pipeline
1. Extracao: Leitura dos arquivos brutos da ANP (2000-2025)
2. Transformacao: Padronizacao de unidades (m3), limpeza e calculos
3. Carga: Estruturacao em tabela fato e dimensoes no banco SQL
4. Analytics: Paineis visuais para analise da balanca comercial e volumes

## Fonte dos Dados
Portal de Dados Abertos do Governo Federal (https://dados.gov.br/dados/conjuntos-dados/importacoes-e-exportacoes)