"""Capture → AI Analysis → Action Execution pipeline.

This is the core loop that connects screen capture to AI decision-making:
1. Capture CATIA screen
2. Send screenshot to cloud AI with context
3. AI analyzes and returns action instructions
4. Execute actions (mouse/keyboard)
5. Repeat

Inspired by better-genshin-impact's task loop architecture.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from catia_mcp.capture.engine import CaptureEngine, CaptureFrame
from catia_mcp.capture.input_sim import InputSimulator
from catia_mcp.capture.overlay import OverlayWindow

logger = logging.getLogger(__name__)


class PipelineState(StrEnum):
    IDLE = "idle"
    CAPTURING = "capturing"
    ANALYZING = "analyzing"
    EXECUTING = "executing"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class ActionCommand:
    """A single action parsed from AI's response."""

    action_type: str  # move, click, double_click, right_click, drag, scroll,
    # key_press, key_combo, type_text, wait
    params: dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class AnalysisResult:
    """Result of AI analysis on a captured frame."""

    description: str = ""
    actions: list[ActionCommand] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    confidence: float = 0.0
    needs_more_info: bool = False
    suggested_region: tuple[int, int, int, int] | None = None


class CaptureOperatePipeline:
    """The main capture-operate pipeline that drives AI-powered CATIA interaction.

    Workflow:
    1. capture_and_prepare() — Take screenshot, encode for AI
    2. (External) AI analyzes the screenshot and returns actions
    3. execute_actions() — Execute the AI's instructions
    4. verify() — Capture again to verify the result
    """

    def __init__(self) -> None:
        self.engine = CaptureEngine()
        self.input = InputSimulator()
        self.overlay = OverlayWindow()
        self._state = PipelineState.IDLE
        self._step_count = 0
        self._history: list[dict[str, Any]] = []
        self._last_frame: CaptureFrame | None = None

    @property
    def state(self) -> str:
        return self._state.value

    def initialize(self, window_title: str = "CATIA") -> dict[str, Any]:
        """Initialize the pipeline: find CATIA, start capture, attach overlay."""
        result = self.engine.start(window_title)
        if result.get("status") != "started":
            self._state = PipelineState.ERROR
            return result

        win = self.engine.target_window
        self.input.set_target(win["hwnd"])
        self.overlay.attach(win["hwnd"], win["rect"])

        self._state = PipelineState.IDLE
        return {
            "status": "initialized",
            "backend": self.engine.backend.value,
            "window": win,
            "overlay": self.overlay.visible,
        }

    def shutdown(self) -> dict[str, str]:
        """Shut down the pipeline."""
        self.overlay.detach()
        self.engine.stop()
        self._state = PipelineState.IDLE
        return {"status": "shutdown"}

    # ── Step 1: Capture ──────────────────────────────────────────────

    def capture_for_ai(
        self,
        region: tuple[int, int, int, int] | None = None,
        add_context: bool = True,
    ) -> dict[str, Any]:
        """Capture the CATIA screen and prepare data for AI analysis.

        Returns the frame data (base64) plus context information
        that helps the AI understand what it's looking at.
        """
        self._state = PipelineState.CAPTURING

        frame = self.engine.capture_region(*region) if region else self.engine.capture()

        self._last_frame = frame

        result: dict[str, Any] = {
            "frame": frame.to_dict(include_image=True, max_b64_len=50000),
            "step": self._step_count,
            "pipeline_state": self._state.value,
        }

        if add_context:
            result["context"] = {
                "window_title": self.engine.target_window.get("title", ""),
                "capture_backend": self.engine.backend.value,
                "overlay_elements": self.overlay.get_elements(),
                "recent_actions": self.input.get_action_log(5),
                "instructions": (
                    "Analyze this CATIA screenshot. Identify what is visible "
                    "(menus, dialogs, 3D view, specification tree, etc.) and "
                    "determine the next action to take. Return a list of "
                    "actions with coordinates relative to the captured image."
                ),
            }

        self._state = PipelineState.IDLE
        return result

    # ── Step 2: Execute Actions ──────────────────────────────────────

    def execute_actions(self, actions: list[dict[str, Any]]) -> dict[str, Any]:
        """Execute a list of action commands from the AI.

        Args:
            actions: List of action dicts, each with:
                - action: "click", "double_click", "right_click", "drag",
                         "scroll", "key_press", "key_combo", "type_text", "wait"
                - params: Action-specific parameters (x, y, key, text, etc.)
                - description: Optional description for overlay display
        """
        self._state = PipelineState.EXECUTING
        self._step_count += 1
        results: list[dict[str, Any]] = []

        for i, action_data in enumerate(actions):
            action = action_data.get("action", "")
            params = action_data.get("params", {})
            desc = action_data.get("description", action)

            if desc:
                x = params.get("x", 0)
                y = params.get("y", 0)
                self.overlay.highlight_click_target(x, y, desc)

            try:
                result = self._execute_single(action, params)
                results.append({"index": i, "action": action, "result": result})
            except Exception as e:
                results.append({"index": i, "action": action, "error": str(e)})

        step_record = {
            "step": self._step_count,
            "action_count": len(actions),
            "results": results,
            "timestamp": time.time(),
        }
        self._history.append(step_record)
        self._state = PipelineState.IDLE
        return step_record

    def _execute_single(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a single action command."""
        if action == "click":
            return self.input.click(params["x"], params["y"], params.get("button", "left"))
        elif action == "double_click":
            return self.input.double_click(params["x"], params["y"])
        elif action == "right_click":
            return self.input.right_click(params["x"], params["y"])
        elif action == "drag":
            return self.input.drag(
                params["from_x"], params["from_y"], params["to_x"], params["to_y"]
            )
        elif action == "scroll":
            return self.input.scroll(params.get("x", 960), params.get("y", 540), params["delta"])
        elif action == "middle_drag":
            return self.input.middle_drag(
                params["from_x"], params["from_y"], params["to_x"], params["to_y"]
            )
        elif action == "key_press":
            return self.input.key_press(params["key"])
        elif action == "key_combo":
            return self.input.key_combo(*params["keys"])
        elif action == "type_text":
            return self.input.type_text(params["text"])
        elif action == "wait":
            time.sleep(params.get("seconds", 0.5))
            return {"action": "wait", "seconds": params.get("seconds", 0.5)}
        elif action == "move":
            return self.input.move_to(params["x"], params["y"])
        else:
            raise ValueError(f"Unknown action: {action}")

    # ── Step 3: Verify ───────────────────────────────────────────────

    def verify_result(self) -> dict[str, Any]:
        """Capture a new frame to verify the result of the last action."""
        return self.capture_for_ai(add_context=True)

    # ── History & State ──────────────────────────────────────────────

    def get_history(self, last_n: int = 5) -> list[dict[str, Any]]:
        return self._history[-last_n:]

    def get_status(self) -> dict[str, Any]:
        return {
            "state": self._state.value,
            "step_count": self._step_count,
            "capture_running": self.engine.is_running,
            "capture_backend": self.engine.backend.value,
            "overlay_visible": self.overlay.visible,
            "overlay_elements": self.overlay.element_count,
            "window": self.engine.target_window,
        }
