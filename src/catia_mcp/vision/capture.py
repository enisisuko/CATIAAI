"""Screen capture for CATIA window."""

from __future__ import annotations

import base64
import io
import logging
import platform
from typing import Any

logger = logging.getLogger(__name__)


class ScreenCapture:
    """Capture screenshots of CATIA or the entire screen."""

    def __init__(self) -> None:
        self._available = False
        self._setup()

    def _setup(self) -> None:
        if platform.system() != "Windows":
            logger.info("Screen capture not available on %s (requires Windows)", platform.system())
            return
        try:
            import pyautogui  # noqa: F401

            self._available = True
        except ImportError:
            logger.warning("pyautogui not installed. Screen capture disabled.")

    def capture_full_screen(self) -> dict[str, Any]:
        """Capture the entire screen."""
        if not self._available:
            return self._mock_capture("full_screen", 1920, 1080)
        import pyautogui

        screenshot = pyautogui.screenshot()
        return self._image_to_result(screenshot, "full_screen")

    def capture_catia_window(self) -> dict[str, Any]:
        """Capture only the CATIA window."""
        if not self._available:
            return self._mock_capture("catia_window", 1600, 900)
        try:
            import pyautogui

            windows = pyautogui.getWindowsWithTitle("CATIA")
            if not windows:
                return {"error": "CATIA window not found", "status": "failed"}
            win = windows[0]
            screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
            return self._image_to_result(screenshot, "catia_window")
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def capture_region(self, x: int, y: int, width: int, height: int) -> dict[str, Any]:
        """Capture a specific screen region."""
        if not self._available:
            return self._mock_capture("region", width, height)
        import pyautogui

        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return self._image_to_result(screenshot, "region")

    @staticmethod
    def _image_to_result(image: Any, capture_type: str) -> dict[str, Any]:
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return {
            "status": "captured",
            "type": capture_type,
            "width": image.width,
            "height": image.height,
            "format": "png",
            "base64_length": len(b64),
            "image_base64": b64[:200] + "..." if len(b64) > 200 else b64,
        }

    @staticmethod
    def _mock_capture(capture_type: str, width: int, height: int) -> dict[str, Any]:
        return {
            "status": "captured (mock)",
            "type": capture_type,
            "width": width,
            "height": height,
            "format": "png",
            "note": "Mock capture - pyautogui not available on this platform",
        }
