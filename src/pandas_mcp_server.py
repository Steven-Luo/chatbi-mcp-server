"""
 Created by Steven Luo on 2025/8/6
"""
import traceback
from typing import List, Dict, Annotated

from fastmcp import FastMCP, Context
from fastmcp.tools.tool import ToolResult
from pydantic import Field

import config
import utils
from code_executor import CodeExecutor
from code_generators.python_generator import PythonGenerator
from data_accessors.csv_accessor import CSVAccessor
from data_accessors.excel_accessor import ExcelAccessor
from llms.chat_openai import ChatOpenAI

mcp = FastMCP('data-analyzer', port=8000)

ACCESS_TOKEN = config.get_config()['mcp_server_token']

logger = utils.get_logger(__name__)

llm = ChatOpenAI()


def get_bearer_token(ctx):
    request = ctx.get_http_request()
    headers = request.headers
    # Check if 'Authorization' header is present
    authorization_header = headers.get('Authorization')

    if authorization_header:
        # Split the header into 'Bearer <token>'
        parts = authorization_header.split()

        if len(parts) == 2 and parts[0] == 'Bearer' and parts[1] == ACCESS_TOKEN:
            return parts[1]
        else:
            raise ValueError("Invalid Authorization header format")
    else:
        raise ValueError("Authorization header missing")


def get_data_accessor(path_or_url: str):
    if path_or_url.lower().startswith('http'):
        try:
            data_accessor = CSVAccessor(path_or_url)
        except Exception as e:
            logger.info(e)
            data_accessor = ExcelAccessor(path_or_url)
    elif path_or_url.lower().endswith('csv'):
        data_accessor = CSVAccessor(path_or_url)
    elif path_or_url.lower().endswith('xlsx'):
        data_accessor = ExcelAccessor(path_or_url)
    else:
        raise TypeError("文件类型不支持")
    return data_accessor


@mcp.tool(name='get_preview_data', description='数据描述信息')
def get_preview_data(
        path_or_url: Annotated[str, Field(description="数据文件路径或URL，仅支持Excel和CSV")],
        context: Context
) -> str:
    """
    以AI易读的格式获取数据信息

    Args:
        path_or_url: 数据文件路径或URL，仅支持Excel和CSV

    Returns:
        以Markdown形式组织的预览结果
    """
    logger.info(f'filepath: {path_or_url}')
    token = get_bearer_token(context)
    logger.info(f"Client token: {token}")
    data_accessor = get_data_accessor(path_or_url)
    return "当前数据信息如下：\n" + data_accessor.description


@mcp.tool(
    name='analyze_data',
    description='对数据进行分析，结果以字典数组形式组织'
)
def analyze_data(
        question: Annotated[str, Field(description="用户问题")],
        path_or_url: Annotated[str, Field(description="数据文件所在路径或者URL，仅支持Excel和CSV")],
        context: Context
) -> Annotated[ToolResult, Field(description="数据分析结果，JSON对象组成的数组")]:
    """
    根据用户问题分析数据

    Args:
        question (str): 用户问题
        path_or_url (str): 数据文件路径，仅支持Excel和CSV

    Returns:
        List[Dict]: 数据分析结果表格，是以字典数组的形式组织的
    """
    token = get_bearer_token(context)
    logger.info(f"Client token: {token}")

    logger.info(f'question: {question}')
    logger.info(f'path_or_url: {path_or_url}')

    path_or_url = path_or_url.strip()
    question = question.strip()

    data_accessor = get_data_accessor(path_or_url)
    code_generator = PythonGenerator(data_accessor, llm)
    code_executor = CodeExecutor(data_accessor, llm)

    try:
        code = code_generator.generate_code(question)
        ans_df = code_executor.execute(question, code)
    except Exception as e:
        logger.info(traceback.format_exc())
        raise

    if len(ans_df) > 500:
        logger.info(f'ans_df.shape: {ans_df.shape}, truncate to 500 rows')
        ans_df = ans_df.head(500)

    # structured_content要求是dict类型的
    resp = ans_df.to_dict(orient='list')
    logger.info(f'{question} -> {resp}')

    # 以两种形式返回，方便不同的客户端使用
    return ToolResult(
        content=ans_df.to_markdown(),
        structured_content=resp
    )


if __name__ == '__main__':
    # # http://localhost:8000/sse
    # mcp.run(transport='sse')

    # http://localhost:8000/mcp
    mcp.run(transport='streamable-http')

    # mcp.run(transport='stdio')
