"""
 Created by Steven Luo on 2025/8/6
"""
import threading
from abc import abstractmethod
from functools import wraps
from typing import Optional, Callable

import pandas as pd

import utils
from data_accessors.base_data_accessor import BaseDataAccessor
from schema.data_summary import DataSummary


class DataFrameAccessor(BaseDataAccessor):
    def __init__(self, df: pd.DataFrame, column_description: Optional[dict] = None):
        super().__init__()
        self._df = df
        self.column_description = column_description
        self._data_summary = None

    def get_data_summary(self):
        return self._data_summary

    def detect_data(self) -> DataSummary:
        ds_df = self._df
        self.logger.info(f"start detect data, record count: {len(ds_df)}")

        columns = ds_df.columns.tolist()
        data_preview = ds_df[:5].to_dict(orient='records')
        for row in data_preview:
            for k, v in row.items():
                row[k] = utils.process_df_value(row[k])

        dtypes = {col: str(ds_df[col].dtype) for col in ds_df}
        dtypes = {col: 'string' if dtype == 'object' else dtype for col, dtype in dtypes.items()}
        # 按频率统计
        column_values = {col: [utils.process_df_value(v) for v in ds_df[col].value_counts(dropna=False).index.tolist()[:25]] for col in ds_df.columns}

        # table_describe = 'test table describe'
        table_describe = ''
        # column_describes = {col: f'test value {v}' for col in range(len(ds_df.columns))}
        column_describes = self.column_description if self.column_description else {}
        data_summary = DataSummary(
            columns=columns,
            dtypes=dtypes,
            column_values=column_values,
            table_description=table_describe,
            column_descriptions=column_describes,
            column_min_values={col: str(ds_df[col].dropna().min()) for col in ds_df.columns if dtypes[col] != 'string'},
            column_max_values={col: str(ds_df[col].dropna().max()) for col in ds_df.columns if dtypes[col] != 'string'}
        )
        return data_summary

    def execute(self, code, func_name='analyze'):
        """
        执行代码
        :param code: 代码
        :param func_name: 代码中的入口函数，主要用于获取代码执行结果，与prompt中定义的让LLM完成的代码签名一致
        :return: 代码执行结果，pd.DataFrame类型
        """
        # 在namespace中执行，不指定的话，带import语句的代码，只在exec的局部作用域中，函数调用时，无法使用这些依赖
        namespace = {'pd': pd}
        # namespace['dfs'] = [self._df.copy()]
        exec(code, namespace, namespace)
        df = self._df
        res = namespace[func_name](df)
        # res = namespace[func_name]([df.copy()])

        if isinstance(res, pd.DataFrame):
            ret_df = res
        elif isinstance(res, pd.Series):
            ret_df = utils.convert_series_to_dataframe(res)
        elif isinstance(res, dict):
            if res['type'] == 'dataframe':
                ret_df = res['value']
            else:
                ret_df = pd.DataFrame({'结果': [res['value']]})
        else:
            ret_df = res
        return ret_df


    def get_type(self):
        return 'python'

    @property
    def dataframe(self):
        """
        对于文件类型的数据，通过此属性可以获取全部数据，数据库类型的子类无需实现
        :return:
        """
        return self._df

    @abstractmethod
    def load_data(self, filepath, **kwargs):
        pass

    @classmethod
    def cached_data_loader(cls, loader_func: Callable) -> Callable:
        cached = {}
        lock = threading.Lock()

        @wraps(loader_func)
        def wrapper(self, filepath, *args, **kwargs):
            cache_key = (filepath, self.__class__.__name__) + tuple(args) + tuple([f"{k}={v}" for k, v in kwargs.items()])
            # 检查缓存（第一次无锁检查）
            if cache_key in cached:
                self.logger.info(f'{cache_key} cache hit')
                return cached[cache_key]

            with lock:
                # 双重检查避免竞争条件
                if cache_key in cached:
                    self.logger.info(f'{cache_key} cache hit in lock')
                    return cached[cache_key]

                self.logger.info(f'{cache_key} cache miss')
                df = loader_func(self, filepath, *args, **kwargs)
                cached[cache_key] = df
                return df.copy()

        return wrapper
