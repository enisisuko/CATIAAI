"""Tests for configuration management."""

from __future__ import annotations

from catia_mcp.config import CATIASettings, get_settings


class TestConfig:
    def test_default_settings(self) -> None:
        settings = CATIASettings()
        assert settings.log_level == "INFO"
        assert settings.catia_version == "V5"
        assert settings.auto_connect is True
        assert settings.use_pycatia is True
        assert settings.vision_enabled is True
        assert settings.transport == "stdio"
        assert settings.port == 8765

    def test_get_settings_singleton(self) -> None:
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_mock_mode_default(self) -> None:
        settings = CATIASettings()
        assert settings.mock_mode is False

    def test_ui_delay(self) -> None:
        settings = CATIASettings()
        assert settings.ui_action_delay == 0.1
