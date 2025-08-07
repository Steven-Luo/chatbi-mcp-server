"""
 Created by Steven Luo on 2025/8/6
"""

import yaml
import os

proj_root = os.path.dirname(os.path.dirname(__file__))

def parse_config():
    config_path = os.path.join(proj_root, 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


__config = parse_config()


def get_log_level():
    import logging

    log_level = __config['log_level']
    if log_level == 'DEBUG':
        return logging.DEBUG
    if log_level == 'INFO':
        return logging.INFO
    if log_level == 'WARNING':
        return logging.WARNING
    if log_level == 'ERROR':
        return logging.ERROR
    if log_level == 'CRITICAL':
        return logging.CRITICAL
    raise ValueError(f'Invalid log level: {log_level}')


def get_config():
    return __config
