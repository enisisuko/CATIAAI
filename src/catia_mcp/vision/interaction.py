"""Mouse and keyboard interaction for CATIA UI automation."""

from __future__ import annotations

import logging
import platform
import time
from typing import Any

logger = logging.getLogger(__name__)


class UIInteraction:
    """Automate mouse/keyboard interaction with CATIA when API isn't sufficient."""

    def __init__(self) -> None:
        self._available = False
        self._is_mock = True
        self._setup()

    def _setup(self) -> None:
        if platform.system() != "Windows":
            logger.info("UI interaction not available on %s", platform.system())
            return
        try:
            import pyautogui  # noqa: F401

            self._available = True
            self._is_mock = False
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
        except ImportError:
            logger.warning("pyautogui not installed. UI interaction disabled.")

    def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> dict[str, Any]:
        if not self._available:
            return {"status": "clicked (mock)", "x": x, "y": y, "button": button, "clicks": clicks}
        import pyautogui

        pyautogui.click(x, y, clicks=clicks, button=button)
        return {"status": "clicked", "x": x, "y": y, "button": button, "clicks": clicks}

    def double_click(self, x: int, y: int) -> dict[str, Any]:
        return self.click(x, y, clicks=2)

    def right_click(self, x: int, y: int) -> dict[str, Any]:
        return self.click(x, y, button="right")

    def drag(
        self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5
    ) -> dict[str, Any]:
        if not self._available:
            return {"status": "dragged (mock)", "from": [start_x, start_y], "to": [end_x, end_y]}
        import pyautogui

        pyautogui.moveTo(start_x, start_y)
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
        return {"status": "dragged", "from": [start_x, start_y], "to": [end_x, end_y]}

    def type_text(self, text: str, interval: float = 0.02) -> dict[str, Any]:
        if not self._available:
            return {"status": "typed (mock)", "text": text}
        import pyautogui

        pyautogui.typewrite(text, interval=interval)
        return {"status": "typed", "text": text}

    def press_key(self, key: str) -> dict[str, Any]:
        if not self._available:
            return {"status": "pressed (mock)", "key": key}
        import pyautogui

        pyautogui.press(key)
        return {"status": "pressed", "key": key}

    def hotkey(self, *keys: str) -> dict[str, Any]:
        if not self._available:
            return {"status": "hotkey (mock)", "keys": list(keys)}
        import pyautogui

        pyautogui.hotkey(*keys)
        return {"status": "hotkey", "keys": list(keys)}

    def move_to(self, x: int, y: int) -> dict[str, Any]:
        if not self._available:
            return {"status": "moved (mock)", "x": x, "y": y}
        import pyautogui

        pyautogui.moveTo(x, y)
        return {"status": "moved", "x": x, "y": y}

    def scroll(self, clicks: int, x: int | None = None, y: int | None = None) -> dict[str, Any]:
        if not self._available:
            return {"status": "scrolled (mock)", "clicks": clicks}
        import pyautogui

        pyautogui.scroll(clicks, x, y)
        return {"status": "scrolled", "clicks": clicks}

    def find_on_screen(self, image_path: str, confidence: float = 0.8) -> dict[str, Any]:
        """Find an image element on screen (e.g., a button icon)."""
        if not self._available:
            return {"status": "found (mock)", "image": image_path, "x": 500, "y": 300}
        try:
            import pyautogui

            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return {"status": "found", "x": center.x, "y": center.y, "region": list(location)}
            return {"status": "not_found", "image": image_path}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_catia_window_info(self) -> dict[str, Any]:
        """Get CATIA window position and size."""
        if not self._available:
            return {
                "status": "mock",
                "title": "CATIA V5 - [Part1]",
                "x": 0,
                "y": 0,
                "width": 1920,
                "height": 1080,
                "is_active": True,
            }
        try:
            import pyautogui

            windows = pyautogui.getWindowsWithTitle("CATIA")
            if not windows:
                return {"status": "not_found", "error": "CATIA window not found"}
            win = windows[0]
            return {
                "status": "found",
                "title": win.title,
                "x": win.left,
                "y": win.top,
                "width": win.width,
                "height": win.height,
                "is_active": win.isActive,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def wait(self, seconds: float) -> dict[str, Any]:
        time.sleep(seconds)
        return {"status": "waited", "seconds": seconds}
