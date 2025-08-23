import sys
import os
from pathlib import Path
from loguru import logger
from app.core.config import settings
import uuid
from contextvars import ContextVar

# 创建请求ID的上下文变量
request_id_var: ContextVar[str] = ContextVar('request_id', default='')

def set_request_id() -> str:
    """设置新的请求ID"""
    request_id = str(uuid.uuid4())[:8]
    request_id_var.set(request_id)
    return request_id

def get_request_id() -> str:
    """获取当前请求ID"""
    return request_id_var.get()

# 自定义日志格式
def custom_format(record):
    """自定义日志格式，包含请求ID"""
    request_id = get_request_id()
    if request_id:
        return "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>[{extra[request_id]}]</cyan> | <level>{message}</level>\n"
    else:
        return "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>\n"

# 清除默认的日志处理器
logger.remove()

# 添加控制台输出
logger.add(
    sys.stdout,
    format=custom_format,
    level=settings.LOG_LEVEL,
    colorize=True,
    enqueue=True,
    backtrace=True,
    diagnose=True
)

# 确保日志目录存在
log_path = Path(settings.LOG_PATH)
log_path.mkdir(parents=True, exist_ok=True)

# 添加文件输出 - 一般日志
logger.add(
    log_path / "app_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level="DEBUG" if settings.DEBUG else "INFO",
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True
)

# 添加错误日志文件
logger.add(
    log_path / "error_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level="ERROR",
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True
)

# 启动日志
logger.info(f"🚀 {settings.PROJECT_NAME} v{settings.APP_VERSION} 启动")
logger.info(f"📍 环境: {settings.ENVIRONMENT}")
logger.info(f"🔧 调试模式: {'开启' if settings.DEBUG else '关闭'}")
logger.info(f"📝 日志级别: {settings.LOG_LEVEL}")
logger.info(f"📂 日志目录: {log_path.absolute()}")

# 导出logger供其他模块使用
__all__ = ['logger', 'set_request_id', 'get_request_id']