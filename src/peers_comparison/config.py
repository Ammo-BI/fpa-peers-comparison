DFP_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/"
ITR_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/"

TMP_FILES_PATH = "tmp_files/"

FULL_COLUMNS = [
    "CNPJ_CIA",
    "CD_CVM",
    "DT_REFER",
    "DT_INI_EXERC",
    "DT_FIM_EXERC",
    "DENOM_CIA",
    "VERSAO",
    "GRUPO_DFP",
    "MOEDA",
    "ESCALA_MOEDA",
    "ORDEM_EXERC",
    "CD_CONTA",
    "DS_CONTA",
    "VL_CONTA",
    "COLUNA_DF",
]

AVAILABLE_DOCS = ["BPA", "BPP", "DFC_MD", "DFC_MI", "DMPL", "DRE", "DVA"]

AVAILABLE_FORMATS = ["ind", "con"]

DEFAULT_ORDEM_EXERC = "ÚLTIMO"

GROUPS = [
    "DF Consolidado - Balanço Patrimonial Passivo",
    "DF Consolidado - Balanço Patrimonial Ativo",
    "DF Consolidado - Demonstração do Fluxo de Caixa (Método Indireto)",
    "DF Consolidado - Demonstração do Resultado",
    "DF Consolidado - Demonstração das Mutações do Patrimônio Líquido",
]

ACCOUNTS = [
    "3.03",
    "3.04",
    "3.04.01",
    "3.04.02",
    "3.04.03",
    "3.04.04",
    "3.04.05",
    "6.01.01.04",
    "6.01.01.02",
    "3.05",
    "3.01",
    "3.02",
]

DFP_COLUMNS = ["DT_FIM_EXERC", "DENOM_CIA", "VL_CONTA", "CD_CONTA", "DS_CONTA", "CD_CVM", "CNPJ_CIA"]

ITR_COLUMNS = ["YEAR", "QUARTER", "DT_FIM_EXERC", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA", "CD_CVM", "CNPJ_CIA"]

INCOMPATIBLE_ACCOUNTS = {"accounts": ["6.01.01.04", "6.01.01.02"], "ds_account": "depreciação|depreciações"}

CD_CONTA_MAP_DICT = {
    "6.01.01.04": "Depreciações e Amortizações_2",
    "6.01.01.02": "Depreciações e Amortizações_1",
    "3.03": "Resultado Bruto",
    "3.04.01": "Despesas de Vendas",
    "3.04.02": "Despesas Gerais e Administrativas",
    "3.04.03": "Perdas por não recuperabilidade de Ativos",
    "3.04.04": "Outras Receitas Operacionais",
    "3.04.05": "Outras Receitas Operacionais",
    "3.05": "EBIT",
    "3.01": "Receita de Venda de Bens/Serviços",
    "3.02": "Custo de Bens/Serviços",
    "3.04": "Despesas/Receitas Operacionais (totais)",
}

UPDATE_COMPANY_NAME = {"RESTOQUE COMÉRCIO E CONFECÇÕES DE ROUPAS S.A.": "VESTE S.A. ESTILO"}


# # If modifying these scopes, delete the file token.json.
# SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# # The ID and range of a sample spreadsheet.
# SAMPLE_SPREADSHEET_ID = "1djT2FhY4ND2TN4iTOvv2Dkx48LKSWi-NM8eu9m6nxfA"
# SAMPLE_RANGE_NAME = "Sheet1!A1:N5"


# URL_teste = ["https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/", "/DADOS/"]
