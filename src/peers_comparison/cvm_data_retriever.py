import io
import os
import zipfile
from datetime import datetime
from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup

import peers_comparison.config as config


class CVMDataRetriever:
    def __init__(self, type_format=["con", "ind"], clean_data=True):
        self.type_format = type_format
        self.clean_data = clean_data
        self.url = None

    def get_content(self, year_filter: List):
        response = requests.get(url=self.url)

        html = BeautifulSoup(response.text, "html.parser")

        self.files_list = [x.get("href") for x in html.find("pre").find_all("a") if x.get("href")[-8:] in year_filter]

    def get_year_filter(self, first_year: int, last_year: int) -> List:
        if first_year and last_year:
            year_range = [x for x in range(first_year, last_year + 1)]
        elif first_year:
            last_year_tmp = datetime.now().year
            year_range = [x for x in range(first_year, last_year_tmp + 1)]
        else:
            first_year_tmp = 2010
            year_range = [x for x in range(first_year_tmp, last_year + 1)]

        return [f"{year}.zip" for year in year_range]

    def get_data(self, companies_cvm_codes: List, first_year: int, last_year: int, type_docs: List) -> pd.DataFrame:

        # valida se os type_docs estão de acordo com os existentes.
        # caso haja algum que não esteja na lista, gerar um erro

        year_filter = self.get_year_filter(first_year, last_year)

        self.get_content(year_filter=year_filter)

        self.data = self.download_read_zip_file(companies_cvm_codes=companies_cvm_codes, type_docs=type_docs)

        return self.data

    def download_read_zip_file(self, companies_cvm_codes: List, type_docs: List) -> pd.DataFrame:
        full_links = [f"{self.url}{file_}" for file_ in self.files_list]

        complete_df = pd.DataFrame()

        for link in full_links:
            tmp_file = requests.get(link, stream=True)
            unzipped = zipfile.ZipFile(io.BytesIO(tmp_file.content))

            filtered_files = [file_ for file_ in unzipped.namelist() for file_type in type_docs if file_type in file_]

            for selected_file in filtered_files:
                unzipped.extract(selected_file, path=config.TMP_FILES_PATH)

                file_df = self.read_file(filename=selected_file)

                if companies_cvm_codes:
                    file_df = file_df[file_df["CD_CVM"].isin(companies_cvm_codes)]

                complete_df = pd.concat([complete_df, file_df])

                self.delete_file(filename=selected_file)

        os.rmdir(config.TMP_FILES_PATH)

        return complete_df

    def read_file(self, filename: str) -> pd.DataFrame:
        df = pd.read_csv(f"{config.TMP_FILES_PATH}{filename}", sep=";", decimal=",", encoding="Latin1")
        df["VL_CONTA"] = df["VL_CONTA"].astype("float64")

        if self.clean_data:
            df = self.clean_file_dataframe(file_dataframe=df, filename=filename)

        return df

    def clean_file_dataframe(self, file_dataframe: pd.DataFrame, filename: str) -> pd.DataFrame:
        tmp_df = (
            file_dataframe[file_dataframe["ORDEM_EXERC"] == config.DEFAULT_ORDEM_EXERC].reset_index(drop=True).copy()
        )

        missing_columns = [x for x in config.FULL_COLUMNS if x not in file_dataframe.columns]

        if len(missing_columns) > 0:
            for col in missing_columns:
                tmp_df.loc[:, col] = None

        tmp_df = tmp_df[config.FULL_COLUMNS]

        tmp_df["DT_INI_EXERC"] = tmp_df[["DT_FIM_EXERC", "DT_INI_EXERC"]].apply(
            lambda x: x["DT_INI_EXERC"] if pd.notnull(x["DT_INI_EXERC"]) else x["DT_FIM_EXERC"][:5] + "01-01", axis=1
        )

        tmp_df["source_file"] = filename

        return tmp_df

    def delete_file(self, filename: str) -> None:
        os.remove(f"{config.TMP_FILES_PATH}{filename}")
