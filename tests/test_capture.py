"""Tests for the capture-operate pipeline."""

from __future__ import annotations

import time

from catia_mcp.capture.engine import CaptureBackend, CaptureEngine, CaptureFrame
from catia_mcp.capture.input_sim import InputSimulator
from catia_mcp.capture.overlay import OverlayElement, OverlayWindow
from catia_mcp.capture.pipeline import CaptureOperatePipeline


class TestCaptureEngine:
    def test_detect_backend_mock(self) -> None:
        engine = CaptureEngine()
        assert engine.backend == CaptureBackend.MOCK

    def test_find_window_mock(self) -> None:
        engine = CaptureEngine()
        win = engine.find_window("CATIA")
        assert win is not None
        assert "CATIA" in win.title
        assert win.width > 0

    def test_list_windows_mock(self) -> None:
        engine = CaptureEngine()
        windows = engine.list_windows()
        assert len(windows) >= 1

    def test_start_stop(self) -> None:
        engine = CaptureEngine()
        result = engine.start("CATIA")
        assert result["status"] == "started"
        assert engine.is_running
        engine.stop()
        assert not engine.is_running

    def test_capture_mock(self) -> None:
        engine = CaptureEngine()
        engine.start("CATIA")
        frame = engine.capture()
        assert isinstance(frame, CaptureFrame)
        assert frame.backend == CaptureBackend.MOCK
        assert frame.width > 0
        assert len(frame.image_data) > 0
        engine.stop()

    def test_capture_region(self) -> None:
        engine = CaptureEngine()
        engine.start("CATIA")
        frame = engine.capture_region(100, 100, 400, 300)
        assert frame.region == (100, 100, 400, 300)
        engine.stop()

    def test_capture_not_running_raises(self) -> None:
        import pytest

        engine = CaptureEngine()
        with pytest.raises(RuntimeError):
            engine.capture()

    def test_frame_to_dict(self) -> None:
        engine = CaptureEngine()
        engine.start("CATIA")
        frame = engine.capture()
        d = frame.to_dict(include_image=True)
        assert "width" in d
        assert "height" in d
        assert "image_base64" in d
        engine.stop()


class TestOverlayWindow:
    def test_attach_mock(self) -> None:
        overlay = OverlayWindow()
        result = overlay.attach(0x12345, (0, 0, 1920, 1080))
        assert "attached" in result["status"]
        assert overlay.visible

    def test_add_elements(self) -> None:
        overlay = OverlayWindow()
        overlay.attach(0, (0, 0, 1920, 1080))
        overlay.add_rect(100, 100, 200, 150, label="Test Box")
        overlay.add_text(50, 50, "Hello AI")
        overlay.add_circle(500, 300, 25)
        overlay.add_arrow(100, 100, 300, 200, label="Click here")
        assert overlay.element_count == 4

    def test_clear(self) -> None:
        overlay = OverlayWindow()
        overlay.attach(0, (0, 0, 1920, 1080))
        overlay.add_rect(0, 0, 100, 100)
        overlay.clear()
        assert overlay.element_count == 0

    def test_element_expiry(self) -> None:
        elem = OverlayElement(element_type="rect", ttl=0.01)
        time.sleep(0.02)
        assert elem.expired

    def test_highlight_click(self) -> None:
        overlay = OverlayWindow()
        overlay.attach(0, (0, 0, 1920, 1080))
        result = overlay.highlight_click_target(500, 300, "Pad Button")
        assert result["highlighted"]

    def test_detach(self) -> None:
        overlay = OverlayWindow()
        overlay.attach(0, (0, 0, 1920, 1080))
        overlay.add_rect(0, 0, 100, 100)
        overlay.detach()
        assert not overlay.visible
        assert overlay.element_count == 0


class TestInputSimulator:
    def test_mock_click(self) -> None:
        sim = InputSimulator()
        result = sim.click(500, 300)
        assert result["action"] == "click"
        assert result["mock"] is True

    def test_mock_drag(self) -> None:
        sim = InputSimulator()
        result = sim.drag(100, 100, 500, 300)
        assert result["action"] == "drag"

    def test_mock_key_press(self) -> None:
        sim = InputSimulator()
        result = sim.key_press("enter")
        assert result["action"] == "key_press"

    def test_mock_key_combo(self) -> None:
        sim = InputSimulator()
        result = sim.key_combo("ctrl", "s")
        assert result["action"] == "key_combo"
        assert result["keys"] == ["ctrl", "s"]

    def test_mock_type_text(self) -> None:
        sim = InputSimulator()
        result = sim.type_text("Hello CATIA")
        assert result["action"] == "type_text"

    def test_mock_scroll(self) -> None:
        sim = InputSimulator()
        result = sim.scroll(500, 300, 3)
        assert result["action"] == "scroll"

    def test_mock_middle_drag(self) -> None:
        sim = InputSimulator()
        result = sim.middle_drag(500, 300, 600, 400)
        assert result["action"] == "middle_drag"

    def test_action_log(self) -> None:
        sim = InputSimulator()
        sim.click(100, 200)
        sim.key_press("escape")
        log = sim.get_action_log(2)
        assert len(log) == 2
        assert log[0]["action"] == "click"
        assert log[1]["action"] == "key_press"


class TestPipeline:
    def test_initialize(self) -> None:
        pipeline = CaptureOperatePipeline()
        result = pipeline.initialize("CATIA")
        assert result["status"] == "initialized"

    def test_capture_for_ai(self) -> None:
        pipeline = CaptureOperatePipeline()
        pipeline.initialize("CATIA")
        result = pipeline.capture_for_ai()
        assert "frame" in result
        assert "context" in result
        assert result["frame"]["width"] > 0

    def test_execute_actions(self) -> None:
        pipeline = CaptureOperatePipeline()
        pipeline.initialize("CATIA")
        result = pipeline.execute_actions(
            [
                {"action": "click", "params": {"x": 100, "y": 50}, "description": "Test"},
                {"action": "wait", "params": {"seconds": 0.01}},
                {"action": "key_press", "params": {"key": "escape"}},
            ]
        )
        assert result["action_count"] == 3
        assert len(result["results"]) == 3

    def test_verify(self) -> None:
        pipeline = CaptureOperatePipeline()
        pipeline.initialize("CATIA")
        result = pipeline.verify_result()
        assert "frame" in result

    def test_status(self) -> None:
        pipeline = CaptureOperatePipeline()
        pipeline.initialize("CATIA")
        status = pipeline.get_status()
        assert status["state"] == "idle"
        assert status["capture_running"]

    def test_history(self) -> None:
        pipeline = CaptureOperatePipeline()
        pipeline.initialize("CATIA")
        pipeline.execute_actions(
            [
                {"action": "click", "params": {"x": 50, "y": 50}},
            ]
        )
        history = pipeline.get_history()
        assert len(history) == 1

    def test_shutdown(self) -> None:
        pipeline = CaptureOperatePipeline()
        pipeline.initialize("CATIA")
        result = pipeline.shutdown()
        assert result["status"] == "shutdown"
