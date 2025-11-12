from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API
    API_TITLE: str = "古籍整理平台"
    API_VERSION: str = "1.0.0"

    # Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # AI Configuration
    AI_PROVIDER: str = "openai"  # 支持: openai, anthropic, deepseek 等
    AI_MODEL: str = "gpt-3.5-turbo"  # 模型名称
    AI_API_KEY: Optional[str] = None  # API 密钥（可选）
    AI_BASE_URL: Optional[str] = None  # 自定义 API 地址（可选）
    AI_TEMPERATURE: float = 0.7  # 温度参数
    AI_MAX_TOKENS: int = 2000  # 最大 token 数

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
