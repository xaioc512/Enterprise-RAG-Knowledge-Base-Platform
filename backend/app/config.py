"""应用配置管理 — 基于 pydantic-settings"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置，所有值可通过 .env 文件或环境变量覆盖"""

    # --- 应用 ---
    APP_NAME: str = "RAG知识库平台"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    CORS_ORIGINS: str = ""  # 逗号分隔，为空则使用默认值
    RATE_LIMIT: str = "200/minute"  # 全局速率限制

    # --- 数据库 ---
    DATABASE_URL: str = ""  # 环境变量覆盖（测试用SQLite等场景）
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "rag_platform"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """异步数据库 URL — 可通过 DATABASE_URL 环境变量覆盖"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """同步数据库 URL（Alembic 迁移使用）"""
        if self.DATABASE_URL:
            # 将异步驱动替换为同步驱动
            return self.DATABASE_URL.replace("+asyncmy", "+mysqldb").replace("+aiosqlite", "+pysqlite")
        return (
            f"mysql+mysqldb://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- DeepSeek ---
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_CHAT_MODEL: str = "deepseek-chat"
    DEEPSEEK_EMBED_MODEL: str = "deepseek-embedding"  # 待确认具体模型名

    # --- JWT ---
    JWT_SECRET: str = "change-me-in-production-use-a-strong-random-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24小时

    # --- 管理员注册密钥 ---
    # 注册时提供此密钥则自动成为管理员；为空则允许所有人注册为管理员
    ADMIN_REGISTRATION_KEY: str = "admin-key-change-me"

    # --- Chroma ---
    CHROMA_PERSIST_DIR: str = str(Path(__file__).parent.parent / "chroma_data")

    # --- 文件上传 ---
    UPLOAD_DIR: str = str(Path(__file__).parent.parent / "uploads")
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS_STR: str = ".pdf,.docx,.md,.txt"

    @property
    def ALLOWED_EXTENSIONS(self) -> set[str]:
        return {ext.strip() for ext in self.ALLOWED_EXTENSIONS_STR.split(",") if ext.strip()}

    # --- RAG ---
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RETRIEVAL_K: int = 5
    MAX_HISTORY_ROUNDS: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
