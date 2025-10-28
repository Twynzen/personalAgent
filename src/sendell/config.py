"""
Sendell Configuration Management

This module handles all configuration for Sendell using Pydantic Settings.
Configuration is loaded from environment variables and .env files.

Security:
- API keys are validated but never logged
- Sensitive values are marked as SecretStr
- All inputs are validated with Pydantic
"""

from enum import Enum
from pathlib import Path
from typing import List

from pydantic import Field, field_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AutonomyLevel(int, Enum):
    """
    Autonomy levels for the Sendell agent.

    L1 - Monitor Only: Observe system, never take actions
    L2 - Ask Permission: Ask before any action (default, safest)
    L3 - Safe Actions: Auto-execute safe operations (open apps, queries)
    L4 - Modify State: Can close apps, move files, modify system
    L5 - Full Autonomy: Complete freedom (expert mode, use with caution)
    """

    L1_MONITOR_ONLY = 1
    L2_ASK_PERMISSION = 2
    L3_SAFE_ACTIONS = 3
    L4_MODIFY_STATE = 4
    L5_FULL_AUTONOMY = 5


class LogLevel(str, Enum):
    """Logging levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MemoryBackend(str, Enum):
    """Memory/database backend options"""

    SQLITE = "sqlite"
    POSTGRES = "postgres"


class VectorStore(str, Enum):
    """Vector store options for RAG"""

    CHROMA = "chroma"
    PINECONE = "pinecone"


class OpenAIConfig(BaseSettings):
    """OpenAI API configuration"""

    model_config = SettingsConfigDict(env_prefix="OPENAI_", env_file=".env", extra="ignore")

    api_key: SecretStr = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-4-turbo-preview", description="Primary model for reasoning")
    fallback_model: str = Field(
        default="gpt-3.5-turbo", description="Fallback model for simple tasks"
    )
    max_tokens: int = Field(default=2000, ge=1, le=8000, description="Max tokens per response")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature (0=deterministic)"
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: SecretStr) -> SecretStr:
        """Validate OpenAI API key format"""
        key = v.get_secret_value()
        if not key.startswith("sk-"):
            raise ValueError("OpenAI API key must start with 'sk-'")
        if len(key) < 20:
            raise ValueError("OpenAI API key is too short")
        return v


class SendellAgentConfig(BaseSettings):
    """Sendell agent configuration"""

    model_config = SettingsConfigDict(env_prefix="SENDELL_", env_file=".env", extra="ignore")

    autonomy_level: AutonomyLevel = Field(
        default=AutonomyLevel.L2_ASK_PERMISSION, description="Agent autonomy level (1-5)"
    )
    loop_interval: int = Field(
        default=60, ge=10, le=600, description="Proactive loop interval in seconds"
    )
    proactive_mode: bool = Field(
        default=True, description="Enable proactive monitoring and suggestions"
    )

    # Privacy & Security
    blocked_apps: List[str] = Field(
        default_factory=lambda: [
            "1password",
            "keepass",
            "bitwarden",
            "lastpass",
            "banking",
        ],
        description="Apps to never monitor",
    )
    blocked_windows: List[str] = Field(
        default_factory=lambda: ["password", "bank", "credit card", "ssn", "tax"],
        description="Window titles to block (partial matches)",
    )
    scrub_pii: bool = Field(default=True, description="Scrub PII from logs")
    encrypt_data: bool = Field(default=True, description="Encrypt sensitive data at rest")

    @field_validator("blocked_apps", "blocked_windows", mode="before")
    @classmethod
    def parse_comma_separated(cls, v):
        """Parse comma-separated strings from env vars"""
        if isinstance(v, str):
            return [item.strip().lower() for item in v.split(",") if item.strip()]
        return v


class LoggingConfig(BaseSettings):
    """Logging configuration"""

    model_config = SettingsConfigDict(env_prefix="SENDELL_LOG_", env_file=".env", extra="ignore")

    level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    file: Path = Field(default=Path("logs/sendell.log"), description="Log file path")
    max_size: int = Field(default=10, ge=1, le=100, description="Max log size in MB")
    backup_count: int = Field(default=5, ge=1, le=20, description="Number of backup log files")

    @field_validator("file", mode="before")
    @classmethod
    def ensure_path(cls, v):
        """Convert string to Path and create parent directories"""
        path = Path(v) if isinstance(v, str) else v
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


class LangSmithConfig(BaseSettings):
    """LangSmith observability configuration (optional)"""

    model_config = SettingsConfigDict(env_prefix="LANGCHAIN_", env_file=".env", extra="ignore")

    tracing_v2: bool = Field(default=False, description="Enable LangSmith tracing")
    api_key: SecretStr | None = Field(default=None, description="LangSmith API key")
    project: str = Field(default="sendell", description="LangSmith project name")


class MemoryConfig(BaseSettings):
    """Memory and storage configuration"""

    model_config = SettingsConfigDict(env_prefix="SENDELL_", env_file=".env", extra="ignore")

    memory_backend: MemoryBackend = Field(
        default=MemoryBackend.SQLITE, description="Memory backend"
    )
    db_path: Path = Field(default=Path("data/sendell.db"), description="SQLite database path")
    vector_store: VectorStore = Field(default=VectorStore.CHROMA, description="Vector store")
    chroma_path: Path = Field(
        default=Path("data/chroma"), description="Chroma persist directory"
    )

    # PostgreSQL (future v0.2+)
    postgres_host: str | None = Field(default=None, description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str | None = Field(default=None, description="PostgreSQL database name")
    postgres_user: str | None = Field(default=None, description="PostgreSQL user")
    postgres_password: SecretStr | None = Field(default=None, description="PostgreSQL password")

    # Pinecone (optional)
    pinecone_api_key: SecretStr | None = Field(default=None, description="Pinecone API key")
    pinecone_environment: str | None = Field(default=None, description="Pinecone environment")
    pinecone_index: str | None = Field(default=None, description="Pinecone index name")

    @field_validator("db_path", "chroma_path", mode="before")
    @classmethod
    def ensure_data_path(cls, v):
        """Ensure data directories exist"""
        path = Path(v) if isinstance(v, str) else v
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


class MonitoringConfig(BaseSettings):
    """System monitoring thresholds"""

    model_config = SettingsConfigDict(env_prefix="SENDELL_", env_file=".env", extra="ignore")

    cpu_threshold: int = Field(
        default=80, ge=50, le=95, description="CPU alert threshold (%)"
    )
    ram_threshold: int = Field(
        default=85, ge=50, le=95, description="RAM alert threshold (%)"
    )
    disk_threshold: int = Field(
        default=90, ge=70, le=98, description="Disk alert threshold (%)"
    )
    process_ram_threshold: int = Field(
        default=2000, ge=500, le=16000, description="Per-process RAM alert (MB)"
    )


class AdvancedConfig(BaseSettings):
    """Advanced settings (experts only)"""

    model_config = SettingsConfigDict(env_prefix="SENDELL_", env_file=".env", extra="ignore")

    api_timeout: int = Field(default=30, ge=5, le=120, description="API timeout in seconds")
    max_retries: int = Field(default=3, ge=1, le=10, description="Max API retries")
    debug: bool = Field(default=False, description="Enable debug mode")
    disable_telemetry: bool = Field(default=True, description="Disable telemetry")


class Settings(BaseSettings):
    """
    Main Sendell configuration.

    Loads all configuration from environment variables and .env file.
    All settings are validated with Pydantic for type safety.

    Example:
        >>> from sendell.config import get_settings
        >>> settings = get_settings()
        >>> print(settings.agent.autonomy_level)
        AutonomyLevel.L2_ASK_PERMISSION
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Sub-configurations
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    agent: SendellAgentConfig = Field(default_factory=SendellAgentConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    langsmith: LangSmithConfig = Field(default_factory=LangSmithConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    advanced: AdvancedConfig = Field(default_factory=AdvancedConfig)

    def __repr__(self) -> str:
        """Safe representation that doesn't leak secrets"""
        return (
            f"Settings(\n"
            f"  autonomy_level={self.agent.autonomy_level.name},\n"
            f"  openai_model={self.openai.model},\n"
            f"  proactive_mode={self.agent.proactive_mode},\n"
            f"  memory_backend={self.memory.memory_backend.value}\n"
            f")"
        )


# Singleton pattern for settings
_settings: Settings | None = None


def get_settings(force_reload: bool = False) -> Settings:
    """
    Get or create the global Settings instance.

    Args:
        force_reload: Force reload settings from environment

    Returns:
        Settings instance

    Example:
        >>> settings = get_settings()
        >>> api_key = settings.openai.api_key.get_secret_value()
    """
    global _settings
    if _settings is None or force_reload:
        _settings = Settings()
    return _settings


def validate_settings() -> None:
    """
    Validate all settings and raise helpful errors if misconfigured.

    Raises:
        ValueError: If critical settings are missing or invalid
    """
    settings = get_settings()

    # Check OpenAI API key
    if not settings.openai.api_key:
        raise ValueError(
            "OPENAI_API_KEY is required. Get one from https://platform.openai.com/api-keys"
        )

    # Warn about autonomy level
    if settings.agent.autonomy_level >= AutonomyLevel.L4_MODIFY_STATE:
        import warnings

        warnings.warn(
            f"High autonomy level ({settings.agent.autonomy_level.name}) is enabled. "
            "Agent can modify system state. Use with caution!",
            UserWarning,
        )

    # Check memory backend config
    if settings.memory.memory_backend == MemoryBackend.POSTGRES:
        if not all(
            [
                settings.memory.postgres_host,
                settings.memory.postgres_db,
                settings.memory.postgres_user,
                settings.memory.postgres_password,
            ]
        ):
            raise ValueError(
                "PostgreSQL backend requires: "
                "SENDELL_POSTGRES_HOST, DB, USER, and PASSWORD"
            )

    # Check vector store config
    if settings.memory.vector_store == VectorStore.PINECONE:
        if not settings.memory.pinecone_api_key:
            raise ValueError("Pinecone requires SENDELL_PINECONE_API_KEY")


# For convenience
__all__ = [
    "Settings",
    "get_settings",
    "validate_settings",
    "AutonomyLevel",
    "LogLevel",
    "MemoryBackend",
    "VectorStore",
]
