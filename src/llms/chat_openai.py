"""
 Created by Steven Luo on 2025/8/6
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from llms.base_llm import BaseLLM


class ChatOpenAI(BaseLLM):
    def __init__(self, model_name=None, remove_think=False, extra_body=None, **kwargs):
        super().__init__(model_name=model_name, extra_body=extra_body)

        load_dotenv()

        self.client = OpenAI(
            base_url=os.environ.get('OPENAI_BASE_URL'),
            api_key=os.environ['OPENAI_API_KEY']
        )
        self.model_name = model_name or os.environ['OPENAI_MODEL_NAME']
        self.remove_think = remove_think
        self.kwargs = kwargs

    def chat(self, prompt, **kwargs):
        self.kwargs.update(kwargs)
        kwargs = self.kwargs
        self.logger.info(f"chat kwargs: {kwargs}")

        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{'role': 'user', 'content': prompt}] if isinstance(prompt, str) else prompt,
            **kwargs
        )
        if self.remove_think:
            return resp.choices[0].message.content.split('</think>')[-1]
        return resp.choices[0].message.content

    def stream_chat(self, prompt, **kwargs):
        self.kwargs.update(kwargs)
        kwargs = self.kwargs
        self.logger.info(f"chat kwargs: {kwargs}")

        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{'role': 'user', 'content': prompt}] if isinstance(prompt, str) else prompt,
            stream=True,
            # 可选，配置以后会在流式输出的最后一行展示token使用信息
            stream_options={"include_usage": True},
            **kwargs
        )
        for chunk in resp:
            if len(chunk.choices) == 0 or chunk.choices[0].delta.content is None:
                continue
            yield chunk.choices[0].delta.content


if __name__ == '__main__':
    llm = ChatOpenAI()
    # print(llm.chat('你是谁', temperature=0.01))

    prompt = '2024年10月08日 14:28:39。\n你是一个专业的数据分析师，我现在有一个问题，对这个问题也获取到了答案，你现在需要根据这个问题和答案，组织一个答复语。\n请注意观察数据，特别是数据中的空缺值，对于有些问题空缺值会影响答案，针对空缺值的情况，**不要**特别说明。仅输出答复语即可，不要包含任何描述性内容、解释。\n但问题中涉及年份时，这只是问题中的时间，跟现实时间没有关系，这不是拼写错误，你无需额外关注，只需根据问题中的时间组织答案即可。\n问题是：2018年6月14号开工的琴台美术馆的建设地点和工程类别分别是什么？\n答案是：[{"建设地点": "汉阳区琴台大剧院以西，知音大道以南、月湖以北", "工程类别": "配套建设地下室、地上土建、安装、弱电、给排水、电气、消防、暖通及电梯安装、装修、幕墙、室外道路排水等"}]'
    for chunk in llm.stream_chat(prompt):
        print(chunk, end='')
