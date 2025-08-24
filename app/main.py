from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import logger, set_request_id, get_request_id
from app.api.v1.router import api_router
import time
import traceback
from pathlib import Path

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description="AI辅助Medicare Benefits Schedule账单系统"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求和响应"""
    start_time = time.time()
    
    # 生成并设置请求ID
    request_id = set_request_id()
    
    # 记录请求信息
    logger.bind(request_id=request_id).info(
        f"📥 [{request_id}] 收到请求: {request.method} {request.url.path}"
    )
    
    if request.url.query:
        logger.bind(request_id=request_id).debug(f"查询参数: {request.url.query}")
    
    try:
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 根据状态码使用不同级别
        if response.status_code < 400:
            logger.bind(request_id=request_id).success(
                f"✅ [{request_id}] 请求完成: {request.method} {request.url.path} | "
                f"状态: {response.status_code} | 耗时: {process_time:.3f}s"
            )
        elif response.status_code < 500:
            logger.bind(request_id=request_id).warning(
                f"⚠️ [{request_id}] 客户端错误: {request.method} {request.url.path} | "
                f"状态: {response.status_code} | 耗时: {process_time:.3f}s"
            )
        else:
            logger.bind(request_id=request_id).error(
                f"❌ [{request_id}] 服务器错误: {request.method} {request.url.path} | "
                f"状态: {response.status_code} | 耗时: {process_time:.3f}s"
            )
        
        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录异常
        logger.bind(request_id=request_id).exception(
            f"💥 [{request_id}] 请求处理异常: {request.method} {request.url.path} | "
            f"耗时: {process_time:.3f}s | 异常: {type(e).__name__}"
        )
        
        # 重新抛出异常，让FastAPI处理
        raise

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    request_id = get_request_id() or "no-request-id"
    
    # 记录异常
    logger.bind(request_id=request_id).exception(
        f"🔥 [{request_id}] 未处理异常 | 路径: {request.url.path} | "
        f"异常: {type(exc).__name__}: {str(exc)}"
    )
    
    # 返回错误响应
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "内部服务器错误",
            "detail": str(exc),
            "request_id": request_id
        }
    )

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("=" * 50)
    logger.info(f"🚀 {settings.PROJECT_NAME} 正在启动...")
    logger.info(f"📂 数据目录: {settings.DATA_PATH.absolute()}")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("🔄 正在关闭应用...")
    logger.info("✅ 应用已安全关闭")

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# 挂载静态文件目录
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """返回欢迎页面或API信息"""
    index_file = static_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.APP_VERSION,
        "description": "AI辅助Medicare Benefits Schedule账单系统",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": f"{settings.API_V1_PREFIX}/health"
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }