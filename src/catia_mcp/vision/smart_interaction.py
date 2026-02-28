"""Intelligent CATIA UI automation using pywinauto.

pywinauto (https://github.com/pywinauto/pywinauto) provides proper Windows
UI element discovery and interaction, much more reliable than coordinate-based
clicking. It can find menus, dialogs, buttons, and tree controls by their
properties.

Falls back to pyautogui for coordinate-based operations when needed.
"""

from __future__ import annotations

import logging
import platform
from typing import Any

logger = logging.getLogger(__name__)

PYWINAUTO_AVAILABLE = False
try:
    if platform.system() == "Windows":
        import pywinauto  # noqa: F401

        PYWINAUTO_AVAILABLE = True
except ImportError:
    pass


class SmartUIAutomation:
    """Enhanced UI automation for CATIA using pywinauto.

    Provides element-based interaction (find buttons, menus, dialogs by text/type)
    rather than just coordinate-based clicking.
    """

    def __init__(self) -> None:
        self._app: Any = None
        self._catia_window: Any = None
        self._is_mock = not PYWINAUTO_AVAILABLE

    def connect_to_catia_window(self) -> dict[str, Any]:
        """Connect to the CATIA main window using pywinauto."""
        if self._is_mock:
            return {
                "status": "mock",
                "note": "pywinauto not available, using mock mode",
                "window": "CATIA V5 (Mock)",
            }

        from pywinauto import Application

        try:
            self._app = Application(backend="uia").connect(title_re=".*CATIA.*")
            self._catia_window = self._app.top_window()
            return {
                "status": "connected",
                "window_title": self._catia_window.window_text(),
                "rect": {
                    "left": self._catia_window.rectangle().left,
                    "top": self._catia_window.rectangle().top,
                    "right": self._catia_window.rectangle().right,
                    "bottom": self._catia_window.rectangle().bottom,
                },
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def click_menu(self, menu_path: str) -> dict[str, Any]:
        """Click a menu item by its path (e.g., 'Insert->Body' or 'File->Save As...').

        Args:
            menu_path: Menu path with '->' separating levels.
        """
        if self._is_mock:
            return {"status": "clicked (mock)", "menu": menu_path}

        try:
            self._catia_window.menu_select(menu_path)
            return {"status": "clicked", "menu": menu_path}
        except Exception as e:
            return {"status": "error", "menu": menu_path, "error": str(e)}

    def click_toolbar_button(self, button_text: str) -> dict[str, Any]:
        """Click a toolbar button by its tooltip or text.

        Args:
            button_text: Button tooltip text (e.g., 'Pad', 'Pocket', 'Sketch').
        """
        if self._is_mock:
            return {"status": "clicked (mock)", "button": button_text}

        try:
            button = self._catia_window.child_window(title=button_text, control_type="Button")
            button.click()
            return {"status": "clicked", "button": button_text}
        except Exception as e:
            return {"status": "error", "button": button_text, "error": str(e)}

    def interact_with_dialog(
        self, dialog_title: str, actions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Interact with a CATIA dialog box.

        Args:
            dialog_title: Title of the dialog window.
            actions: List of actions, each a dict with:
                - type: 'set_text', 'click_button', 'select_combo', 'check', 'uncheck'
                - target: control identifier (title or auto_id)
                - value: value to set (for set_text, select_combo)
        """
        if self._is_mock:
            return {"status": "interacted (mock)", "dialog": dialog_title, "actions": len(actions)}

        try:
            dialog = self._app.window(title=dialog_title)
            results = []
            for action in actions:
                action_type = action.get("type", "")
                target = action.get("target", "")
                value = action.get("value", "")

                if action_type == "set_text":
                    ctrl = dialog.child_window(title=target, control_type="Edit")
                    ctrl.set_text(value)
                    results.append({"action": "set_text", "target": target, "value": value})
                elif action_type == "click_button":
                    ctrl = dialog.child_window(title=target, control_type="Button")
                    ctrl.click()
                    results.append({"action": "click_button", "target": target})
                elif action_type == "select_combo":
                    ctrl = dialog.child_window(title=target, control_type="ComboBox")
                    ctrl.select(value)
                    results.append({"action": "select_combo", "target": target, "value": value})
                elif action_type == "check":
                    ctrl = dialog.child_window(title=target, control_type="CheckBox")
                    ctrl.check()
                    results.append({"action": "check", "target": target})
                elif action_type == "uncheck":
                    ctrl = dialog.child_window(title=target, control_type="CheckBox")
                    ctrl.uncheck()
                    results.append({"action": "uncheck", "target": target})

            return {"status": "completed", "dialog": dialog_title, "results": results}
        except Exception as e:
            return {"status": "error", "dialog": dialog_title, "error": str(e)}

    def get_specification_tree(self) -> dict[str, Any]:
        """Read the CATIA specification tree via UI automation.

        This is useful when COM access to the tree is limited.
        """
        if self._is_mock:
            return {
                "status": "mock",
                "tree": [
                    {"name": "PartBody", "children": ["Pad.1", "Pocket.1"]},
                    {"name": "Geometrical Set.1", "children": []},
                ],
            }

        try:
            tree_ctrl = self._catia_window.child_window(control_type="Tree")
            items = []
            for item in tree_ctrl.descendants():
                items.append({"name": item.window_text(), "type": item.control_type()})
            return {"status": "read", "items": items[:100]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def list_available_controls(self) -> dict[str, Any]:
        """List all visible UI controls in the CATIA window.

        Useful for debugging and finding the right control identifiers.
        """
        if self._is_mock:
            return {
                "status": "mock",
                "controls": [
                    {"title": "Pad", "type": "Button"},
                    {"title": "Pocket", "type": "Button"},
                    {"title": "Sketch", "type": "Button"},
                    {"title": "File", "type": "MenuItem"},
                ],
            }

        try:
            controls = []
            for ctrl in self._catia_window.descendants():
                try:
                    text = ctrl.window_text()
                    if text and len(text) < 100:
                        controls.append(
                            {
                                "title": text,
                                "type": ctrl.control_type(),
                                "rect": str(ctrl.rectangle()),
                            }
                        )
                except Exception:
                    pass
            return {"status": "listed", "controls": controls[:200]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def select_in_tree(self, node_path: str) -> dict[str, Any]:
        """Select an item in the specification tree by its path.

        Args:
            node_path: Tree path with '\\' separating levels
                       (e.g., 'PartBody\\Pad.1').
        """
        if self._is_mock:
            return {"status": "selected (mock)", "path": node_path}

        try:
            tree = self._catia_window.child_window(control_type="Tree")
            item = tree.get_item(node_path)
            item.select()
            return {"status": "selected", "path": node_path}
        except Exception as e:
            return {"status": "error", "path": node_path, "error": str(e)}

    def wait_for_dialog(self, title: str, timeout: int = 10) -> dict[str, Any]:
        """Wait for a dialog to appear.

        Args:
            title: Dialog window title.
            timeout: Maximum wait time in seconds.
        """
        if self._is_mock:
            return {"status": "found (mock)", "dialog": title}

        try:
            dialog = self._app.window(title=title)
            dialog.wait("visible", timeout=timeout)
            return {"status": "found", "dialog": title}
        except Exception as e:
            return {"status": "timeout", "dialog": title, "error": str(e)}
