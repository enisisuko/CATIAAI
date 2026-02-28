"""Universal window manager — discover, select, and manage target windows.

Provides a GUI window-picker and programmatic API for selecting ANY
application window to capture and control, not just CATIA.
"""

from __future__ import annotations

import logging
import platform
import threading
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

IS_WINDOWS = platform.system() == "Windows"


@dataclass
class ManagedWindow:
    """A window being tracked by the manager."""

    hwnd: int
    title: str
    process_name: str
    rect: tuple[int, int, int, int]
    width: int
    height: int
    is_target: bool = False
    alias: str = ""
    last_seen: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "hwnd": self.hwnd,
            "title": self.title,
            "process_name": self.process_name,
            "rect": list(self.rect),
            "width": self.width,
            "height": self.height,
            "is_target": self.is_target,
            "alias": self.alias,
        }


class WindowManager:
    """Discovers, lists, and manages application windows.

    Supports targeting ANY window — CATIA, SolidWorks, Excel, browser, etc.
    On non-Windows: returns mock windows for development.
    """

    def __init__(self) -> None:
        self._windows: dict[int, ManagedWindow] = {}
        self._target_hwnd: int = 0
        self._is_mock = not IS_WINDOWS
        self._lock = threading.Lock()

    @property
    def target(self) -> ManagedWindow | None:
        with self._lock:
            return self._windows.get(self._target_hwnd)

    @property
    def target_hwnd(self) -> int:
        return self._target_hwnd

    def refresh(self) -> list[ManagedWindow]:
        """Refresh the list of all visible windows on the system."""
        with self._lock:
            old_target = self._target_hwnd
            self._windows.clear()

            if self._is_mock:
                self._populate_mock_windows()
            else:
                self._populate_real_windows()

            if old_target in self._windows:
                self._windows[old_target].is_target = True
                self._target_hwnd = old_target

            return list(self._windows.values())

    def list_windows(
        self,
        filter_keyword: str | None = None,
        refresh: bool = True,
    ) -> list[dict[str, Any]]:
        """List all visible windows, optionally filtered by keyword.

        Args:
            filter_keyword: Only return windows whose title contains this string.
            refresh: Whether to refresh the window list first.
        """
        if refresh:
            self.refresh()

        with self._lock:
            windows = list(self._windows.values())

        if filter_keyword:
            kw = filter_keyword.lower()
            windows = [w for w in windows if kw in w.title.lower()]

        return [w.to_dict() for w in windows]

    def select_by_hwnd(self, hwnd: int, alias: str = "") -> dict[str, Any]:
        """Select a window as the capture/control target by its handle.

        Args:
            hwnd: Window handle (from list_windows).
            alias: Friendly name for this target (e.g., 'CATIA', 'Excel').
        """
        self.refresh()
        with self._lock:
            if hwnd not in self._windows:
                return {"status": "error", "error": f"Window handle {hwnd} not found"}

            for w in self._windows.values():
                w.is_target = False

            self._target_hwnd = hwnd
            win = self._windows[hwnd]
            win.is_target = True
            if alias:
                win.alias = alias

        return {
            "status": "selected",
            "window": win.to_dict(),
        }

    def select_by_title(self, title_keyword: str, alias: str = "") -> dict[str, Any]:
        """Select a window by searching its title.

        Args:
            title_keyword: Substring to match against window titles.
            alias: Friendly name for this target.
        """
        self.refresh()
        kw = title_keyword.lower()

        with self._lock:
            for w in self._windows.values():
                if kw in w.title.lower():
                    for other in self._windows.values():
                        other.is_target = False
                    self._target_hwnd = w.hwnd
                    w.is_target = True
                    if alias:
                        w.alias = alias
                    return {"status": "selected", "window": w.to_dict()}

        return {
            "status": "error",
            "error": f"No window matching '{title_keyword}' found",
            "available": [w.title for w in self._windows.values()][:20],
        }

    def select_by_index(self, index: int, alias: str = "") -> dict[str, Any]:
        """Select a window by its index in the window list.

        Args:
            index: 0-based index from list_windows result.
            alias: Friendly name for this target.
        """
        self.refresh()
        with self._lock:
            windows = list(self._windows.values())
            if index < 0 or index >= len(windows):
                return {
                    "status": "error",
                    "error": f"Index {index} out of range (0-{len(windows) - 1})",
                }

            for w in windows:
                w.is_target = False

            win = windows[index]
            self._target_hwnd = win.hwnd
            win.is_target = True
            if alias:
                win.alias = alias

        return {"status": "selected", "window": win.to_dict()}

    def get_target_info(self) -> dict[str, Any]:
        """Get information about the currently targeted window."""
        target = self.target
        if target is None:
            return {"status": "no_target", "error": "No window selected. Call wm_select_* first."}

        if not self._is_mock:
            self._update_window_rect(target)

        return {"status": "active", "window": target.to_dict()}

    def bring_to_front(self) -> dict[str, Any]:
        """Bring the target window to the foreground."""
        if self._target_hwnd == 0:
            return {"status": "error", "error": "No target window selected"}

        if self._is_mock:
            return {"status": "brought_to_front (mock)", "hwnd": self._target_hwnd}

        try:
            import win32gui

            win32gui.SetForegroundWindow(self._target_hwnd)
            return {"status": "brought_to_front", "hwnd": self._target_hwnd}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def minimize_target(self) -> dict[str, Any]:
        """Minimize the target window."""
        if self._is_mock:
            return {"status": "minimized (mock)"}
        try:
            import win32gui

            win32gui.ShowWindow(self._target_hwnd, 6)
            return {"status": "minimized"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def restore_target(self) -> dict[str, Any]:
        """Restore the target window from minimized state."""
        if self._is_mock:
            return {"status": "restored (mock)"}
        try:
            import win32gui

            win32gui.ShowWindow(self._target_hwnd, 9)
            return {"status": "restored"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ── GUI Window Picker ────────────────────────────────────────────

    def open_picker_gui(self) -> dict[str, Any]:
        """Open a Tkinter GUI window for picking the target window.

        Shows a list of all windows with live filtering.
        Returns the selected window info after user confirms.
        """
        result: dict[str, Any] = {"status": "cancelled"}

        def run_gui() -> None:
            nonlocal result
            try:
                result = self._run_picker_gui()
            except Exception as e:
                result = {"status": "error", "error": str(e)}

        if self._is_mock:
            return {
                "status": "selected (mock/gui)",
                "note": "GUI not available on this platform. Use wm_select_by_title instead.",
                "window": {
                    "hwnd": 0x12345,
                    "title": "CATIA V5 - [Part1] (Mock)",
                    "process_name": "CNEXT.exe",
                    "width": 1920,
                    "height": 1080,
                },
            }

        thread = threading.Thread(target=run_gui, daemon=True)
        thread.start()
        thread.join(timeout=60)

        return result

    def _run_picker_gui(self) -> dict[str, Any]:
        """Run the Tkinter window picker dialog."""
        import tkinter as tk
        from tkinter import ttk

        self.refresh()
        selected_hwnd: int = 0

        root = tk.Tk()
        root.title("CATIA MCP — Select Target Window")
        root.geometry("700x500")
        root.resizable(True, True)

        header = tk.Frame(root)
        header.pack(fill=tk.X, padx=10, pady=(10, 5))
        tk.Label(
            header, text="Select the application window to control:", font=("Segoe UI", 11, "bold")
        ).pack(side=tk.LEFT)

        filter_frame = tk.Frame(root)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT)
        filter_var = tk.StringVar()
        filter_entry = tk.Entry(filter_frame, textvariable=filter_var, width=40)
        filter_entry.pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        columns = ("title", "process", "size", "hwnd")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        tree.heading("title", text="Window Title")
        tree.heading("process", text="Process")
        tree.heading("size", text="Size")
        tree.heading("hwnd", text="Handle")
        tree.column("title", width=350)
        tree.column("process", width=120)
        tree.column("size", width=100)
        tree.column("hwnd", width=80)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def populate(keyword: str = "") -> None:
            tree.delete(*tree.get_children())
            kw = keyword.lower()
            with self._lock:
                for w in self._windows.values():
                    if kw and kw not in w.title.lower() and kw not in w.process_name.lower():
                        continue
                    tree.insert(
                        "",
                        tk.END,
                        iid=str(w.hwnd),
                        values=(
                            w.title[:80],
                            w.process_name,
                            f"{w.width}x{w.height}",
                            hex(w.hwnd),
                        ),
                    )

        def on_filter(*_: Any) -> None:
            populate(filter_var.get())

        filter_var.trace_add("write", on_filter)
        populate()

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        def on_refresh() -> None:
            self.refresh()
            populate(filter_var.get())

        def on_select() -> None:
            nonlocal selected_hwnd
            sel = tree.selection()
            if sel:
                selected_hwnd = int(sel[0])
                root.destroy()

        def on_cancel() -> None:
            root.destroy()

        ttk.Button(btn_frame, text="Refresh", command=on_refresh).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Select", command=on_select).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side=tk.RIGHT, padx=5)

        tree.bind("<Double-1>", lambda _: on_select())

        root.mainloop()

        if selected_hwnd:
            result = self.select_by_hwnd(selected_hwnd)
            return result

        return {"status": "cancelled"}

    # ── Internal ─────────────────────────────────────────────────────

    def _populate_mock_windows(self) -> None:
        mocks = [
            (0x1001, "CATIA V5 - [Part1]", "CNEXT.exe", (0, 0, 1920, 1080)),
            (0x1002, "CATIA V5 - [Assembly1.CATProduct]", "CNEXT.exe", (0, 0, 1920, 1080)),
            (0x1003, "SolidWorks 2024 - Part1", "SLDWORKS.exe", (0, 0, 1920, 1080)),
            (0x1004, "AutoCAD 2025 - Drawing1.dwg", "acad.exe", (100, 50, 1800, 950)),
            (0x1005, "Microsoft Excel - Book1.xlsx", "EXCEL.EXE", (50, 50, 1400, 900)),
            (0x1006, "Notepad - Untitled", "notepad.exe", (200, 100, 800, 600)),
            (0x1007, "Google Chrome - New Tab", "chrome.exe", (0, 0, 1920, 1080)),
            (0x1008, "Visual Studio Code", "Code.exe", (0, 0, 1920, 1080)),
            (0x1009, "Windows Explorer", "explorer.exe", (100, 100, 1200, 800)),
            (0x100A, "3ds Max 2025", "3dsmax.exe", (0, 0, 1920, 1080)),
        ]
        for hwnd, title, proc, rect in mocks:
            self._windows[hwnd] = ManagedWindow(
                hwnd=hwnd,
                title=title,
                process_name=proc,
                rect=rect,
                width=rect[2] - rect[0],
                height=rect[3] - rect[1],
            )

    def _populate_real_windows(self) -> None:
        try:
            import win32gui
            import win32process

            def enum_cb(hwnd: int, _: Any) -> None:
                if not win32gui.IsWindowVisible(hwnd):
                    return
                title = win32gui.GetWindowText(hwnd)
                if not title or len(title) < 2:
                    return
                rect = win32gui.GetWindowRect(hwnd)
                w = rect[2] - rect[0]
                h = rect[3] - rect[1]
                if w < 50 or h < 50:
                    return

                proc_name = ""
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    import psutil

                    proc_name = psutil.Process(pid).name()
                except Exception:
                    proc_name = "unknown"

                self._windows[hwnd] = ManagedWindow(
                    hwnd=hwnd,
                    title=title,
                    process_name=proc_name,
                    rect=rect,
                    width=w,
                    height=h,
                )

            win32gui.EnumWindows(enum_cb, None)
        except Exception as e:
            logger.error("Failed to enumerate windows: %s", e)

    def _update_window_rect(self, win: ManagedWindow) -> None:
        try:
            import win32gui

            rect = win32gui.GetWindowRect(win.hwnd)
            win.rect = rect
            win.width = rect[2] - rect[0]
            win.height = rect[3] - rect[1]
        except Exception:
            pass
