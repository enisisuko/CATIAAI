"""Configuration management using pydantic-settings."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class CATIASettings(BaseSettings):
    """CATIA MCP Server configuration. Loaded from environment variables or .env file."""

    model_config = {"env_prefix": "CATIA_MCP_", "env_file": ".env", "extra": "ignore"}

    log_level: str = Field(default="INFO", description="Logging level")

    catia_version: str = Field(default="V5", description="CATIA version: V5 or V6")
    auto_connect: bool = Field(default=True, description="Auto-connect to CATIA on startup")
    connection_timeout: int = Field(default=10, description="COM connection timeout in seconds")
    use_pycatia: bool = Field(
        default=True,
        description="Use pycatia library for COM automation (recommended)",
    )

    vision_enabled: bool = Field(default=True, description="Enable vision/UI automation tools")
    screenshot_format: str = Field(default="png", description="Screenshot format: png or jpg")
    ui_action_delay: float = Field(
        default=0.1,
        description="Delay between UI actions in seconds",
    )

    mock_mode: bool = Field(
        default=False,
        description="Force mock mode (auto-enabled on non-Windows)",
    )

    transport: str = Field(default="stdio", description="MCP transport: stdio or sse")
    host: str = Field(default="127.0.0.1", description="SSE host (when transport=sse)")
    port: int = Field(default=8765, description="SSE port (when transport=sse)")


_settings: CATIASettings | None = None


def get_settings() -> CATIASettings:
    global _settings
    if _settings is None:
        _settings = CATIASettings()
    return _settings
