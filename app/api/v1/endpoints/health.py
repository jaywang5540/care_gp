from fastapi import APIRouter
from app.core.config import settings
from app.utils.response import ResponseUtil
from app.schemas.common_response import SuccessResponse
from typing import Dict, Any
import os
from pathlib import Path

router = APIRouter()

@router.get("/health", response_model=SuccessResponse[Dict[str, Any]], summary="健康检查")
async def health_check():
    """
    系统健康检查
    
    返回系统状态、版本信息和资源状态
    """
    # 检查数据目录
    data_dirs = {
        "mbs_codes": settings.MBS_DATA_PATH.exists(),
        "consultations": settings.CONSULTATIONS_PATH.exists(),
        "documents": settings.DOCUMENTS_PATH.exists()
    }
    
    # 计算数据目录中的文件数
    file_counts = {}
    for name, path in [
        ("mbs_codes", settings.MBS_DATA_PATH),
        ("consultations", settings.CONSULTATIONS_PATH),
        ("documents", settings.DOCUMENTS_PATH)
    ]:
        if Path(path).exists():
            file_counts[name] = len(list(Path(path).glob("*")))
        else:
            file_counts[name] = 0
    
    health_data = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "data_directories": data_dirs,
        "file_counts": file_counts,
        "api_prefix": settings.API_V1_PREFIX
    }
    
    return ResponseUtil.success(
        data=health_data,
        message="系统运行正常"
    )

@router.get("/info", response_model=SuccessResponse[Dict[str, Any]], summary="系统信息")
async def system_info():
    """
    获取系统详细信息
    
    返回配置、路径和环境信息
    """
    info = {
        "application": {
            "name": settings.PROJECT_NAME,
            "version": settings.APP_VERSION,
            "description": "AI辅助Medicare Benefits Schedule账单系统"
        },
        "logging": {
            "log_level": settings.LOG_LEVEL,
            "log_path": str(Path(settings.LOG_PATH).absolute())
        },
        "paths": {
            "data": str(settings.DATA_PATH.absolute()),
            "mbs_codes": str(settings.MBS_DATA_PATH.absolute()),
            "consultations": str(settings.CONSULTATIONS_PATH.absolute()),
            "documents": str(settings.DOCUMENTS_PATH.absolute()),
            "logs": str(Path(settings.LOG_PATH).absolute())
        },
        "api": {
            "prefix": settings.API_V1_PREFIX,
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }
    
    return ResponseUtil.success(
        data=info,
        message="系统信息获取成功"
    )