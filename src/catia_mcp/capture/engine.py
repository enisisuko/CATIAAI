"""Screen capture engine — multi-backend high-performance window capture.

Universal capture engine that works with ANY application window,
not just CATIA. Inspired by better-genshin-impact's GameCapture system.
Supports multiple capture backends with automatic fallback:
  1. DXcam  — Desktop Duplication API, 240Hz+ (fastest)
  2. BitBlt — GDI capture via win32gui, captures specific windows
  3. MSS    — Cross-platform fallback, moderate speed
  4. Mock   — Returns synthetic frames for testing on non-Windows
"""

from __future__ import annotations

import base64
import io
import logging
import platform
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class CaptureBackend(StrEnum):
    DXCAM = "dxcam"
    BITBLT = "bitblt"
    MSS = "mss"
    MOCK = "mock"


@dataclass
class CaptureFrame:
    """A single captured frame with metadata."""

    width: int
    height: int
    timestamp: float
    backend: CaptureBackend
    image_data: bytes = field(repr=False)
    region: tuple[int, int, int, int] | None = None  # (x, y, w, h)

    def to_base64_png(self) -> str:
        return base64.b64encode(self.image_data).decode("utf-8")

    def to_dict(self, include_image: bool = False, max_b64_len: int = 500) -> dict[str, Any]:
        d: dict[str, Any] = {
            "width": self.width,
            "height": self.height,
            "timestamp": self.timestamp,
            "backend": self.backend.value,
            "region": self.region,
            "data_size_bytes": len(self.image_data),
        }
        if include_image:
            b64 = self.to_base64_png()
            d["image_base64"] = b64 if len(b64) <= max_b64_len else b64[:max_b64_len] + "..."
        return d


@dataclass
class WindowInfo:
    hwnd: int
    title: str
    rect: tuple[int, int, int, int]  # (left, top, right, bottom)
    width: int
    height: int
    is_visible: bool


