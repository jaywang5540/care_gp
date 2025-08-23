from fastapi import APIRouter
from app.api.v1.endpoints import health, medicare, consultation

api_router = APIRouter()

# 健康检查路由
api_router.include_router(
    health.router,
    tags=["健康检查"]
)

# Medicare相关路由
api_router.include_router(
    medicare.router,
    prefix="/medicare",
    tags=["Medicare"]
)

# 诊疗相关路由
api_router.include_router(
    consultation.router,
    prefix="/consultation",
    tags=["诊疗管理"]
)