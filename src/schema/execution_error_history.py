"""
 Created by Steven Luo on 2025/8/6
"""

from dataclasses import dataclass


@dataclass
class ExecutionErrorHistoryItem:
    code: str
    e: Exception
