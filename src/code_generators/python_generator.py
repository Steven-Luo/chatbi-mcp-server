"""
 Created by Steven Luo on 2025/8/6
"""
import os
from datetime import datetime

import config
import utils
from data_accessors.dataframe_accessor import DataFrameAccessor
from llms.base_llm import BaseLLM
from schema.data_summary import DataSummary

class PythonGenerator:
    def __init__(self, data_accessor: DataFrameAccessor, llm: BaseLLM):
        self.llm = llm
        self.data_accessor = data_accessor
        self.df = data_accessor.dataframe
        self.logger = utils.get_logger(self.__class__.__name__)

    def _load_prompt_tmpl(self):
        version = "v1"
        with open(os.path.join(config.proj_root, 'data', 'prompts', 'code_gen', 'python', f"{version}.md"), encoding='utf-8') as f:
            prompt_tmpl = f.read()
        return prompt_tmpl

    def _build_prompt(self, question: str, data_summary: DataSummary):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        prompt = self._load_prompt_tmpl().replace(
            '{{question}}', question
        ).replace(
            '{{current_time}}', current_time
        ).replace(
            '{{data_info}}', data_summary.description
        )

        return prompt

    def generate_code(self, question: str):
        data_summary = self.data_accessor.get_data_summary()
        df = self.df

        prompt = self._build_prompt(question, data_summary)

        self.logger.info('propmt:\n')
        self.logger.info(prompt)

        resp = self.llm.chat_with_retry(prompt)
        self.logger.info(f'generated code raw_resp:\n{resp}')
        code = utils.extract_code(resp, lang='python')
        self.logger.info(f'generated code:\n{code}')
        return code
