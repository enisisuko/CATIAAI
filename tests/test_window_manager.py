"""Tests for the universal window manager."""

from __future__ import annotations

from catia_mcp.capture.window_manager import WindowManager


class TestWindowManagerList:
    def test_list_all(self) -> None:
        wm = WindowManager()
        windows = wm.list_windows()
        assert len(windows) >= 5
        assert all("hwnd" in w and "title" in w for w in windows)

    def test_list_with_filter(self) -> None:
        wm = WindowManager()
        catia = wm.list_windows(filter_keyword="CATIA")
        assert len(catia) >= 1
        assert all("CATIA" in w["title"] for w in catia)

    def test_list_filter_case_insensitive(self) -> None:
        wm = WindowManager()
        excel = wm.list_windows(filter_keyword="excel")
        assert len(excel) >= 1

    def test_list_filter_no_match(self) -> None:
        wm = WindowManager()
        none = wm.list_windows(filter_keyword="xyznonexistent")
        assert len(none) == 0

    def test_refresh(self) -> None:
        wm = WindowManager()
        windows = wm.refresh()
        assert len(windows) >= 5


class TestWindowManagerSelect:
    def test_select_by_title(self) -> None:
        wm = WindowManager()
        result = wm.select_by_title("CATIA")
        assert result["status"] == "selected"
        assert "CATIA" in result["window"]["title"]

    def test_select_by_title_nonexistent(self) -> None:
        wm = WindowManager()
        result = wm.select_by_title("xyznonexistent")
        assert result["status"] == "error"

    def test_select_by_title_excel(self) -> None:
        wm = WindowManager()
        result = wm.select_by_title("Excel")
        assert result["status"] == "selected"

    def test_select_by_title_chrome(self) -> None:
        wm = WindowManager()
        result = wm.select_by_title("Chrome")
        assert result["status"] == "selected"

    def test_select_by_index(self) -> None:
        wm = WindowManager()
        result = wm.select_by_index(0)
        assert result["status"] == "selected"

    def test_select_by_index_out_of_range(self) -> None:
        wm = WindowManager()
        result = wm.select_by_index(999)
        assert result["status"] == "error"

    def test_select_by_hwnd(self) -> None:
        wm = WindowManager()
        wm.refresh()
        windows = wm.list_windows()
        hwnd = windows[0]["hwnd"]
        result = wm.select_by_hwnd(hwnd)
        assert result["status"] == "selected"

    def test_select_with_alias(self) -> None:
        wm = WindowManager()
        result = wm.select_by_title("CATIA", alias="design_app")
        assert result["window"]["alias"] == "design_app"


class TestWindowManagerTarget:
    def test_no_target(self) -> None:
        wm = WindowManager()
        result = wm.get_target_info()
        assert result["status"] == "no_target"

    def test_has_target(self) -> None:
        wm = WindowManager()
        wm.select_by_title("CATIA")
        result = wm.get_target_info()
        assert result["status"] == "active"

    def test_bring_to_front_mock(self) -> None:
        wm = WindowManager()
        wm.select_by_title("CATIA")
        result = wm.bring_to_front()
        assert "mock" in result["status"]

    def test_minimize_mock(self) -> None:
        wm = WindowManager()
        result = wm.minimize_target()
        assert "mock" in result["status"]

    def test_restore_mock(self) -> None:
        wm = WindowManager()
        result = wm.restore_target()
        assert "mock" in result["status"]


class TestWindowManagerGUI:
    def test_picker_mock(self) -> None:
        wm = WindowManager()
        result = wm.open_picker_gui()
        assert "mock" in result["status"]


class TestWindowManagerSwitchTarget:
    def test_switch_targets(self) -> None:
        wm = WindowManager()
        wm.select_by_title("CATIA")
        assert "CATIA" in wm.target.title

        wm.select_by_title("Excel")
        assert "Excel" in wm.target.title

        wm.select_by_title("Chrome")
        assert "Chrome" in wm.target.title
