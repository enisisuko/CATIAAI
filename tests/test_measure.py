"""Tests for CATIA Measurement operations."""

from __future__ import annotations

from catia_mcp.catia.connection import CATIAConnection


class TestMeasurement:
    def test_distance(self, catia_with_part: CATIAConnection) -> None:
        result = catia_with_part.measure_distance("Face.1", "Face.2")
        assert "distance" in result
        assert result["unit"] == "mm"

    def test_angle(self, catia_with_part: CATIAConnection) -> None:
        result = catia_with_part.measure_angle("Plane.1", "Plane.2")
        assert "angle" in result
        assert result["unit"] == "deg"

    def test_properties(self, catia_with_part: CATIAConnection) -> None:
        result = catia_with_part.measure_properties("PartBody")
        assert "area" in result
        assert "volume" in result
        assert "center_of_gravity" in result
