"""
 Created by Steven Luo on 2025/8/6
"""
import time
from abc import ABC, abstractmethod

import utils


class BaseLLM(ABC):
    def __init__(self, model_name=None, extra_body=None, **kwargs):
        """
        基础的LLM类，所有的LLM类都需要继承自这个类
        :param model_name: 模型名称
        :param extra_body: 额外的请求参数，像GLM 4.5的thinking参数，赋值到这个变量
        :param kwargs: 其他参数
        """
        self.logger = utils.get_logger(self.__class__.__name__)
        self.model_name = model_name
        self.extra_body = extra_body

    @abstractmethod
    def chat(self, prompt, **kwargs):
        pass

    def chat_with_retry(self, prompt, max_retry=3, error_sleeping_seconds=8, **kwargs):
        """
        增加一个带重试的方法，使上层调用更稳定
        :param prompt:
        :param max_retry:
        :param error_sleeping_seconds:
        :param kwargs:
        :return:
        """
        while max_retry > 0:
            try:
                return self.chat(prompt, **kwargs)
            except Exception as e:
                self.logger.error(f"prompt {prompt[:20]}, chat error: {e}, retry left: {max_retry}, sleeping {error_sleeping_seconds} seconds")
                time.sleep(error_sleeping_seconds)
                max_retry -= 1
        raise ValueError(f'chat failed after {max_retry} retries')

    def stream_chat(self, prompt, **kwargs):
        raise NotImplementedError
