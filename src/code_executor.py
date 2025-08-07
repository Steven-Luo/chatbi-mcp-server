"""
 Created by Steven Luo on 2025/8/6
"""

import traceback
from typing import Optional

import pandas as pd

import config
import utils
from code_error_corrector import CodeErrorCorrector
from data_accessors.base_data_accessor import BaseDataAccessor
from llms.base_llm import BaseLLM
from schema.execution_error_history import ExecutionErrorHistoryItem


class CodeExecutor:
    def __init__(self, data_accessor: BaseDataAccessor, llm: Optional[BaseLLM] = None):
        self.llm = llm
        self.data_accessor = data_accessor
        self.logger = utils.get_logger(self.__class__.__name__)

    def execute(self, question, code) -> pd.DataFrame:
        """
        执行代码

        根据过往执行结果，共有如下几种形式：
        - {'type': 'dataframe', 'value': result_df}
        - {'type': 'number', 'value': result_num}
        - {'type': 'string', 'value': result_str}
        - pd.DataFrame({'Actual': y_test, 'Predicted': predictions})
        - result_df
        """
        max_retry_count = config.get_config()['max_retry_execution_count']
        self.logger.info(f"max_retry_execution_count: {max_retry_count}")

        code_err_corrector = CodeErrorCorrector(self.llm)
        error_history_list = []
        ans_df = pd.DataFrame([])

        while len(error_history_list) <= max_retry_count:
            try:
                ans_df = self.data_accessor.execute(code)
                break
            except Exception as e:
                self.logger.warning(f"retry_count: {len(error_history_list)}\ncode: {code}\nexception:\n: {traceback.format_exc()}")

                if len(error_history_list) + 1 > max_retry_count:
                    break

                error_history_list.append(ExecutionErrorHistoryItem(code=code, e=e))
                rewritten_code = code_err_corrector.correct(self.data_accessor, question, error_history_list)
                self.logger.error(f"rewritten_code:\n {rewritten_code}")
                code = rewritten_code
        return ans_df
