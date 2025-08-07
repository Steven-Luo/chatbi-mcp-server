"""
 Created by Steven Luo on 2025/8/6
"""
from typing import Optional

import pandas as pd
from pandas import DataFrame

from data_accessors.dataframe_accessor import DataFrameAccessor


class CSVAccessor(DataFrameAccessor):
    def __init__(self, filepath: str, df: Optional[pd.DataFrame] = None, column_description: Optional[dict] = None):
        super().__init__(df, column_description)

        self.filepath = filepath
        self._df = df if df is not None else self.load_data(filepath)
        self._data_summary = self.detect_data()

    @DataFrameAccessor.cached_data_loader
    def load_data(self, filepath, n_rows=None) -> DataFrame:
        df = pd.read_csv(filepath)
        return df
