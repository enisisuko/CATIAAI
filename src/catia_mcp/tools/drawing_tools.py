"""MCP tools for CATIA Drawing/Drafting operations."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.catia.connection import get_catia


def register(mcp: FastMCP) -> None:
    """Register all drawing/drafting tools with the MCP server."""

    @mcp.tool()
    def create_front_view(
        source_document: str | None = None, sheet_name: str | None = None
    ) -> dict[str, Any]:
        """Create a front view projection on a drawing sheet.
        Args:
            source_document: Path to the 3D part/assembly to project.
            sheet_name: Target sheet name. Uses first sheet if not specified.
        """
        return get_catia().create_view("Front", source_document, sheet_name)

    @mcp.tool()
    def create_projection_view(
        direction: str = "right",
        source_document: str | None = None,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """Create a projection view from a front view.
        Args:
            direction: Projection direction - 'right', 'left', 'top', 'bottom'.
            source_document: Source 3D document path.
            sheet_name: Target sheet name.
        """
        return get_catia().create_view(
            "Projection", source_document, sheet_name, direction=direction
        )

    @mcp.tool()
    def create_section_view(
        plane: str = "XZ",
        source_document: str | None = None,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """Create a section/cross-section view.
        Args:
            plane: Cutting plane definition.
            source_document: Source 3D document path.
            sheet_name: Target sheet name.
        """
        return get_catia().create_view("Section", source_document, sheet_name, plane=plane)

    @mcp.tool()
    def create_detail_view(
        center_x: float,
        center_y: float,
        radius: float,
        source_document: str | None = None,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """Create a detail (zoomed-in) view.
        Args:
            center_x, center_y: Center of the detail circle.
            radius: Radius of the detail circle (mm).
            source_document: Source 3D document path.
            sheet_name: Target sheet name.
        """
        return get_catia().create_view(
            "Detail",
            source_document,
            sheet_name,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
        )

    @mcp.tool()
    def create_isometric_view(
        source_document: str | None = None, sheet_name: str | None = None
    ) -> dict[str, Any]:
        """Create an isometric (3D) view on a drawing sheet.
        Args:
            source_document: Source 3D document path.
            sheet_name: Target sheet name.
        """
        return get_catia().create_view("Isometric", source_document, sheet_name)

    @mcp.tool()
    def add_dimension(
        view_name: str,
        dimension_type: str,
        elements: list[str],
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """Add a dimension annotation to a drawing view.
        Args:
            view_name: Target view name (e.g., 'FrontView.1').
            dimension_type: 'distance', 'length', 'radius', 'diameter', 'angle'.
            elements: Elements to dimension (e.g., ['Edge.1', 'Edge.2']).
            sheet_name: Sheet name.
        """
        return get_catia().add_drawing_dimension(view_name, dimension_type, elements, sheet_name)

    @mcp.tool()
    def add_text_annotation(
        view_name: str,
        text: str,
        x: float,
        y: float,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """Add a text annotation to a drawing view.
        Args:
            view_name: Target view name.
            text: Annotation text content.
            x, y: Position on the drawing (mm).
            sheet_name: Sheet name.
        """
        return get_catia().add_annotation(view_name, text, x, y, sheet_name)
