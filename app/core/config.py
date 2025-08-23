from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Medicare GP Assistant"
    APP_VERSION: str = "1.0.0"
    PROJECT_NAME: str = "Care GP - AI Medicare Assistant"
    ENVIRONMENT: str = "development"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # 日志配置
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_PATH: str = "logs"
    LOG_ROTATION: str = "00:00"
    LOG_RETENTION: str = "30 days"
    
    # 数据路径配置
    DATA_PATH: Path = Path("./data")
    MBS_DATA_PATH: Path = Path("./data/mbs_codes")
    CONSULTATIONS_PATH: Path = Path("./data/consultations")
    DOCUMENTS_PATH: Path = Path("./data/documents")
    
    # API配置
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保所有数据目录存在
        self.DATA_PATH.mkdir(parents=True, exist_ok=True)
        self.MBS_DATA_PATH.mkdir(parents=True, exist_ok=True)
        self.CONSULTATIONS_PATH.mkdir(parents=True, exist_ok=True)
        self.DOCUMENTS_PATH.mkdir(parents=True, exist_ok=True)

# 创建配置实例
settings = Settings()

# 打印配置信息
if settings.DEBUG:
    print(f"🚀 {settings.PROJECT_NAME}")
    print(f"📍 环境: {settings.ENVIRONMENT}")
    print(f"🔧 调试模式: {'开启' if settings.DEBUG else '关闭'}")
    print(f"📂 数据目录: {settings.DATA_PATH.absolute()}")