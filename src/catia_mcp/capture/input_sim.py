"""Mouse and keyboard input simulation for CATIA.

Inspired by better-genshin-impact's input simulation system.
Uses Win32 SendInput API for realistic human-like input,
with support for both global and window-specific input methods:

- SendInput: Global input injection (most reliable for CATIA)
- PostMessage: Window-specific, works even if window is not focused
- Natural delays and movement curves for anti-detection
"""

from __future__ import annotations

import logging
import math
import platform
import random
import time
from typing import Any

logger = logging.getLogger(__name__)

IS_WINDOWS = platform.system() == "Windows"


class InputSimulator:
    """Simulate mouse and keyboard input to control CATIA.

    Provides human-like input with natural delays, curved mouse
    movements, and randomized timing.
    """

    def __init__(self, target_hwnd: int = 0) -> None:
        self._hwnd = target_hwnd
        self._is_mock = not IS_WINDOWS
        self._current_x = 0
        self._current_y = 0
        self._base_delay = 0.02
        self._action_log: list[dict[str, Any]] = []

    def set_target(self, hwnd: int) -> None:
        self._hwnd = hwnd

    # ── Mouse Operations ─────────────────────────────────────────────

    def move_to(
        self, x: int, y: int, duration: float = 0.3, natural: bool = True
    ) -> dict[str, Any]:
        """Move mouse to (x, y) with optional natural curve.

        Args:
            x, y: Target screen coordinates.
            duration: Movement duration in seconds.
            natural: If True, use bezier curve for human-like movement.
        """
        if self._is_mock:
            self._current_x, self._current_y = x, y
            return self._log_action("move", x=x, y=y, duration=duration)

        if natural:
            self._bezier_move(x, y, duration)
        else:
            self._direct_move(x, y)

        self._current_x, self._current_y = x, y
        return self._log_action("move", x=x, y=y, duration=duration)

    def click(
        self,
        x: int,
        y: int,
        button: str = "left",
        duration: float = 0.3,
    ) -> dict[str, Any]:
        """Move to position and click.

        Args:
            x, y: Click position (screen coordinates).
            button: "left", "right", or "middle".
            duration: Mouse movement duration before click.
        """
        self.move_to(x, y, duration)
        time.sleep(self._random_delay(0.02, 0.05))

        if not self._is_mock:
            self._send_click(button)

        time.sleep(self._random_delay(0.03, 0.08))
        return self._log_action("click", x=x, y=y, button=button)

    def double_click(self, x: int, y: int, duration: float = 0.3) -> dict[str, Any]:
        """Double-click at position."""
        self.move_to(x, y, duration)
        if not self._is_mock:
            self._send_click("left")
            time.sleep(self._random_delay(0.05, 0.12))
            self._send_click("left")
        return self._log_action("double_click", x=x, y=y)

    def right_click(self, x: int, y: int, duration: float = 0.3) -> dict[str, Any]:
        """Right-click at position (open context menu)."""
        return self.click(x, y, button="right", duration=duration)

    def drag(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        duration: float = 0.5,
    ) -> dict[str, Any]:
        """Drag from one position to another.

        Args:
            from_x, from_y: Start position.
            to_x, to_y: End position.
            duration: Total drag duration.
        """
        self.move_to(from_x, from_y, duration=0.2)
        time.sleep(self._random_delay(0.02, 0.05))

        if not self._is_mock:
            self._send_mouse_down("left")

        self.move_to(to_x, to_y, duration=duration, natural=True)
        time.sleep(self._random_delay(0.02, 0.05))

        if not self._is_mock:
            self._send_mouse_up("left")

        return self._log_action("drag", from_x=from_x, from_y=from_y, to_x=to_x, to_y=to_y)

    def scroll(self, x: int, y: int, delta: int) -> dict[str, Any]:
        """Scroll at position. Positive = up/zoom in, negative = down/zoom out."""
        self.move_to(x, y, duration=0.1, natural=False)

        if not self._is_mock:
            self._send_scroll(delta)

        return self._log_action("scroll", x=x, y=y, delta=delta)

    def middle_drag(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        duration: float = 0.5,
    ) -> dict[str, Any]:
        """Middle-button drag — used for 3D view rotation in CATIA."""
        self.move_to(from_x, from_y, duration=0.1)
        if not self._is_mock:
            self._send_mouse_down("middle")
        self.move_to(to_x, to_y, duration=duration, natural=True)
        if not self._is_mock:
            self._send_mouse_up("middle")
        return self._log_action("middle_drag", from_x=from_x, from_y=from_y, to_x=to_x, to_y=to_y)

    # ── Keyboard Operations ──────────────────────────────────────────

    def key_press(self, key: str) -> dict[str, Any]:
        """Press and release a single key."""
        if not self._is_mock:
            self._send_key(key, down=True)
            time.sleep(self._random_delay(0.03, 0.08))
            self._send_key(key, down=False)
        return self._log_action("key_press", key=key)

    def key_combo(self, *keys: str) -> dict[str, Any]:
        """Press a key combination (e.g., 'ctrl', 's' for Ctrl+S)."""
        if not self._is_mock:
            for k in keys:
                self._send_key(k, down=True)
                time.sleep(self._random_delay(0.01, 0.03))
            time.sleep(self._random_delay(0.03, 0.08))
            for k in reversed(keys):
                self._send_key(k, down=False)
                time.sleep(self._random_delay(0.01, 0.03))
        return self._log_action("key_combo", keys=list(keys))

    def type_text(self, text: str, interval: float = 0.05) -> dict[str, Any]:
        """Type a string character by character with natural timing."""
        if not self._is_mock:
            for char in text:
                self._send_char(char)
                time.sleep(self._random_delay(interval * 0.7, interval * 1.3))
        return self._log_action("type_text", text=text)

    # ── Win32 SendInput Implementation ───────────────────────────────

    def _send_click(self, button: str) -> None:
        self._send_mouse_down(button)
        time.sleep(self._random_delay(0.02, 0.06))
        self._send_mouse_up(button)

    def _send_mouse_down(self, button: str) -> None:

        flags = {"left": 0x0002, "right": 0x0008, "middle": 0x0020}
        self._send_mouse_event(flags.get(button, 0x0002))

    def _send_mouse_up(self, button: str) -> None:

        flags = {"left": 0x0004, "right": 0x0010, "middle": 0x0040}
        self._send_mouse_event(flags.get(button, 0x0004))

    def _send_scroll(self, delta: int) -> None:
        import ctypes

        MOUSEEVENTF_WHEEL = 0x0800
        extra = ctypes.c_ulong(0)
        ii = InputUnion()
        ii.mi = MouseInput(0, 0, delta * 120, MOUSEEVENTF_WHEEL, 0, ctypes.pointer(extra))
        inp = Input(0, ii)
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

    def _send_mouse_event(self, flags: int) -> None:
        import ctypes

        extra = ctypes.c_ulong(0)
        ii = InputUnion()
        ii.mi = MouseInput(0, 0, 0, flags, 0, ctypes.pointer(extra))
        inp = Input(0, ii)
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

    def _direct_move(self, x: int, y: int) -> None:
        import ctypes

        MOUSEEVENTF_MOVE = 0x0001
        MOUSEEVENTF_ABSOLUTE = 0x8000
        screen_w = ctypes.windll.user32.GetSystemMetrics(0)
        screen_h = ctypes.windll.user32.GetSystemMetrics(1)
        nx = int(x * 65535 / screen_w)
        ny = int(y * 65535 / screen_h)
        extra = ctypes.c_ulong(0)
        ii = InputUnion()
        ii.mi = MouseInput(
            nx, ny, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, 0, ctypes.pointer(extra)
        )
        inp = Input(0, ii)
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

    def _bezier_move(self, target_x: int, target_y: int, duration: float) -> None:
        """Move mouse along a bezier curve for natural movement."""
        start_x, start_y = self._current_x, self._current_y
        dist = math.hypot(target_x - start_x, target_y - start_y)
        steps = max(int(dist / 5), 10)
        step_delay = duration / steps

        cx = (start_x + target_x) / 2 + random.uniform(-50, 50)
        cy = (start_y + target_y) / 2 + random.uniform(-50, 50)

        for i in range(steps + 1):
            t = i / steps
            t_smooth = t * t * (3 - 2 * t)
            bx = (
                (1 - t_smooth) ** 2 * start_x
                + 2 * (1 - t_smooth) * t_smooth * cx
                + t_smooth**2 * target_x
            )
            by = (
                (1 - t_smooth) ** 2 * start_y
                + 2 * (1 - t_smooth) * t_smooth * cy
                + t_smooth**2 * target_y
            )
            self._direct_move(int(bx), int(by))
            time.sleep(step_delay)

    def _send_key(self, key: str, down: bool) -> None:
        import ctypes

        VK_MAP = {
            "ctrl": 0x11,
            "shift": 0x10,
            "alt": 0x12,
            "enter": 0x0D,
            "escape": 0x1B,
            "tab": 0x09,
            "space": 0x20,
            "delete": 0x2E,
            "backspace": 0x08,
            "up": 0x26,
            "down": 0x28,
            "left": 0x25,
            "right": 0x27,
            "f1": 0x70,
            "f2": 0x71,
            "f3": 0x72,
            "f4": 0x73,
            "f5": 0x74,
            "f6": 0x75,
            "f7": 0x76,
            "f8": 0x77,
            "f9": 0x78,
            "f10": 0x79,
            "f11": 0x7A,
            "f12": 0x7B,
        }
        vk = VK_MAP.get(key.lower(), ord(key.upper()) if len(key) == 1 else 0)
        flags = 0x0002 if not down else 0
        extra = ctypes.c_ulong(0)
        ii = InputUnion()
        ii.ki = KeyboardInput(vk, 0, flags, 0, ctypes.pointer(extra))
        inp = Input(1, ii)
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

    def _send_char(self, char: str) -> None:
        import ctypes

        KEYEVENTF_UNICODE = 0x0004
        extra = ctypes.c_ulong(0)
        ii = InputUnion()
        ii.ki = KeyboardInput(0, ord(char), KEYEVENTF_UNICODE, 0, ctypes.pointer(extra))
        inp = Input(1, ii)
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
        ii.ki = KeyboardInput(0, ord(char), KEYEVENTF_UNICODE | 0x0002, 0, ctypes.pointer(extra))
        inp2 = Input(1, ii)
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp2), ctypes.sizeof(inp2))

    # ── Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _random_delay(low: float, high: float) -> float:
        return random.uniform(low, high)

    def _log_action(self, action: str, **kwargs: Any) -> dict[str, Any]:
        entry = {"action": action, "timestamp": time.time(), "mock": self._is_mock, **kwargs}
        self._action_log.append(entry)
        if len(self._action_log) > 100:
            self._action_log = self._action_log[-50:]
        return entry

    def get_action_log(self, last_n: int = 10) -> list[dict[str, Any]]:
        return self._action_log[-last_n:]


# ── ctypes structures (only instantiated on Windows) ─────────────────

if IS_WINDOWS:
    import ctypes

    PUL = ctypes.POINTER(ctypes.c_ulong)

    class MouseInput(ctypes.Structure):
        _fields_ = [
            ("dx", ctypes.c_long),
            ("dy", ctypes.c_long),
            ("mouseData", ctypes.c_ulong),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", PUL),
        ]

    class KeyboardInput(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.c_ushort),
            ("wScan", ctypes.c_ushort),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", PUL),
        ]

    class HardwareInput(ctypes.Structure):
        _fields_ = [
            ("uMsg", ctypes.c_ulong),
            ("wParamL", ctypes.c_ushort),
            ("wParamH", ctypes.c_ushort),
        ]

    class InputUnion(ctypes.Union):
        _fields_ = [("ki", KeyboardInput), ("mi", MouseInput), ("hi", HardwareInput)]

    class Input(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong), ("ii", InputUnion)]
