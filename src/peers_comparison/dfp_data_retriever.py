import numpy as np

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

    def pivot_and_clean(self):
        cvm_df = self.dfp_original_data.copy()

        cvm_df = cvm_df[(cvm_df["VL_CONTA"] < 0) | (cvm_df["VL_CONTA"] > 1)]

        cvm_df = cvm_df[(cvm_df["GRUPO_DFP"].isin(config.GROUPS)) & (cvm_df["CD_CONTA"].isin(config.ACCOUNTS))][
            config.DFP_COLUMNS
        ]

        cvm_df["remove"] = np.where(
            cvm_df["CD_CONTA"].isin(config.INCOMPATIBLE_ACCOUNTS["accounts"]),
            np.where(cvm_df["DS_CONTA"].str.lower().str.contains(config.INCOMPATIBLE_ACCOUNTS["ds_account"]), 0, 1),
            0,
        )

        cvm_df = (
            cvm_df[cvm_df["remove"] == 0][["DT_FIM_EXERC", "DENOM_CIA", "VL_CONTA", "CD_CONTA"]]
            .replace({"CD_CONTA": config.CD_CONTA_MAP_DICT})
            .replace({"DENOM_CIA": config.UPDATE_COMPANY_NAME})
        )

        self.df_pivot = (
            cvm_df.pivot(index=["DT_FIM_EXERC", "DENOM_CIA"], columns="CD_CONTA", values="VL_CONTA")
            .reset_index()
            .fillna(0)
        )
