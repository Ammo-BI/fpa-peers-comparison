import numpy as np
import pandas as pd

import peers_comparison.config as config
from peers_comparison.cvm_data_retriever import CVMDataRetriever
from peers_comparison.dfp_data_retriever import DFPDataRetriever


class ITRDataRetriever(CVMDataRetriever):
    def __init__(self):
        CVMDataRetriever.__init__(self)
        self.url = config.ITR_URL

    def get_itr_data(self, companies_cvm_codes, type_docs, first_year, last_year):

        self.itr_original_data = self.get_data(
            companies_cvm_codes=companies_cvm_codes, first_year=first_year, last_year=last_year, type_docs=type_docs
        )

        dfp_retriever = DFPDataRetriever()
        dfp_retriever.type_format = "ind"
        dfp_retriever.get_dfp_data(
            companies_cvm_codes=companies_cvm_codes, type_docs=["DRE"], first_year=first_year, last_year=last_year
        )

        self.dfp_original_data = dfp_retriever.dfp_original_data

    def pivot_and_clean(self):
        itr_df = self.itr_original_data.copy()
        dfp_df = self.dfp_original_data.copy()

        dfp_itr_df = pd.concat([itr_df[itr_df["source_file"].str.lower().str.contains("dre_ind")], dfp_df]).reset_index(
            drop=True
        )
        dfp_itr_df["DT_FIM_EXERC"] = pd.to_datetime(dfp_itr_df["DT_FIM_EXERC"])
        dfp_itr_df["DT_INI_EXERC"] = pd.to_datetime(dfp_itr_df["DT_INI_EXERC"])
        dfp_itr_df["QUARTER"] = dfp_itr_df["DT_FIM_EXERC"].apply(lambda x: f"Q{x.quarter}")

        dfp_itr_df["YEAR"] = dfp_itr_df["DT_REFER"].apply(lambda x: x[:4])
        dfp_itr_df["EXERC_PERIOD_DAYS"] = (dfp_itr_df["DT_FIM_EXERC"] - dfp_itr_df["DT_INI_EXERC"]).dt.days
        dfp_itr_df["SALDO_DF"] = dfp_itr_df["EXERC_PERIOD_DAYS"].apply(
            lambda x: "Acumulado" if x in range(100, 300) else "Trimestre"
        )

        dfp_itr_df = dfp_itr_df[dfp_itr_df["GRUPO_DFP"].str.contains("Individual")]

        dfp_itr_df_tri = dfp_itr_df[dfp_itr_df["SALDO_DF"] == "Trimestre"].copy()
        dfp_itr_df_acu = (
            dfp_itr_df[dfp_itr_df["SALDO_DF"] == "Acumulado"].rename(columns={"VL_CONTA": "VL_CONTA_AUX"}).copy()
        )

        dfp_itr_df_tri = dfp_itr_df_tri.sort_values(by=["CNPJ_CIA", "CD_CONTA", "QUARTER"]).reset_index(drop=True)
        dfp_itr_df_tri = dfp_itr_df_tri.merge(
            dfp_itr_df_acu[dfp_itr_df_acu["QUARTER"] == "Q3"][["YEAR", "CD_CVM", "CD_CONTA", "VL_CONTA_AUX"]],
            how="left",
            on=["YEAR", "CD_CVM", "CD_CONTA"],
        )

        dfp_itr_df_tri["VL_CONTA"] = dfp_itr_df_tri[["ESCALA_MOEDA", "VL_CONTA", "VL_CONTA_AUX", "QUARTER"]].apply(
            lambda x: self.update_vl_conta(x), axis=1
        )

        dfp_itr_df_tri.drop(["EXERC_PERIOD_DAYS", "SALDO_DF", "VL_CONTA_AUX"], axis=1, inplace=True)

        dfp_itr_df_tri = dfp_itr_df_tri[dfp_itr_df_tri["CD_CONTA"].isin(config.ACCOUNTS)][config.ITR_COLUMNS]

        dfp_itr_df_tri["remove"] = np.where(
            dfp_itr_df_tri["CD_CONTA"].isin(config.INCOMPATIBLE_ACCOUNTS["accounts"]),
            np.where(
                dfp_itr_df_tri["DS_CONTA"].str.lower().str.contains(config.INCOMPATIBLE_ACCOUNTS["ds_account"]), 0, 1
            ),
            0,
        )

        dfp_itr_df_tri = (
            dfp_itr_df_tri[dfp_itr_df_tri["remove"] == 0][["YEAR", "QUARTER", "DENOM_CIA", "VL_CONTA", "CD_CONTA"]]
            .replace({"CD_CONTA": config.CD_CONTA_MAP_DICT})
            .replace({"DENOM_CIA": config.UPDATE_COMPANY_NAME})
        )

        self.df_pivot = (
            dfp_itr_df_tri.pivot(index=["YEAR", "QUARTER", "DENOM_CIA"], columns="CD_CONTA", values="VL_CONTA")
            .reset_index()
            .fillna(0)
        )

    def update_vl_conta(self, row):
        unit_value = 1000 if row["ESCALA_MOEDA"] == "MIL" else 1
        vl_conta_aux = row["VL_CONTA"] - row["VL_CONTA_AUX"] if row["QUARTER"] == "Q4" else row["VL_CONTA"]

        return unit_value * vl_conta_aux
