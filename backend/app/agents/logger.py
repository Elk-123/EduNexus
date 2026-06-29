"""
Agent 模块日志配置
"""
import logging
import sys

# 模块级 logger
logger = logging.getLogger("edunexus.agents")
logger.setLevel(logging.DEBUG)

# 控制台 handler（开发环境用）
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-7s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# 防止传播到 root logger
logger.propagate = False


def get_logger(name: str = None) -> logging.Logger:
    """获取子模块 logger"""
    if name:
        return logging.getLogger(f"edunexus.agents.{name}")
    return logger
