"""Tests for CATIA Sketcher operations."""

from __future__ import annotations

import pytest

from catia_mcp.catia.connection import CATIAConnection


class TestSketchLifecycle:
    def test_create_sketch(self, catia_with_part: CATIAConnection) -> None:
        result = catia_with_part.create_sketch("XY")
        assert result["name"] == "Sketch.1"
        assert result["plane"] == "XY"
        assert catia_with_part.active_sketch is not None

    def test_close_sketch(self, catia_with_part: CATIAConnection) -> None:
        catia_with_part.create_sketch("XY")
        result = catia_with_part.close_sketch()
        assert result["status"] == "closed"
        assert catia_with_part.active_sketch is None

    def test_multiple_sketches(self, catia_with_part: CATIAConnection) -> None:
        catia_with_part.create_sketch("XY")
        catia_with_part.close_sketch()
        catia_with_part.create_sketch("YZ")
        assert catia_with_part.active_sketch.name == "Sketch.2"

    def test_close_without_sketch_raises(self, catia_with_part: CATIAConnection) -> None:
        with pytest.raises(RuntimeError, match="No active sketch"):
            catia_with_part.close_sketch()


class TestSketchElements:
    @pytest.fixture(autouse=True)
    def _open_sketch(self, catia_with_part: CATIAConnection) -> None:
        self.catia = catia_with_part
        self.catia.create_sketch("XY")

    def test_line(self) -> None:
        result = self.catia.sketch_line(0, 0, 100, 0)
        assert result["type"] == "line"
        assert result["from"] == [0, 0]
        assert result["to"] == [100, 0]

    def test_circle(self) -> None:
        result = self.catia.sketch_circle(50, 50, 25)
        assert result["type"] == "circle"
        assert result["radius"] == 25

    def test_rectangle(self) -> None:
        result = self.catia.sketch_rectangle(0, 0, 100, 50)
        assert result["type"] == "rectangle"
        assert len(result["ids"]) == 4

    def test_arc(self) -> None:
        result = self.catia.sketch_arc(0, 0, 30, 0, 180)
        assert result["type"] == "arc"
        assert result["angles"] == [0, 180]

    def test_spline(self) -> None:
        points = [(0, 0), (10, 5), (20, 0), (30, -5)]
        result = self.catia.sketch_spline(points)
        assert result["type"] == "spline"
        assert result["point_count"] == 4

    def test_point(self) -> None:
        result = self.catia.sketch_point(25, 25)
        assert result["type"] == "point"
        assert result["position"] == [25, 25]

    def test_no_sketch_raises(self, catia_with_part: CATIAConnection) -> None:
        catia_with_part._active_sketch = None
        with pytest.raises(RuntimeError, match="No active sketch"):
            catia_with_part.sketch_line(0, 0, 10, 10)


class TestSketchConstraints:
    @pytest.fixture(autouse=True)
    def _open_sketch(self, catia_with_part: CATIAConnection) -> None:
        self.catia = catia_with_part
        self.catia.create_sketch("XY")
        self.catia.sketch_line(0, 0, 100, 0)
        self.catia.sketch_line(100, 0, 100, 50)

    def test_add_constraint(self) -> None:
        result = self.catia.sketch_constraint("perpendicular", ["line_1", "line_2"])
        assert result["type"] == "perpendicular"

    def test_dimensional_constraint(self) -> None:
        result = self.catia.sketch_constraint("length", ["line_1"], value=100.0)
        assert result["value"] == 100.0

    def test_fillet(self) -> None:
        result = self.catia.sketch_fillet("line_1", "line_2", 5.0)
        assert result["type"] == "fillet_2d"
        assert result["radius"] == 5.0

    def test_trim(self) -> None:
        result = self.catia.sketch_trim("line_1", 50, 0)
        assert result["status"] == "trimmed"
