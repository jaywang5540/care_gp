from typing import Any, Optional
from app.schemas.common_response import SuccessResponse, ErrorResponse

class ResponseUtil:
    """响应工具类"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = 200) -> SuccessResponse:
        """
        返回成功响应
        
        Args:
            data: 响应数据
            message: 成功消息
            code: 状态码
            
        Returns:
            SuccessResponse: 成功响应对象
        """
        return SuccessResponse(
            code=code,
            message=message,
            data=data,
            success=True
        )
    
    @staticmethod
    def error(message: str = "操作失败", code: int = 400, data: Any = None) -> ErrorResponse:
        """
        返回错误响应
        
        Args:
            message: 错误消息
            code: 错误码
            data: 额外数据（通常为None）
            
        Returns:
            ErrorResponse: 错误响应对象
        """
        return ErrorResponse(
            code=code,
            message=message,
            data=data,
            success=False
        )