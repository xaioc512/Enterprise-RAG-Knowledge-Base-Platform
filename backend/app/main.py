"""FastAPI 应用入口"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.utils.logger import setup_logger, logger
from app.database import check_db_connection
from app.api import auth, users, documents, categories, chat, conversations, feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    setup_logger(debug=settings.DEBUG)
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting...")

    # 验证数据库连接
    db_ok = await check_db_connection()
    if db_ok:
        logger.info("Database connection OK")
    else:
        logger.warning("Database connection FAILED — check MySQL configuration")

    yield
    logger.info(f"{settings.APP_NAME} shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(categories.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(feedback.router)


@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    db_ok = await check_db_connection()
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "ok" if db_ok else "error",
    }
