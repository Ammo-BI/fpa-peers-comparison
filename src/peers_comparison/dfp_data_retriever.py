import numpy as np
import pandas as pd

import peers_comparison.config as config
from peers_comparison.cvm_data_retriever import CVMDataRetriever


class DFPDataRetriever(CVMDataRetriever):
    def __init__(self):
        CVMDataRetriever.__init__(self)
        self.url = config.DFP_URL

    def get_dfp_data(self, companies_cvm_codes, type_docs, first_year, last_year):

        self.dfp_original_data = self.get_data(
            companies_cvm_codes=companies_cvm_codes, first_year=first_year, last_year=last_year, type_docs=type_docs
        )

    def create_report(self):
        dfp_df = self.dfp_original_data.copy()

        dfp_df = dfp_df[(dfp_df["VL_CONTA"] < 0) | (dfp_df["VL_CONTA"] > 1)]

        dfp_df["VL_CONTA"] = dfp_df[["ESCALA_MOEDA", "VL_CONTA"]].apply(lambda x: self.update_vl_conta(x), axis=1)

        dfp_df = dfp_df[(dfp_df["GRUPO_DFP"].isin(config.GROUPS)) & (dfp_df["CD_CONTA"].isin(config.ACCOUNTS))][
            config.DFP_COLUMNS
        ]

        dfp_df["remove"] = np.where(
            dfp_df["CD_CONTA"].isin(config.INCOMPATIBLE_ACCOUNTS["accounts"]),
            np.where(dfp_df["DS_CONTA"].str.lower().str.contains(config.INCOMPATIBLE_ACCOUNTS["ds_account"]), 0, 1),
            0,
        )

        dfp_df = dfp_df[dfp_df["remove"] == 0][
            ["DT_FIM_EXERC", "CD_CVM", "CNPJ_CIA", "DENOM_CIA", "CD_CONTA", "CD_CONTA", "VL_CONTA"]
        ]
        dfp_df.columns = ["DT_FIM_EXERC", "CD_CVM", "CNPJ_CIA", "DENOM_CIA", "CD_CONTA", "DESC_CONTA", "VL_CONTA"]

        dfp_df["DT_FIM_EXERC"] = pd.to_datetime(dfp_df["DT_FIM_EXERC"])

        self.dfp_report = dfp_df.replace({"DESC_CONTA": config.CD_CONTA_MAP_DICT}).replace(
            {"DENOM_CIA": config.UPDATE_COMPANY_NAME}
        )

    def pivot_report(self):
        self.df_pivot = (
            self.dfp_report.pivot(index=["DT_FIM_EXERC", "DENOM_CIA"], columns="CD_CONTA", values="VL_CONTA")
            .reset_index()
            .fillna(0)
        )

    def update_vl_conta(self, row):
        unit_value = 1000 if row["ESCALA_MOEDA"] == "MIL" else 1

        return unit_value * row["VL_CONTA"]