class CaptureEngine:
    """Multi-backend screen capture engine for ANY application window.

    Usage:
        engine = CaptureEngine()
        engine.start("CATIA")          # find and lock to CATIA window
        engine.start("Excel")          # ...or any other app
        engine.start_with_hwnd(0x1234) # ...or by window handle
        frame = engine.capture()       # capture current frame
        region = engine.capture_region(100, 100, 400, 300)
        engine.stop()
    """

    def __init__(self, preferred_backend: CaptureBackend | None = None) -> None:
        self._backend = preferred_backend or self._detect_best_backend()
        self._target_hwnd: int = 0
        self._target_title: str = ""
        self._target_rect: tuple[int, int, int, int] = (0, 0, 1920, 1080)
        self._running = False
        self._frame_count = 0
        self._dxcam_instance: Any = None
        logger.info("CaptureEngine initialized with backend: %s", self._backend)

    @staticmethod
    def _detect_best_backend() -> CaptureBackend:
        if platform.system() != "Windows":
            return CaptureBackend.MOCK
        try:
            import dxcam  # noqa: F401

            return CaptureBackend.DXCAM
        except ImportError:
            pass
        try:
            import win32gui  # noqa: F401

            return CaptureBackend.BITBLT
        except ImportError:
            pass
        try:
            import mss  # noqa: F401

            return CaptureBackend.MSS
        except ImportError:
            pass
        return CaptureBackend.MOCK

    @property
    def backend(self) -> CaptureBackend:
        return self._backend

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def target_window(self) -> dict[str, Any]:
        return {
            "hwnd": self._target_hwnd,
            "title": self._target_title,
            "rect": self._target_rect,
        }

    # ── Window Discovery ─────────────────────────────────────────────

    def find_window(self, title_keyword: str = "CATIA") -> WindowInfo | None:
        """Find a window by title keyword."""
        if self._backend == CaptureBackend.MOCK:
            return WindowInfo(
                hwnd=0x12345,
                title="CATIA V5 - [Part1] (Mock)",
                rect=(0, 0, 1920, 1080),
                width=1920,
                height=1080,
                is_visible=True,
            )

        try:
            import win32gui

            result: WindowInfo | None = None

            def enum_cb(hwnd: int, _: Any) -> None:
                nonlocal result
                if not win32gui.IsWindowVisible(hwnd):
                    return
                text = win32gui.GetWindowText(hwnd)
                if title_keyword.lower() in text.lower():
                    rect = win32gui.GetWindowRect(hwnd)
                    result = WindowInfo(
                        hwnd=hwnd,
                        title=text,
                        rect=rect,
                        width=rect[2] - rect[0],
                        height=rect[3] - rect[1],
                        is_visible=True,
                    )

            win32gui.EnumWindows(enum_cb, None)
            return result
        except Exception as e:
            logger.error("Failed to find window: %s", e)
            return None

    def list_windows(self) -> list[dict[str, Any]]:
        """List all visible windows."""
        if self._backend == CaptureBackend.MOCK:
            return [
                {"hwnd": 0x12345, "title": "CATIA V5 - [Part1]", "width": 1920, "height": 1080},
                {"hwnd": 0x12346, "title": "CATIA V5 - [Assembly1]", "width": 1920, "height": 1080},
            ]

        windows: list[dict[str, Any]] = []
        try:
            import win32gui

            def enum_cb(hwnd: int, _: Any) -> None:
                if win32gui.IsWindowVisible(hwnd):
                    text = win32gui.GetWindowText(hwnd)
                    if text:
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append(
                            {
                                "hwnd": hwnd,
                                "title": text,
                                "width": rect[2] - rect[0],
                                "height": rect[3] - rect[1],
                            }
                        )

            win32gui.EnumWindows(enum_cb, None)
        except Exception as e:
            logger.error("Failed to list windows: %s", e)
        return windows

    # ── Start / Stop ─────────────────────────────────────────────────

    def start(self, title_keyword: str = "CATIA") -> dict[str, Any]:
        """Find the target window by title and start capture session."""
        win = self.find_window(title_keyword)
        if win is None:
            return {"status": "error", "error": f"Window '{title_keyword}' not found"}
        return self._start_with_window(win)

    def start_with_hwnd(
        self, hwnd: int, title: str = "", rect: tuple[int, int, int, int] = (0, 0, 1920, 1080)
    ) -> dict[str, Any]:
        """Start capture on a specific window handle (from WindowManager)."""
        win = WindowInfo(
            hwnd=hwnd,
            title=title,
            rect=rect,
            width=rect[2] - rect[0],
            height=rect[3] - rect[1],
            is_visible=True,
        )
        return self._start_with_window(win)

    def _start_with_window(self, win: WindowInfo) -> dict[str, Any]:
        """Internal: start capture session for the given window."""
        self._target_hwnd = win.hwnd
        self._target_title = win.title
        self._target_rect = win.rect
        self._running = True
        self._frame_count = 0

        if self._backend == CaptureBackend.DXCAM:
            try:
                import dxcam

                self._dxcam_instance = dxcam.create()
            except Exception as e:
                logger.warning("DXcam init failed: %s, falling back", e)
                self._backend = CaptureBackend.BITBLT

        return {
            "status": "started",
            "backend": self._backend.value,
            "window": {"title": win.title, "hwnd": win.hwnd, "size": [win.width, win.height]},
        }

    def stop(self) -> dict[str, str]:
        """Stop capture session."""
        self._running = False
        if self._dxcam_instance is not None:
            try:
                self._dxcam_instance.stop()
            except Exception:
                pass
            self._dxcam_instance = None
        return {"status": "stopped", "frames_captured": str(self._frame_count)}

    # ── Capture Methods ──────────────────────────────────────────────

    def capture(self) -> CaptureFrame:
        """Capture a full frame of the target window."""
        if not self._running:
            raise RuntimeError("CaptureEngine not running. Call start() first.")

        self._frame_count += 1
        ts = time.time()

        if self._backend == CaptureBackend.DXCAM:
            return self._capture_dxcam(ts)
        elif self._backend == CaptureBackend.BITBLT:
            return self._capture_bitblt(ts)
        elif self._backend == CaptureBackend.MSS:
            return self._capture_mss(ts)
        else:
            return self._capture_mock(ts)

    def capture_region(self, x: int, y: int, w: int, h: int) -> CaptureFrame:
        """Capture a specific region relative to the target window."""
        frame = self.capture()
        frame.region = (x, y, w, h)
        # In real impl, crop the image here
        return frame

    def _capture_dxcam(self, ts: float) -> CaptureFrame:
        """Capture using DXcam (Desktop Duplication API, fastest)."""
        try:
            frame_np = self._dxcam_instance.grab(
                region=(
                    self._target_rect[0],
                    self._target_rect[1],
                    self._target_rect[2],
                    self._target_rect[3],
                )
            )
            if frame_np is None:
                return self._capture_mock(ts)

            from PIL import Image

            img = Image.fromarray(frame_np)
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=False)
            return CaptureFrame(
                width=img.width,
                height=img.height,
                timestamp=ts,
                backend=CaptureBackend.DXCAM,
                image_data=buf.getvalue(),
            )
        except Exception as e:
            logger.warning("DXcam capture failed: %s", e)
            return self._capture_mock(ts)

    def _capture_bitblt(self, ts: float) -> CaptureFrame:
        """Capture using BitBlt (GDI, captures specific window)."""
        try:
            from ctypes import windll

            import win32gui
            import win32ui

            hwnd = self._target_hwnd
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            w = right - left
            h = bottom - top

            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
            save_dc.SelectObject(bitmap)

            windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)

            bmp_info = bitmap.GetInfo()
            bmp_data = bitmap.GetBitmapBits(True)

            from PIL import Image

            img = Image.frombuffer(
                "RGB", (bmp_info["bmWidth"], bmp_info["bmHeight"]), bmp_data, "raw", "BGRX", 0, 1
            )

            buf = io.BytesIO()
            img.save(buf, format="PNG")

            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

            return CaptureFrame(
                width=w,
                height=h,
                timestamp=ts,
                backend=CaptureBackend.BITBLT,
                image_data=buf.getvalue(),
            )
        except Exception as e:
            logger.warning("BitBlt capture failed: %s", e)
            return self._capture_mock(ts)

    def _capture_mss(self, ts: float) -> CaptureFrame:
        """Capture using mss (cross-platform, moderate speed)."""
        try:
            import mss

            with mss.mss() as sct:
                monitor = {
                    "left": self._target_rect[0],
                    "top": self._target_rect[1],
                    "width": self._target_rect[2] - self._target_rect[0],
                    "height": self._target_rect[3] - self._target_rect[1],
                }
                shot = sct.grab(monitor)
                from PIL import Image

                img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                return CaptureFrame(
                    width=img.width,
                    height=img.height,
                    timestamp=ts,
                    backend=CaptureBackend.MSS,
                    image_data=buf.getvalue(),
                )
        except Exception as e:
            logger.warning("MSS capture failed: %s", e)
            return self._capture_mock(ts)

    def _capture_mock(self, ts: float) -> CaptureFrame:
        """Generate a mock frame for non-Windows testing."""
        w = self._target_rect[2] - self._target_rect[0]
        h = self._target_rect[3] - self._target_rect[1]
        if w <= 0:
            w = 1920
        if h <= 0:
            h = 1080

        mock_png = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02"
            b"\x00\x00\x00\x90wS\xde"
            b"\x00\x00\x00\x0cIDATx"
            b"\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05"
            b"\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return CaptureFrame(
            width=w,
            height=h,
            timestamp=ts,
            backend=CaptureBackend.MOCK,
            image_data=mock_png,
        )
