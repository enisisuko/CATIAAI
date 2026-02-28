"""Tests for CATIA Drawing operations."""

from __future__ import annotations

import pytest

from catia_mcp.catia.connection import CATIAConnection


class TestDrawingViews:
    def test_create_front_view(self, catia_with_drawing: CATIAConnection) -> None:
        result = catia_with_drawing.create_view("Front", "test.CATPart")
        assert result["type"] == "Front"
        assert result["sheet"] == "Sheet.1"

    def test_create_projection_view(self, catia_with_drawing: CATIAConnection) -> None:
        catia_with_drawing.create_view("Front")
        result = catia_with_drawing.create_view("Projection", direction="right")
        assert result["type"] == "Projection"

    def test_create_section_view(self, catia_with_drawing: CATIAConnection) -> None:
        result = catia_with_drawing.create_view("Section", plane="XZ")
        assert result["type"] == "Section"

    def test_create_detail_view(self, catia_with_drawing: CATIAConnection) -> None:
        result = catia_with_drawing.create_view("Detail", center_x=100, center_y=100, radius=30)
        assert result["type"] == "Detail"

    def test_create_isometric(self, catia_with_drawing: CATIAConnection) -> None:
        result = catia_with_drawing.create_view("Isometric")
        assert result["type"] == "Isometric"


class TestDrawingAnnotations:
    @pytest.fixture(autouse=True)
    def _setup(self, catia_with_drawing: CATIAConnection) -> None:
        self.catia = catia_with_drawing
        self.catia.create_view("Front")

    def test_add_dimension(self) -> None:
        result = self.catia.add_drawing_dimension("FrontView.1", "distance", ["Edge.1", "Edge.2"])
        assert result["type"] == "distance"

    def test_add_annotation(self) -> None:
        result = self.catia.add_annotation("FrontView.1", "Surface finish Ra 1.6", 50, 30)
        assert result["text"] == "Surface finish Ra 1.6"

    def test_dimension_nonexistent_view_raises(self) -> None:
        with pytest.raises(RuntimeError, match="View.*not found"):
            self.catia.add_drawing_dimension("NoView", "length", ["Edge.1"])
