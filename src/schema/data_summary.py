"""
 Created by Steven Luo on 2025/8/6

 数据概要，主要用于保存数据探查结果，为代码生成提供上下文
"""

from dataclasses import dataclass
from textwrap import dedent


@dataclass
class DataSummary:
    # 数据列名
    columns: list
    # 数据类型
    dtypes: dict
    # 每个列的典型值
    column_values: dict
    # 每个列的描述
    column_descriptions: dict
    # 表的描述
    table_description: str
    # 每个列的最小值
    column_min_values: dict
    # 每个列的最大值
    column_max_values: dict

    @property
    def description(self):
        data_summary = self
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

        return final_data_info