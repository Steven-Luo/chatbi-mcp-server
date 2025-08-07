"""
 Created by Steven Luo on 2025/8/6
"""
from typing import Optional

import pandas as pd
from pandas import DataFrame

from data_accessors.dataframe_accessor import DataFrameAccessor


class ExcelAccessor(DataFrameAccessor):
    def __init__(self, filepath: str, sheet_name: Optional[str]=None, df: Optional[DataFrame] = None, column_description: Optional[dict] = None):
        super().__init__(df, column_description)

        self.filepath = filepath
        self.sheet_name = sheet_name
        df = df if df is not None else self.load_data(filepath, sheet_name=sheet_name)
        self._df = df
        self._data_summary = self.detect_data()

    @DataFrameAccessor.cached_data_loader
    def load_data(self, filepath, sheet_name=None, n_rows=None) -> DataFrame:
        if sheet_name is not None:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
        else:
            df = pd.read_excel(self.filepath)
        self.logger.info(f"{filepath} sheet: {sheet_name}, load finished, shape: {df.shape}")
        return df
