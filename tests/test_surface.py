"""Tests for CATIA Surface Design operations."""

from __future__ import annotations

from catia_mcp.catia.connection import CATIAConnection


class TestSurfaces:
    def test_create_extrude(self, catia_with_part: CATIAConnection) -> None:
        catia_with_part.create_sketch("XY")
        catia_with_part.sketch_line(0, 0, 100, 0)
        catia_with_part.close_sketch()
        result = catia_with_part.create_surface("Extrude", "Sketch.1", depth=50)
        assert result["type"] == "Extrude"

    def test_create_revolve(self, catia_with_part: CATIAConnection) -> None:
        catia_with_part.create_sketch("XZ")
        catia_with_part.sketch_line(10, 0, 10, 50)
        catia_with_part.close_sketch()
        result = catia_with_part.create_surface("Revolve", "Sketch.1", angle=360)
        assert result["type"] == "Revolve"

    def test_create_loft(self, catia_with_part: CATIAConnection) -> None:
        result = catia_with_part.create_surface("Loft", sections=["Section.1", "Section.2"])
        assert result["type"] == "Loft"

    def test_trim(self, catia_with_part: CATIAConnection) -> None:
        result = catia_with_part.surface_operation("Trim", ["Surface.1", "Plane.1"])
        assert result["operation"] == "Trim"

    def test_split(self, catia_with_part: CATIAConnection) -> None:
        result = catia_with_part.surface_operation("Split", ["Body", "Plane.1"])
        assert result["operation"] == "Split"

    def test_join(self, catia_with_part: CATIAConnection) -> None:
        result = catia_with_part.surface_operation("Join", ["Surface.1", "Surface.2"])
        assert result["operation"] == "Join"
