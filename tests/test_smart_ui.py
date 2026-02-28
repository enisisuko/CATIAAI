"""Tests for smart UI automation (pywinauto-based)."""

from __future__ import annotations

from catia_mcp.vision.smart_interaction import SmartUIAutomation


class TestSmartUI:
    def test_init_mock(self) -> None:
        ui = SmartUIAutomation()
        assert ui._is_mock is True

    def test_connect_mock(self) -> None:
        ui = SmartUIAutomation()
        result = ui.connect_to_catia_window()
        assert result["status"] == "mock"

    def test_click_menu_mock(self) -> None:
        ui = SmartUIAutomation()
        result = ui.click_menu("Insert->Body")
        assert result["status"] == "clicked (mock)"
        assert result["menu"] == "Insert->Body"

    def test_click_toolbar_mock(self) -> None:
        ui = SmartUIAutomation()
        result = ui.click_toolbar_button("Pad")
        assert result["status"] == "clicked (mock)"

    def test_dialog_mock(self) -> None:
        ui = SmartUIAutomation()
        result = ui.interact_with_dialog(
            "Pad Definition",
            [
                {"type": "set_text", "target": "Length", "value": "30mm"},
                {"type": "click_button", "target": "OK"},
            ],
        )
        assert result["status"] == "interacted (mock)"
        assert result["actions"] == 2

    def test_spec_tree_mock(self) -> None:
        ui = SmartUIAutomation()
        result = ui.get_specification_tree()
        assert result["status"] == "mock"
        assert len(result["tree"]) > 0

    def test_list_controls_mock(self) -> None:
        ui = SmartUIAutomation()
        result = ui.list_available_controls()
        assert result["status"] == "mock"
        assert len(result["controls"]) > 0

    def test_select_tree_mock(self) -> None:
        ui = SmartUIAutomation()
        result = ui.select_in_tree("PartBody\\Pad.1")
        assert result["status"] == "selected (mock)"

    def test_wait_dialog_mock(self) -> None:
        ui = SmartUIAutomation()
        result = ui.wait_for_dialog("Test Dialog", timeout=5)
        assert result["status"] == "found (mock)"
