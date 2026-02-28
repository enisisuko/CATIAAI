"""MCP tools for intelligent CATIA UI automation via pywinauto.

These tools provide element-based UI interaction (find by text/type),
menu navigation, dialog handling, and specification tree access.
More reliable than coordinate-based clicking for complex UI workflows.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.vision.smart_interaction import SmartUIAutomation

_smart_ui = SmartUIAutomation()


def register(mcp: FastMCP) -> None:
    """Register all smart UI automation tools."""

    @mcp.tool()
    def connect_catia_ui() -> dict[str, Any]:
        """Connect to the CATIA window for UI automation via pywinauto.
        Enables element-based interaction (menus, buttons, dialogs)
        instead of coordinate-based clicking."""
        return _smart_ui.connect_to_catia_window()

    @mcp.tool()
    def click_menu_item(menu_path: str) -> dict[str, Any]:
        """Click a CATIA menu item by its path.
        More reliable than coordinate clicking for menu operations.

        Args:
            menu_path: Menu path with '->' separating levels.
                Examples:
                - 'Insert->Body'
                - 'File->Save As...'
                - 'Insert->Sketch'
                - 'Tools->Macro->Macros...'
                - 'Edit->Undo'
        """
        return _smart_ui.click_menu(menu_path)

    @mcp.tool()
    def click_toolbar(button_text: str) -> dict[str, Any]:
        """Click a CATIA toolbar button by its tooltip text.
        Use this for toolbar operations when you know the button name.

        Args:
            button_text: Toolbar button tooltip text.
                Examples: 'Pad', 'Pocket', 'Sketch', 'Fillet', 'Chamfer',
                'Shell', 'Hole', 'Mirror', 'Pattern', 'Measure Between'.
        """
        return _smart_ui.click_toolbar_button(button_text)

    @mcp.tool()
    def interact_dialog(dialog_title: str, actions: list[dict[str, str]]) -> dict[str, Any]:
        """Interact with a CATIA dialog box (fill forms, click buttons).
        Use this for complex dialog interactions that COM API can't handle.

        Args:
            dialog_title: Title of the dialog window.
            actions: List of action dicts, each with:
                - type: 'set_text', 'click_button', 'select_combo', 'check', 'uncheck'
                - target: Control label/text
                - value: Value to set (for set_text and select_combo)

        Example:
            interact_dialog('Pad Definition', [
                {'type': 'set_text', 'target': 'Length', 'value': '30mm'},
                {'type': 'click_button', 'target': 'OK'}
            ])
        """
        return _smart_ui.interact_with_dialog(dialog_title, actions)

    @mcp.tool()
    def read_spec_tree_ui() -> dict[str, Any]:
        """Read the CATIA specification tree via UI automation.
        Use when COM-based get_feature_tree doesn't provide enough detail
        or when you need to see exactly what's visible in the tree."""
        return _smart_ui.get_specification_tree()

    @mcp.tool()
    def list_ui_controls() -> dict[str, Any]:
        """List all visible UI controls (buttons, menus, etc.) in the CATIA window.
        Useful for discovering available toolbar buttons and control identifiers
        when you're unsure what operations are available."""
        return _smart_ui.list_available_controls()

    @mcp.tool()
    def select_tree_node(node_path: str) -> dict[str, Any]:
        r"""Select an item in the CATIA specification tree by its path.
        This is equivalent to clicking on a tree item.

        Args:
            node_path: Path in the tree with '\\' separating levels.
                Examples:
                - 'PartBody\\Pad.1'
                - 'PartBody\\Hole.1'
                - 'Geometrical Set.1\\Point.1'
        """
        return _smart_ui.select_in_tree(node_path)

    @mcp.tool()
    def wait_for_dialog_appear(title: str, timeout: int = 10) -> dict[str, Any]:
        """Wait for a dialog box to appear in CATIA.
        Use before interact_dialog when an operation triggers a dialog.

        Args:
            title: Expected dialog title.
            timeout: Maximum wait time in seconds.
        """
        return _smart_ui.wait_for_dialog(title, timeout)
