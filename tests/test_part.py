"""Tests for CATIA Part Design operations."""

from __future__ import annotations

import pytest

from catia_mcp.catia.connection import CATIAConnection


@pytest.fixture
def part_with_sketch(catia_with_part: CATIAConnection) -> CATIAConnection:
    """Part with a completed sketch ready for feature creation."""
    catia_with_part.create_sketch("XY")
    catia_with_part.sketch_rectangle(0, 0, 100, 50)
    catia_with_part.close_sketch()
    return catia_with_part


class TestPadPocket:
    def test_create_pad(self, part_with_sketch: CATIAConnection) -> None:
        result = part_with_sketch.create_pad("Sketch.1", 30.0)
        assert result["name"] == "Pad.1"
        assert result["depth"] == 30.0

    def test_create_pocket(self, part_with_sketch: CATIAConnection) -> None:
        part_with_sketch.create_pad("Sketch.1", 30.0)
        part_with_sketch.create_sketch("XY")
        part_with_sketch.sketch_circle(50, 25, 10)
        part_with_sketch.close_sketch()
        result = part_with_sketch.create_pocket("Sketch.2", 15.0)
        assert result["name"] == "Pocket.1"

    def test_pad_missing_sketch_raises(self, catia_with_part: CATIAConnection) -> None:
        with pytest.raises(RuntimeError, match="Sketch.*not found"):
            catia_with_part.create_pad("NonExistent", 10.0)


class TestRevolve:
    def test_shaft(self, part_with_sketch: CATIAConnection) -> None:
        result = part_with_sketch.create_shaft("Sketch.1", 360.0)
        assert result["name"] == "Shaft.1"
        assert result["angle"] == 360.0

    def test_groove(self, part_with_sketch: CATIAConnection) -> None:
        part_with_sketch.create_shaft("Sketch.1", 360.0)
        part_with_sketch.create_sketch("XZ")
        part_with_sketch.sketch_rectangle(20, 0, 10, 5)
        part_with_sketch.close_sketch()
        result = part_with_sketch.create_groove("Sketch.2", 360.0)
        assert result["name"] == "Groove.1"


class TestDressUp:
    def test_fillet(self, part_with_sketch: CATIAConnection) -> None:
        part_with_sketch.create_pad("Sketch.1", 30.0)
        result = part_with_sketch.create_fillet(["Edge.1", "Edge.2"], 5.0)
        assert result["name"] == "EdgeFillet.1"
        assert result["radius"] == 5.0

    def test_chamfer(self, part_with_sketch: CATIAConnection) -> None:
        part_with_sketch.create_pad("Sketch.1", 30.0)
        result = part_with_sketch.create_chamfer(["Edge.1"], 3.0, 45.0)
        assert result["name"] == "Chamfer.1"

    def test_shell(self, part_with_sketch: CATIAConnection) -> None:
        part_with_sketch.create_pad("Sketch.1", 30.0)
        result = part_with_sketch.create_shell(2.0, ["Face.Top"])
        assert result["name"] == "Shell.1"
        assert result["thickness"] == 2.0


class TestHoleAndPattern:
    def test_hole(self, part_with_sketch: CATIAConnection) -> None:
        part_with_sketch.create_pad("Sketch.1", 30.0)
        result = part_with_sketch.create_hole(50, 25, 10, 20, "threaded")
        assert result["name"] == "Hole.1"
        assert result["type"] == "threaded"

    def test_rectangular_pattern(self, part_with_sketch: CATIAConnection) -> None:
        part_with_sketch.create_pad("Sketch.1", 30.0)
        part_with_sketch.create_hole(10, 10, 5, 15)
        result = part_with_sketch.create_pattern_rectangular("Hole.1", 3, 20.0, 2, 15.0)
        assert result["total_instances"] == 6

    def test_circular_pattern(self, part_with_sketch: CATIAConnection) -> None:
        part_with_sketch.create_pad("Sketch.1", 30.0)
        part_with_sketch.create_hole(40, 25, 5, 15)
        result = part_with_sketch.create_pattern_circular("Hole.1", 6)
        assert result["instances"] == 6
        assert result["spacing"] == 60.0

    def test_mirror(self, part_with_sketch: CATIAConnection) -> None:
        part_with_sketch.create_pad("Sketch.1", 30.0)
        result = part_with_sketch.create_mirror("Pad.1", "YZ")
        assert result["name"] == "Mirror.1"


class TestBodyOperations:
    def test_add_body(self, catia_with_part: CATIAConnection) -> None:
        result = catia_with_part.add_body("SecondBody")
        assert result["name"] == "SecondBody"
        assert len(catia_with_part.active_document.bodies) == 2

    def test_boolean_operation(self, catia_with_part: CATIAConnection) -> None:
        result = catia_with_part.boolean_operation("PartBody", "Body.2", "remove")
        assert result["operation"] == "remove"
