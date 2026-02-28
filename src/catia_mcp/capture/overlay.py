"""Transparent overlay window for CATIA.

Inspired by better-genshin-impact's overlay system.
Creates a transparent, click-through window on top of CATIA to display:
- AI analysis results (bounding boxes, labels)
- Operation status and progress
- Visual guides and annotations

Uses Win32 API layered windows (WS_EX_LAYERED + WS_EX_TRANSPARENT).
On non-Windows, provides a mock implementation.
"""

from __future__ import annotations

import logging
import platform
import threading
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class OverlayElement:
    """A visual element to draw on the overlay."""

    element_type: str  # "rect", "circle", "text", "line", "arrow"
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    color: str = "#00FF00"
    text: str = ""
    thickness: int = 2
    opacity: float = 0.8
    ttl: float = 3.0
    created_at: float = field(default_factory=time.time)

    @property
    def expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl


class OverlayWindow:
    """Transparent overlay rendered on top of the CATIA window.

    On Windows: creates a real WS_EX_LAYERED transparent window.
    On other platforms: maintains element state for mock testing.
    """

    def __init__(self) -> None:
        self._elements: list[OverlayElement] = []
        self._visible = False
        self._target_hwnd: int = 0
        self._target_rect: tuple[int, int, int, int] = (0, 0, 1920, 1080)
        self._is_mock = platform.system() != "Windows"
        self._overlay_hwnd: int = 0
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def element_count(self) -> int:
        with self._lock:
            return len([e for e in self._elements if not e.expired])

    def attach(self, hwnd: int, rect: tuple[int, int, int, int]) -> dict[str, Any]:
        """Attach the overlay to a target window (CATIA)."""
        self._target_hwnd = hwnd
        self._target_rect = rect

        if self._is_mock:
            self._visible = True
            return {
                "status": "attached (mock)",
                "target_hwnd": hwnd,
                "overlay_rect": list(rect),
            }

        try:
            self._create_win32_overlay()
            self._visible = True
            return {
                "status": "attached",
                "target_hwnd": hwnd,
                "overlay_hwnd": self._overlay_hwnd,
                "overlay_rect": list(rect),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def detach(self) -> dict[str, str]:
        """Remove the overlay."""
        self._visible = False
        with self._lock:
            self._elements.clear()

        if not self._is_mock and self._overlay_hwnd:
            try:
                import win32gui

                win32gui.DestroyWindow(self._overlay_hwnd)
            except Exception:
                pass
            self._overlay_hwnd = 0

        return {"status": "detached"}

    def _create_win32_overlay(self) -> None:
        """Create a transparent layered window using Win32 API."""
        import ctypes

        user32 = ctypes.windll.user32

        WS_EX_LAYERED = 0x80000
        WS_EX_TRANSPARENT = 0x20
        WS_EX_TOPMOST = 0x8
        WS_EX_TOOLWINDOW = 0x80
        WS_POPUP = 0x80000000
        LWA_ALPHA = 0x2

        left, top, right, bottom = self._target_rect
        w = right - left
        h = bottom - top

        ex_style = WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST | WS_EX_TOOLWINDOW

        self._overlay_hwnd = user32.CreateWindowExW(
            ex_style,
            "Static",
            "CATIA MCP Overlay",
            WS_POPUP,
            left,
            top,
            w,
            h,
            0,
            0,
            0,
            0,
        )

        user32.SetLayeredWindowAttributes(self._overlay_hwnd, 0, 200, LWA_ALPHA)
        user32.ShowWindow(self._overlay_hwnd, 1)
        user32.UpdateWindow(self._overlay_hwnd)

    # ── Element Management ───────────────────────────────────────────

    def add_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: str = "#00FF00",
        label: str = "",
        thickness: int = 2,
        ttl: float = 5.0,
    ) -> dict[str, Any]:
        """Draw a rectangle on the overlay (e.g., highlight a detected element)."""
        elem = OverlayElement(
            element_type="rect",
            x=x,
            y=y,
            width=width,
            height=height,
            color=color,
            text=label,
            thickness=thickness,
            ttl=ttl,
        )
        with self._lock:
            self._elements.append(elem)
        return {
            "type": "rect",
            "position": [x, y, width, height],
            "label": label,
            "color": color,
        }

    def add_text(
        self,
        x: int,
        y: int,
        text: str,
        color: str = "#FFFFFF",
        ttl: float = 5.0,
    ) -> dict[str, Any]:
        """Display text on the overlay."""
        elem = OverlayElement(element_type="text", x=x, y=y, text=text, color=color, ttl=ttl)
        with self._lock:
            self._elements.append(elem)
        return {"type": "text", "position": [x, y], "text": text}

    def add_circle(
        self,
        cx: int,
        cy: int,
        radius: int,
        color: str = "#FF0000",
        ttl: float = 5.0,
    ) -> dict[str, Any]:
        """Draw a circle on the overlay."""
        elem = OverlayElement(
            element_type="circle",
            x=cx,
            y=cy,
            width=radius * 2,
            height=radius * 2,
            color=color,
            ttl=ttl,
        )
        with self._lock:
            self._elements.append(elem)
        return {"type": "circle", "center": [cx, cy], "radius": radius}

    def add_arrow(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str = "#FFFF00",
        label: str = "",
        ttl: float = 5.0,
    ) -> dict[str, Any]:
        """Draw an arrow on the overlay (e.g., indicate click direction)."""
        elem = OverlayElement(
            element_type="arrow",
            x=x1,
            y=y1,
            width=x2 - x1,
            height=y2 - y1,
            color=color,
            text=label,
            ttl=ttl,
        )
        with self._lock:
            self._elements.append(elem)
        return {"type": "arrow", "from": [x1, y1], "to": [x2, y2], "label": label}

    def clear(self) -> dict[str, str]:
        """Remove all overlay elements."""
        with self._lock:
            count = len(self._elements)
            self._elements.clear()
        return {"status": "cleared", "removed": str(count)}

    def get_elements(self) -> list[dict[str, Any]]:
        """Get all active (non-expired) overlay elements."""
        with self._lock:
            self._elements = [e for e in self._elements if not e.expired]
            return [
                {
                    "type": e.element_type,
                    "x": e.x,
                    "y": e.y,
                    "text": e.text,
                    "color": e.color,
                    "remaining_ttl": round(e.ttl - (time.time() - e.created_at), 1),
                }
                for e in self._elements
            ]

    def highlight_click_target(self, x: int, y: int, label: str = "Click") -> dict[str, Any]:
        """Show a visual indicator where the AI is about to click."""
        self.add_circle(x, y, 15, color="#FF0000", ttl=2.0)
        self.add_text(x + 20, y - 10, label, color="#FF0000", ttl=2.0)
        return {"highlighted": True, "position": [x, y], "label": label}
