"""MCP tools for CATIA measurement operations."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.catia.connection import get_catia


def register(mcp: FastMCP) -> None:
    """Register all measurement tools with the MCP server."""

    @mcp.tool()
    def measure_distance(element1: str, element2: str) -> dict[str, Any]:
        """Measure the minimum distance between two elements.
        Args:
            element1: First element name (face, edge, vertex, etc.).
            element2: Second element name.
        Returns:
            Distance in mm.
        """
        return get_catia().measure_distance(element1, element2)

    @mcp.tool()
    def measure_angle(element1: str, element2: str) -> dict[str, Any]:
        """Measure the angle between two elements (planes, lines, edges).
        Args:
            element1: First element name.
            element2: Second element name.
        Returns:
            Angle in degrees.
        """
        return get_catia().measure_angle(element1, element2)

    @mcp.tool()
    def measure_properties(element: str) -> dict[str, Any]:
        """Measure geometric properties of an element: area, volume,
        center of gravity, and moments of inertia.
        Args:
            element: Element or body name to measure.
        Returns:
            Area (mm²), volume (mm³), center of gravity, etc.
        """
        return get_catia().measure_properties(element)
