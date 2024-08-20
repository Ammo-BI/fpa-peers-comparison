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

    def get_dfp_data(self, dfp_needed_df):
        dfp_retriever = DFPDataRetriever()
        dfp_retriever.type_format = "ind"

        original_dfp_df = pd.DataFrame()

        for i, row in dfp_needed_df.iterrows():
            year = int(row["YEAR"])
            dfp_retriever.get_dfp_data(
                companies_cvm_codes=row["CD_CVM"], type_docs=["DRE"], first_year=year, last_year=year
            )
            original_dfp_df = pd.concat([original_dfp_df, dfp_retriever.dfp_original_data])

        self.dfp_original_data = original_dfp_df

    def create_report(self):
        original_itr_df = self.itr_original_data.copy()
        original_itr_df = original_itr_df[original_itr_df["source_file"].str.lower().str.contains("dre_ind")]

        complete_itr_df = self.add_aux_columns(original_itr_df)
        itr_df_tri = complete_itr_df[complete_itr_df["SALDO_DF"] == "Trimestre"].copy()
        itr_df_tri.loc[:, "VL_CONTA_AUX"] = 0

        dfp_needed_df = self.identify_dfp_need(itr_df_tri)

        self.get_dfp_data(dfp_needed_df)

        dfp_df = self.add_aux_columns(self.dfp_original_data)
        dfp_df = dfp_df[dfp_df["SALDO_DF"] == "Trimestre"].copy()

        itr_df_acu = (
            complete_itr_df[(complete_itr_df["SALDO_DF"] == "Acumulado") & (complete_itr_df["QUARTER"] == "Q3")]
            .rename(columns={"VL_CONTA": "VL_CONTA_AUX"})
            .copy()
        )

        q4_df = dfp_df.merge(
            itr_df_acu[["YEAR", "CD_CVM", "CD_CONTA", "VL_CONTA_AUX"]], on=["YEAR", "CD_CVM", "CD_CONTA"]
        )

        dfp_itr_df = pd.concat([itr_df_tri, q4_df]).reset_index(drop=True)
        dfp_itr_df["VL_CONTA"] = dfp_itr_df[["ESCALA_MOEDA", "VL_CONTA", "VL_CONTA_AUX", "QUARTER"]].apply(
            lambda x: self.update_vl_conta(x), axis=1
        )

        dfp_itr_df.drop(["EXERC_PERIOD_DAYS", "SALDO_DF", "VL_CONTA_AUX"], axis=1, inplace=True)

        dfp_itr_df = dfp_itr_df[dfp_itr_df["CD_CONTA"].isin(config.ACCOUNTS)][config.ITR_COLUMNS]

        dfp_itr_df["remove"] = np.where(
            dfp_itr_df["CD_CONTA"].isin(config.INCOMPATIBLE_ACCOUNTS["accounts"]),
            np.where(dfp_itr_df["DS_CONTA"].str.lower().str.contains(config.INCOMPATIBLE_ACCOUNTS["ds_account"]), 0, 1),
            0,
        )

        dfp_itr_df = dfp_itr_df[dfp_itr_df["remove"] == 0][
            ["YEAR", "QUARTER", "CD_CVM", "CNPJ_CIA", "DENOM_CIA", "CD_CONTA", "CD_CONTA", "VL_CONTA"]
        ]
        dfp_itr_df.columns = [
            "YEAR",
            "QUARTER",
            "CD_CVM",
            "CNPJ_CIA",
            "DENOM_CIA",
            "CD_CONTA",
            "DESC_CONTA",
            "VL_CONTA",
        ]

        self.itr_report = dfp_itr_df.replace({"DESC_CONTA": config.CD_CONTA_MAP_DICT}).replace(
            {"DENOM_CIA": config.UPDATE_COMPANY_NAME}
        )

    def pivor_report(self):
        self.df_pivot = (
            self.itr_report.pivot(index=["YEAR", "QUARTER", "DENOM_CIA"], columns="CD_CONTA", values="VL_CONTA")
            .reset_index()
            .fillna(0)
        )

    def update_vl_conta(self, row):
        unit_value = 1000 if row["ESCALA_MOEDA"] == "MIL" else 1
        vl_conta_aux = row["VL_CONTA"] - row["VL_CONTA_AUX"] if row["QUARTER"] == "Q4" else row["VL_CONTA"]

        return unit_value * vl_conta_aux

    def add_aux_columns(self, original_df):
        df = original_df.copy()

        df["DT_FIM_EXERC"] = pd.to_datetime(df["DT_FIM_EXERC"])
        df["DT_INI_EXERC"] = pd.to_datetime(df["DT_INI_EXERC"])
        df["QUARTER"] = df["DT_FIM_EXERC"].apply(lambda x: f"Q{x.quarter}")

        df["YEAR"] = df["DT_REFER"].apply(lambda x: x[:4])
        df["EXERC_PERIOD_DAYS"] = (df["DT_FIM_EXERC"] - df["DT_INI_EXERC"]).dt.days
        df["SALDO_DF"] = df[["EXERC_PERIOD_DAYS", "source_file"]].apply(lambda x: self.get_saldo_type(x), axis=1)

        df = df[df["GRUPO_DFP"].str.contains("Individual")]

        return df

    def get_saldo_type(self, row):

        if row["EXERC_PERIOD_DAYS"] in range(80, 100):
            return "Trimestre"
        elif "dfp" in row["source_file"] and row["EXERC_PERIOD_DAYS"] > 300:
            return "Trimestre"
        else:
            return "Acumulado"

    def identify_dfp_need(self, df):
        df_pivot = df[["YEAR", "QUARTER", "CD_CVM", "DENOM_CIA", "CD_CONTA"]].value_counts().reset_index().copy()

        df_pivot = (
            df_pivot.pivot(index=["YEAR", "CD_CVM", "DENOM_CIA", "CD_CONTA"], columns="QUARTER", values="count")
            .reset_index()
            .copy()
        )

        if "Q4" in df_pivot.columns:
            df_pivot = df_pivot[df_pivot["Q4"].isna()][["YEAR", "CD_CVM"]].drop_duplicates()
        else:
            df_pivot = df_pivot[["YEAR", "CD_CVM"]].drop_duplicates()

        return df_pivot.groupby("YEAR")["CD_CVM"].apply(list).reset_index()
