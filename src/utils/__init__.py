"""
 Created by Steven Luo on 2025/8/6
"""


import datetime
import logging
import re

import numpy as np
import pandas as pd

import config

log_level = config.get_log_level()


def get_logger(name):
    logger = logging.getLogger(name)
    logging.basicConfig(level=log_level, format="[%(asctime)s] [%(name)s] [%(filename)s(%(lineno)d)] [%(levelname)s] %(message)s")
    return logger


logger = get_logger(__name__)


def process_df_value(val, truncate_len=30):
    """
    处理DataFrame的值，主要进行空缺值、日期、长度截断处理
    :param val:
    :param truncate_len:
    :return:
    """
    if pd.isna(val):
        val = None
    elif isinstance(val, pd.Timestamp):
        val = val.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(val, datetime.date):
        val = val.strftime('%Y-%m-%d')
    elif isinstance(val, datetime.timedelta):
        val = (pd.Timestamp('1970-01-01') + val).time().strftime('%H:%M:%S')
    elif isinstance(val, str):
        if truncate_len is not None:
            return val[:truncate_len] + ('...' if len(val) > truncate_len else '')
        else:
            return val
    elif isinstance(val, list):
        return [process_df_value(item, truncate_len) for item in val]
    return val


def extract_code(text: str, lang='sql'):
    if text.startswith(f'```{lang}'):
        pattern = fr"```{lang}\n(.*?)\n```"
    elif text.startswith(f'{lang}'):
        pattern = fr"<{lang}>\n(.*?)\n</{lang}>"
    elif text.startswith(f'<{lang}>'):
        pattern = fr"<{lang}>\n(.*?)\n</{lang}>"
    else:
        return text

    match = re.search(pattern, text, re.DOTALL)
    if match:
        code = match.group(1)
    else:
        logger.error(f"code: {text}, No code found")
        code = text
    return code


def convert_series_to_dataframe(data_series: pd.Series):
    index_name = data_series.index.name
    logger.info(f"index_name: {index_name}")
    list_name = data_series.name
    logger.info(f"list_name: {list_name}")

    has_real_index = False
    index_list = data_series.index.values

    for idx, index in enumerate(index_list):
        # if not index == idx:
        if not isinstance(index, (int, np.int64)):
            has_real_index = True
            break

    if index_name:
        try:
            data_frame = data_series.reset_index(name="值")
            data_frame.columns = [index_name, "值"]
            return data_frame
        except Exception as e:
            return data_series.to_frame()
    elif has_real_index:
        return data_series.reset_index(name="值")
    else:
        return data_series.to_frame()
