"""
 Created by Steven Luo on 2025/8/6
"""
from abc import ABC, abstractmethod
from datetime import datetime
from textwrap import dedent

import utils


class BaseDataAccessor(ABC):
    def __init__(self):
        self.logger = utils.get_logger(self.__class__.__name__)

    @abstractmethod
    def load_data(self, n_rows=None):
        pass

    @abstractmethod
    def detect_data(self):
        pass

    @abstractmethod
    def execute(self, code, *args, **kwargs):
        pass

    @abstractmethod
    def get_type(self):
        pass

    @abstractmethod
    def get_data_summary(self):
        pass

    @property
    def dataframe(self):
        """
        对于文件类型的数据，通过此属性可以获取全部数据，数据库类型的子类无需实现
        :return:
        """
        raise NotImplementedError()

    @property
    def description(self):
        data_summary = self.get_data_summary()
        data_descriptions = []
        for col in data_summary.columns:
            values = data_summary.column_values[col][:15]
            # 非字符串类型的，只预览5个值
            value_range_info = ''

            columns_description = data_summary.column_descriptions.get(col, '')
            if columns_description != '':
                columns_description = f"列名含义：{columns_description}\n"

            if data_summary.dtypes[col] != 'string' and col in data_summary.column_min_values:
                values = values[:3]
                value_range_info = f"最小取值：{data_summary.column_min_values[col]}\n最大取值：{data_summary.column_max_values[col]}"

            data_info = dedent(f"""
                ------
                列名：{col}
                典型取值：{values}
                字段类型：{data_summary.dtypes[col]}
                """) + columns_description + value_range_info
            data_descriptions.append(data_info)

        table_description = data_summary.table_description
        if table_description is not None and table_description.strip() != '':
            table_description = f"表格描述：{table_description}\n"

        final_data_info = table_description + '\n'.join(data_descriptions).strip()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return final_data_info
