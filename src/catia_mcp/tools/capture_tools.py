"""MCP tools for the universal screen capture-operate system.

Exposes window management, capture, and action execution to the LLM,
enabling it to see and interact with ANY application window like a human.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.capture.pipeline import CaptureOperatePipeline

_pipeline: CaptureOperatePipeline | None = None


def _get_pipeline() -> CaptureOperatePipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = CaptureOperatePipeline()
    return _pipeline


def register(mcp: FastMCP) -> None:
    """Register all capture-operate tools."""

    # ── Window Management ────────────────────────────────────────────

    @mcp.tool()
    def wm_list_windows(filter_keyword: str | None = None) -> dict[str, Any]:
        """List all visible application windows on the system.
        Use this to find the window you want to capture and control.

        Args:
            filter_keyword: Optional filter (e.g., 'CATIA', 'Excel', 'Chrome').
                            Only shows windows whose title contains this string.
        """
        windows = _get_pipeline().window_manager.list_windows(filter_keyword)
        return {"windows": windows, "count": len(windows)}

    @mcp.tool()
    def wm_select_by_title(title_keyword: str, alias: str = "") -> dict[str, Any]:
        """Select a target window by searching its title.
        The selected window becomes the target for all capture/control operations.

        Args:
            title_keyword: Text to match in window title (e.g., 'CATIA', 'Excel').
            alias: Friendly name for this target (e.g., 'design_app').

        Examples:
            wm_select_by_title('CATIA')      → targets CATIA
            wm_select_by_title('Excel')      → targets Microsoft Excel
            wm_select_by_title('Chrome')     → targets Google Chrome
            wm_select_by_title('SolidWorks') → targets SolidWorks
        """
        return _get_pipeline().window_manager.select_by_title(title_keyword, alias)

    @mcp.tool()
    def wm_select_by_index(index: int, alias: str = "") -> dict[str, Any]:
        """Select a target window by its index in the window list.
        Call wm_list_windows first to see the list.

        Args:
            index: 0-based index from wm_list_windows result.
            alias: Friendly name for this target.
        """
        return _get_pipeline().window_manager.select_by_index(index, alias)

    @mcp.tool()
    def wm_select_by_hwnd(hwnd: int, alias: str = "") -> dict[str, Any]:
        """Select a target window by its handle (for advanced use).

        Args:
            hwnd: Window handle from wm_list_windows.
            alias: Friendly name.
        """
        return _get_pipeline().window_manager.select_by_hwnd(hwnd, alias)

    @mcp.tool()
    def wm_get_target() -> dict[str, Any]:
        """Get information about the currently targeted window."""
        return _get_pipeline().window_manager.get_target_info()

    @mcp.tool()
    def wm_open_picker() -> dict[str, Any]:
        """Open a GUI window picker dialog.
        Shows a searchable list of all windows. The user can select
        which application to target. (Windows only)"""
        return _get_pipeline().window_manager.open_picker_gui()

    @mcp.tool()
    def wm_bring_to_front() -> dict[str, Any]:
        """Bring the target window to the foreground."""
        return _get_pipeline().window_manager.bring_to_front()

    @mcp.tool()
    def wm_minimize() -> dict[str, Any]:
        """Minimize the target window."""
        return _get_pipeline().window_manager.minimize_target()

    @mcp.tool()
    def wm_restore() -> dict[str, Any]:
        """Restore the target window from minimized state."""
        return _get_pipeline().window_manager.restore_target()

    # ── Pipeline Lifecycle ───────────────────────────────────────────

    @mcp.tool()
    def co_init(window_title: str = "CATIA") -> dict[str, Any]:
        """Initialize the capture-operate pipeline for any application.
        Finds the window, starts screen capture, and attaches overlay.

        Args:
            window_title: Window title to search for.
                Examples: 'CATIA', 'Excel', 'SolidWorks', 'Chrome', 'Notepad'
        """
        return _get_pipeline().initialize(window_title)

    @mcp.tool()
    def co_init_hwnd(hwnd: int) -> dict[str, Any]:
        """Initialize the pipeline targeting a specific window handle.
        Use after wm_select_by_* to start capture on the selected window.

        Args:
            hwnd: Window handle from wm_list_windows or wm_select_*.
        """
        return _get_pipeline().initialize_with_hwnd(hwnd)

    @mcp.tool()
    def co_switch(window_title: str) -> dict[str, Any]:
        """Switch the capture target to a different application window.
        No need to shut down and re-initialize.

        Args:
            window_title: Title of the new target window.
        """
        return _get_pipeline().switch_target(window_title)

    @mcp.tool()
    def co_shutdown() -> dict[str, str]:
        """Shut down the capture-operate pipeline."""
        return _get_pipeline().shutdown()

    @mcp.tool()
    def co_status() -> dict[str, Any]:
        """Get the current status of the capture-operate pipeline."""
        return _get_pipeline().get_status()

    # ── Screen Capture ───────────────────────────────────────────────

    @mcp.tool()
    def co_capture(
        region_x: int | None = None,
        region_y: int | None = None,
        region_w: int | None = None,
        region_h: int | None = None,
    ) -> dict[str, Any]:
        """Capture the target window screen for AI analysis.
        Returns screenshot data (base64 PNG) with context.

        Args:
            region_x, region_y: Top-left corner of region to capture.
            region_w, region_h: Size of region. If None, captures full window.
        """
        region = None
        if all(v is not None for v in [region_x, region_y, region_w, region_h]):
            region = (region_x, region_y, region_w, region_h)
        return _get_pipeline().capture_for_ai(region=region)

    @mcp.tool()
    def co_capture_and_describe() -> dict[str, Any]:
        """Capture the target window with full context for AI analysis.

        The AI should look at the image and describe:
        1. What application and mode is active
        2. What is visible in the main view
        3. Any open dialogs, menus, or panels
        4. What action should be taken next
        """
        return _get_pipeline().capture_for_ai(add_context=True)

    # ── Action Execution ─────────────────────────────────────────────

    @mcp.tool()
    def co_execute(actions: list[dict[str, Any]]) -> dict[str, Any]:
        """Execute a sequence of mouse/keyboard actions on the target window.

        Args:
            actions: List of action dicts. Each dict has:
                - action: The action type
                - params: Action parameters
                - description: Optional label shown on overlay

        Supported actions:
            click:        {x, y, button?}
            double_click: {x, y}
            right_click:  {x, y}
            drag:         {from_x, from_y, to_x, to_y}
            middle_drag:  {from_x, from_y, to_x, to_y}
            scroll:       {x?, y?, delta}
            key_press:    {key}
            key_combo:    {keys: [...]}
            type_text:    {text}
            move:         {x, y}
            wait:         {seconds}
        """
        return _get_pipeline().execute_actions(actions)

    @mcp.tool()
    def co_click(x: int, y: int, button: str = "left", description: str = "") -> dict[str, Any]:
        """Click at a position on the target window.

        Args:
            x, y: Click position.
            button: 'left', 'right', or 'middle'.
            description: Label shown on overlay.
        """
        return _get_pipeline().execute_actions(
            [
                {
                    "action": "click",
                    "params": {"x": x, "y": y, "button": button},
                    "description": description,
                }
            ]
        )

    @mcp.tool()
    def co_drag(
        from_x: int, from_y: int, to_x: int, to_y: int, description: str = ""
    ) -> dict[str, Any]:
        """Drag from one position to another.

        Args:
            from_x, from_y: Start position.
            to_x, to_y: End position.
            description: Label shown on overlay.
        """
        return _get_pipeline().execute_actions(
            [
                {
                    "action": "drag",
                    "params": {"from_x": from_x, "from_y": from_y, "to_x": to_x, "to_y": to_y},
                    "description": description,
                }
            ]
        )

    @mcp.tool()
    def co_rotate_view(
        dx: int, dy: int, center_x: int = 960, center_y: int = 540
    ) -> dict[str, Any]:
        """Rotate a 3D view using middle-mouse drag (CAD software).

        Args:
            dx, dy: Rotation amount in pixels.
            center_x, center_y: Center point.
        """
        return _get_pipeline().execute_actions(
            [
                {
                    "action": "middle_drag",
                    "params": {
                        "from_x": center_x,
                        "from_y": center_y,
                        "to_x": center_x + dx,
                        "to_y": center_y + dy,
                    },
                    "description": "Rotate 3D view",
                }
            ]
        )

    @mcp.tool()
    def co_zoom(delta: int, x: int = 960, y: int = 540) -> dict[str, Any]:
        """Zoom in/out on the target window.

        Args:
            delta: Positive = zoom in, negative = zoom out.
            x, y: Zoom center.
        """
        return _get_pipeline().execute_actions(
            [
                {
                    "action": "scroll",
                    "params": {"x": x, "y": y, "delta": delta},
                    "description": f"Zoom {'in' if delta > 0 else 'out'}",
                }
            ]
        )

    @mcp.tool()
    def co_type(text: str) -> dict[str, Any]:
        """Type text into the currently focused input.

        Args:
            text: Text to type.
        """
        return _get_pipeline().execute_actions(
            [
                {
                    "action": "type_text",
                    "params": {"text": text},
                    "description": f"Type: {text[:20]}",
                }
            ]
        )

    @mcp.tool()
    def co_shortcut(*keys: str) -> dict[str, Any]:
        """Press a keyboard shortcut.

        Args:
            keys: Keys to press together (e.g., 'ctrl', 's').
        """
        return _get_pipeline().execute_actions(
            [
                {
                    "action": "key_combo",
                    "params": {"keys": list(keys)},
                    "description": "+".join(keys),
                }
            ]
        )

    @mcp.tool()
    def co_verify() -> dict[str, Any]:
        """Capture a new screenshot to verify the last action's result."""
        return _get_pipeline().verify_result()

    # ── Overlay ──────────────────────────────────────────────────────

    @mcp.tool()
    def co_overlay_rect(
        x: int,
        y: int,
        width: int,
        height: int,
        label: str = "",
        color: str = "#00FF00",
    ) -> dict[str, Any]:
        """Draw a highlighted rectangle on the overlay.

        Args:
            x, y: Top-left corner.
            width, height: Size.
            label: Text label.
            color: Hex color.
        """
        return _get_pipeline().overlay.add_rect(x, y, width, height, color, label)

    @mcp.tool()
    def co_overlay_clear() -> dict[str, str]:
        """Clear all overlay elements."""
        return _get_pipeline().overlay.clear()

    # ── History ──────────────────────────────────────────────────────

    @mcp.tool()
    def co_history(last_n: int = 5) -> dict[str, Any]:
        """Get the history of capture-operate steps.

        Args:
            last_n: Number of recent steps to return.
        """
        return {
            "steps": _get_pipeline().get_history(last_n),
            "total_steps": _get_pipeline()._step_count,
        }

    @mcp.tool()
    def co_action_log(last_n: int = 10) -> dict[str, Any]:
        """Get the log of recent input actions.

        Args:
            last_n: Number of recent actions to return.
        """
        return {"actions": _get_pipeline().input.get_action_log(last_n)}
