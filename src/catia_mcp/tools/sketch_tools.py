"""MCP tools for CATIA Sketcher operations."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.catia.connection import get_catia


def register(mcp: FastMCP) -> None:
    """Register all sketch tools with the MCP server."""

    @mcp.tool()
    def create_sketch(plane: str = "XY") -> dict[str, Any]:
        """Create a new sketch on a reference plane and enter sketch editing mode.
        Args:
            plane: Reference plane - 'XY', 'YZ', 'XZ', or a named plane/face.
        """
        return get_catia().create_sketch(plane)

    @mcp.tool()
    def close_sketch() -> dict[str, str]:
        """Exit sketch editing mode and finalize the current sketch."""
        return get_catia().close_sketch()

    @mcp.tool()
    def sketch_line(x1: float, y1: float, x2: float, y2: float) -> dict[str, Any]:
        """Draw a line in the active sketch.
        Args:
            x1, y1: Start point coordinates (mm).
            x2, y2: End point coordinates (mm).
        """
        return get_catia().sketch_line(x1, y1, x2, y2)

    @mcp.tool()
    def sketch_circle(cx: float, cy: float, radius: float) -> dict[str, Any]:
        """Draw a circle in the active sketch.
        Args:
            cx, cy: Center point coordinates (mm).
            radius: Circle radius (mm).
        """
        return get_catia().sketch_circle(cx, cy, radius)

    @mcp.tool()
    def sketch_rectangle(x: float, y: float, width: float, height: float) -> dict[str, Any]:
        """Draw a rectangle in the active sketch.
        Args:
            x, y: Bottom-left corner coordinates (mm).
            width: Rectangle width (mm).
            height: Rectangle height (mm).
        """
        return get_catia().sketch_rectangle(x, y, width, height)

    @mcp.tool()
    def sketch_arc(
        cx: float, cy: float, radius: float, start_angle: float, end_angle: float
    ) -> dict[str, Any]:
        """Draw an arc in the active sketch.
        Args:
            cx, cy: Center coordinates (mm).
            radius: Arc radius (mm).
            start_angle: Start angle in degrees.
            end_angle: End angle in degrees.
        """
        return get_catia().sketch_arc(cx, cy, radius, start_angle, end_angle)

    @mcp.tool()
    def sketch_spline(points: list[list[float]]) -> dict[str, Any]:
        """Draw a spline through control points in the active sketch.
        Args:
            points: List of [x, y] coordinate pairs, e.g., [[0,0], [10,5], [20,0]].
        """
        return get_catia().sketch_spline([(p[0], p[1]) for p in points])

    @mcp.tool()
    def sketch_point(x: float, y: float) -> dict[str, Any]:
        """Create a construction point in the active sketch.
        Args:
            x, y: Point coordinates (mm).
        """
        return get_catia().sketch_point(x, y)

    @mcp.tool()
    def sketch_constraint(
        constraint_type: str,
        elements: list[str],
        value: float | None = None,
    ) -> dict[str, Any]:
        """Add a geometric or dimensional constraint in the active sketch.
        Args:
            constraint_type: Type of constraint. Geometric: 'horizontal', 'vertical',
                'perpendicular', 'parallel', 'tangent', 'coincident', 'concentric',
                'equal', 'symmetric', 'fix'. Dimensional: 'distance', 'length',
                'angle', 'radius', 'diameter'.
            elements: List of element IDs to constrain (e.g., ['line_1', 'line_2']).
            value: Numeric value for dimensional constraints (mm or degrees).
        """
        return get_catia().sketch_constraint(constraint_type, elements, value)

    @mcp.tool()
    def sketch_fillet(element1: str, element2: str, radius: float) -> dict[str, Any]:
        """Create a 2D fillet between two sketch elements.
        Args:
            element1: First element ID.
            element2: Second element ID.
            radius: Fillet radius (mm).
        """
        return get_catia().sketch_fillet(element1, element2, radius)

    @mcp.tool()
    def sketch_trim(element: str, point_x: float, point_y: float) -> dict[str, Any]:
        """Trim a sketch element at a specified point.
        Args:
            element: Element ID to trim.
            point_x, point_y: Point near the segment to keep.
        """
        return get_catia().sketch_trim(element, point_x, point_y)
