"""
 Created by Steven Luo on 2025/8/6
"""

import os
from textwrap import dedent
from typing import List

import config
import utils
from data_accessors.base_data_accessor import BaseDataAccessor
from llms.base_llm import BaseLLM
from schema.execution_error_history import ExecutionErrorHistoryItem

logger = utils.get_logger(__name__)


class CodeErrorCorrector:
    def __init__(self, llm: BaseLLM):
        self._llm = llm

    def _load_err_correction_propmt_tmpl(self, data_accessor: BaseDataAccessor):
        """
        加载代码纠错Prompt
        :param data_accessor:
        :return:
        """
        if data_accessor.get_type() == 'mysql':
            version = 'v1'
            return open(os.path.join(config.proj_root, 'data', 'prompts', 'code_error_correction', 'mysql', f"{version}.md"), encoding='utf-8').read()
        else:
            version = 'v1'
            return open(os.path.join(config.proj_root, 'data', 'prompts', 'code_error_correction', 'python', f"{version}.md"), encoding='utf-8').read()

    def _build_error_history_prompt(self, hist_item: ExecutionErrorHistoryItem, lang: str):
        error_info = str(hist_item.e)

        return f"""\n\n以下代码执行时报错：
```{lang}
{hist_item.code}
```

报错信息如下：
```
{error_info}
```
"""

    def correct(self, data_accessor: BaseDataAccessor, query: str, error_history: List[ExecutionErrorHistoryItem]):
        data_summary = data_accessor.get_data_summary()
        prompt_tmpl = self._load_err_correction_propmt_tmpl(data_accessor)

        if data_accessor.get_type() == 'mysql':
            lang = 'sql'
        elif data_accessor.get_type() == 'python':
            lang = 'python'
        else:
            raise ValueError(f"暂时不支持{data_accessor.get_type()}类型的数据")

        error_history_part = ''
        for hist in error_history:
            error_history_part += self._build_error_history_prompt(hist, lang)

        prompt = prompt_tmpl.replace(
            '{{data_info}}', data_summary.description
        ).replace(
            '{{question}}', query
        ).replace(
            '{{error_history}}', error_history_part
        )
        logger.info(f"prompt: {prompt}")

        raw_rewritten_code = self._llm.chat_with_retry(prompt)
        rewritten_code = utils.extract_code(raw_rewritten_code, lang)

        return rewritten_code
