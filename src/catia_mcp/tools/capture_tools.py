"""MCP tools for the screen capture-operate system.

Exposes the capture → analyze → act pipeline to the LLM,
enabling it to see and interact with the CATIA UI like a human.
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

    # ── Pipeline Lifecycle ───────────────────────────────────────────

    @mcp.tool()
    def co_init(window_title: str = "CATIA") -> dict[str, Any]:
        """Initialize the capture-operate pipeline.
        Finds the CATIA window, starts screen capture, and attaches overlay.
        Must be called before using any other co_* tools.

        Args:
            window_title: Window title to search for (default: 'CATIA').
        """
        return _get_pipeline().initialize(window_title)

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
        """Capture the CATIA screen and prepare for AI analysis.
        Returns the screenshot data (base64 PNG) with context.

        Use this to 'see' the CATIA window. The AI should analyze
        the returned image and decide what actions to take next.

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
        """Capture the CATIA screen with full context for AI analysis.
        Returns the frame plus instructions for the AI to analyze it.

        The AI should look at the image and describe:
        1. What CATIA workbench/mode is active
        2. What is visible in the 3D view
        3. The state of the specification tree
        4. Any open dialogs or menus
        5. What action should be taken next
        """
        return _get_pipeline().capture_for_ai(add_context=True)

    # ── Action Execution ─────────────────────────────────────────────

    @mcp.tool()
    def co_execute(actions: list[dict[str, Any]]) -> dict[str, Any]:
        """Execute a sequence of mouse/keyboard actions on CATIA.
        Actions are performed with human-like timing and movement.

        Args:
            actions: List of action dicts. Each dict has:
                - action: The action type
                - params: Action parameters
                - description: Optional label shown on overlay

        Supported actions and their params:
            click:        {x, y, button?}
            double_click: {x, y}
            right_click:  {x, y}
            drag:         {from_x, from_y, to_x, to_y}
            middle_drag:  {from_x, from_y, to_x, to_y}  (3D view rotation)
            scroll:       {x?, y?, delta}  (zoom in/out)
            key_press:    {key}  (e.g., 'enter', 'escape', 'f1')
            key_combo:    {keys: [...]}  (e.g., ['ctrl', 's'])
            type_text:    {text}
            move:         {x, y}
            wait:         {seconds}

        Example:
            co_execute([
                {"action": "click", "params": {"x": 100, "y": 50},
                 "description": "Click File menu"},
                {"action": "wait", "params": {"seconds": 0.5}},
                {"action": "click", "params": {"x": 120, "y": 80},
                 "description": "Click Save"},
            ])
        """
        return _get_pipeline().execute_actions(actions)

    @mcp.tool()
    def co_click(
        x: int,
        y: int,
        button: str = "left",
        description: str = "",
    ) -> dict[str, Any]:
        """Click at a specific position on the CATIA window.
        Shows a visual indicator on the overlay before clicking.

        Args:
            x, y: Click position (relative to CATIA window).
            button: 'left', 'right', or 'middle'.
            description: Label shown on the overlay.
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
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        description: str = "",
    ) -> dict[str, Any]:
        """Drag from one position to another on the CATIA window.

        Args:
            from_x, from_y: Start position.
            to_x, to_y: End position.
            description: Label shown on the overlay.
        """
        return _get_pipeline().execute_actions(
            [
                {
                    "action": "drag",
                    "params": {
                        "from_x": from_x,
                        "from_y": from_y,
                        "to_x": to_x,
                        "to_y": to_y,
                    },
                    "description": description,
                }
            ]
        )

    @mcp.tool()
    def co_rotate_view(
        dx: int,
        dy: int,
        center_x: int = 960,
        center_y: int = 540,
    ) -> dict[str, Any]:
        """Rotate the 3D view in CATIA using middle-mouse-button drag.

        Args:
            dx, dy: Rotation amount in pixels.
            center_x, center_y: Center point to rotate around.
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
        """Zoom in or out in the CATIA 3D view.

        Args:
            delta: Positive = zoom in, negative = zoom out.
            x, y: Zoom center position.
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
        """Type text into the currently focused input in CATIA.

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
        """Press a keyboard shortcut in CATIA.

        Args:
            keys: Keys to press together (e.g., 'ctrl', 's').

        Common CATIA shortcuts:
            Ctrl+S — Save
            Ctrl+Z — Undo
            Ctrl+Y — Redo
            Ctrl+Shift+F — Fit All In
            Escape — Cancel current operation
            F3 — Toggle specification tree
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
        """Capture a new screenshot to verify the result of the last action.
        Use after executing actions to check if they succeeded."""
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
        """Draw a highlighted rectangle on the CATIA overlay.
        Use to mark regions of interest for the user.

        Args:
            x, y: Top-left corner position.
            width, height: Rectangle size.
            label: Text label to show.
            color: Color in hex (e.g., '#00FF00').
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
        """Get the log of recent input actions (clicks, keystrokes, etc.).

        Args:
            last_n: Number of recent actions to return.
        """
        return {"actions": _get_pipeline().input.get_action_log(last_n)}
