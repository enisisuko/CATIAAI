"""MCP tools for vision-based CATIA interaction (screen capture + automation)."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.vision.capture import ScreenCapture
from catia_mcp.vision.interaction import UIInteraction

_capture = ScreenCapture()
_interaction = UIInteraction()


def register(mcp: FastMCP) -> None:
    """Register all vision/UI automation tools with the MCP server."""

    @mcp.tool()
    def capture_screenshot(mode: str = "catia") -> dict[str, Any]:
        """Take a screenshot of CATIA or the full screen.
        Use when you need to visually inspect the current state,
        find UI elements, or verify operations.
        Args:
            mode: 'catia' (CATIA window only), 'full' (entire screen),
                  or 'region' (requires additional params via capture_region).
        """
        if mode == "full":
            return _capture.capture_full_screen()
        return _capture.capture_catia_window()

    @mcp.tool()
    def capture_region(x: int, y: int, width: int, height: int) -> dict[str, Any]:
        """Capture a specific region of the screen.
        Args:
            x, y: Top-left corner of the region.
            width, height: Size of the region in pixels.
        """
        return _capture.capture_region(x, y, width, height)

    @mcp.tool()
    def click_at(x: int, y: int, button: str = "left", clicks: int = 1) -> dict[str, Any]:
        """Click at a specific screen coordinate.
        Use for interacting with CATIA UI elements not accessible via COM API.
        Args:
            x, y: Screen coordinates to click.
            button: 'left', 'right', or 'middle'.
            clicks: Number of clicks (1=single, 2=double).
        """
        return _interaction.click(x, y, button, clicks)

    @mcp.tool()
    def double_click_at(x: int, y: int) -> dict[str, Any]:
        """Double-click at a specific screen coordinate.
        Args:
            x, y: Screen coordinates.
        """
        return _interaction.double_click(x, y)

    @mcp.tool()
    def right_click_at(x: int, y: int) -> dict[str, Any]:
        """Right-click at a specific screen coordinate (open context menu).
        Args:
            x, y: Screen coordinates.
        """
        return _interaction.right_click(x, y)

    @mcp.tool()
    def drag_and_drop(
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5,
    ) -> dict[str, Any]:
        """Drag from one point to another.
        Useful for moving features, resizing, or 3D rotation.
        Args:
            start_x, start_y: Start coordinates.
            end_x, end_y: End coordinates.
            duration: Drag duration in seconds.
        """
        return _interaction.drag(start_x, start_y, end_x, end_y, duration)

    @mcp.tool()
    def type_text_input(text: str) -> dict[str, Any]:
        """Type text into the currently focused input field.
        Args:
            text: Text to type.
        """
        return _interaction.type_text(text)

    @mcp.tool()
    def press_key(key: str) -> dict[str, Any]:
        """Press a single key.
        Args:
            key: Key name - 'enter', 'escape', 'tab', 'delete',
                 'f1'-'f12', 'up', 'down', 'left', 'right', etc.
        """
        return _interaction.press_key(key)

    @mcp.tool()
    def keyboard_shortcut(*keys: str) -> dict[str, Any]:
        """Press a keyboard shortcut (hotkey combination).
        Args:
            keys: Keys to press simultaneously, e.g., 'ctrl', 's' for Ctrl+S.
        """
        return _interaction.hotkey(*keys)

    @mcp.tool()
    def scroll_wheel(clicks: int, x: int | None = None, y: int | None = None) -> dict[str, Any]:
        """Scroll the mouse wheel. Useful for zooming in CATIA.
        Args:
            clicks: Scroll amount (positive=up/zoom in, negative=down/zoom out).
            x, y: Optional position to scroll at.
        """
        return _interaction.scroll(clicks, x, y)

    @mcp.tool()
    def find_on_screen(image_path: str, confidence: float = 0.8) -> dict[str, Any]:
        """Find a UI element on screen by matching an image template.
        Use for finding buttons, icons, or specific UI elements.
        Args:
            image_path: Path to the template image file.
            confidence: Match confidence threshold (0-1).
        """
        return _interaction.find_on_screen(image_path, confidence)

    @mcp.tool()
    def get_catia_window_info() -> dict[str, Any]:
        """Get CATIA window position, size, and state.
        Useful for calculating relative positions of UI elements."""
        return _interaction.get_catia_window_info()

    @mcp.tool()
    def wait_seconds(seconds: float) -> dict[str, Any]:
        """Wait for a specified duration. Use when CATIA needs time
        to process an operation before the next step.
        Args:
            seconds: Time to wait.
        """
        return _interaction.wait(seconds)
