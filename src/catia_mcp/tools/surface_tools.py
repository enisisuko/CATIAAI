"""MCP tools for CATIA Generative Shape Design (surface) operations."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.catia.connection import get_catia


def register(mcp: FastMCP) -> None:
    """Register all surface design tools with the MCP server."""

    @mcp.tool()
    def create_extrude_surface(
        sketch_name: str,
        depth: float,
        direction: str = "normal",
        hybrid_body: str | None = None,
    ) -> dict[str, Any]:
        """Extrude a sketch profile or curve to create a surface.
        Args:
            sketch_name: Sketch or curve to extrude.
            depth: Extrusion distance in mm.
            direction: Extrusion direction.
            hybrid_body: Target geometrical set name.
        """
        return get_catia().create_surface(
            "Extrude", sketch_name, hybrid_body, depth=depth, direction=direction
        )

    @mcp.tool()
    def create_revolve_surface(
        sketch_name: str,
        angle: float = 360.0,
        axis: str = "sketch_axis",
        hybrid_body: str | None = None,
    ) -> dict[str, Any]:
        """Revolve a profile or curve around an axis to create a surface.
        Args:
            sketch_name: Profile to revolve.
            angle: Revolution angle in degrees.
            axis: Revolution axis.
            hybrid_body: Target geometrical set.
        """
        return get_catia().create_surface(
            "Revolve", sketch_name, hybrid_body, angle=angle, axis=axis
        )

    @mcp.tool()
    def create_sweep_surface(
        profile: str,
        guide: str,
        hybrid_body: str | None = None,
    ) -> dict[str, Any]:
        """Create a surface by sweeping a profile along a guide curve.
        Args:
            profile: Profile sketch/curve name.
            guide: Guide curve name.
            hybrid_body: Target geometrical set.
        """
        return get_catia().create_surface("Sweep", profile, hybrid_body, guide=guide)

    @mcp.tool()
    def create_fill_surface(
        boundary_curves: list[str],
        hybrid_body: str | None = None,
    ) -> dict[str, Any]:
        """Create a fill surface bounded by curves.
        Args:
            boundary_curves: List of boundary curve names forming a closed contour.
            hybrid_body: Target geometrical set.
        """
        return get_catia().create_surface("Fill", None, hybrid_body, boundaries=boundary_curves)

    @mcp.tool()
    def create_loft_surface(
        sections: list[str],
        guides: list[str] | None = None,
        hybrid_body: str | None = None,
    ) -> dict[str, Any]:
        """Create a multi-section (loft) surface through several profiles.
        Args:
            sections: List of section sketch/curve names.
            guides: Optional guide curves for shape control.
            hybrid_body: Target geometrical set.
        """
        return get_catia().create_surface(
            "Loft", None, hybrid_body, sections=sections, guides=guides or []
        )

    @mcp.tool()
    def create_offset_surface(
        surface: str,
        offset: float,
        hybrid_body: str | None = None,
    ) -> dict[str, Any]:
        """Create an offset copy of a surface.
        Args:
            surface: Source surface name.
            offset: Offset distance in mm (positive = outward).
            hybrid_body: Target geometrical set.
        """
        return get_catia().create_surface(
            "Offset", None, hybrid_body, source=surface, offset=offset
        )

    @mcp.tool()
    def create_blend_surface(
        curve1: str,
        support1: str,
        curve2: str,
        support2: str,
        hybrid_body: str | None = None,
    ) -> dict[str, Any]:
        """Create a blend surface between two curves on supports.
        Args:
            curve1: First boundary curve.
            support1: First support surface.
            curve2: Second boundary curve.
            support2: Second support surface.
            hybrid_body: Target geometrical set.
        """
        return get_catia().create_surface(
            "Blend",
            None,
            hybrid_body,
            curve1=curve1,
            support1=support1,
            curve2=curve2,
            support2=support2,
        )

    @mcp.tool()
    def trim_surface(
        elements: list[str],
        hybrid_body: str | None = None,
    ) -> dict[str, Any]:
        """Trim surfaces or curves using other elements.
        Args:
            elements: List of elements to trim (the first element is trimmed by the others).
            hybrid_body: Target geometrical set.
        """
        return get_catia().surface_operation("Trim", elements, hybrid_body)

    @mcp.tool()
    def split_surface(
        elements: list[str],
        hybrid_body: str | None = None,
    ) -> dict[str, Any]:
        """Split a surface or solid using a cutting element.
        Args:
            elements: [element_to_split, cutting_element].
            hybrid_body: Target geometrical set.
        """
        return get_catia().surface_operation("Split", elements, hybrid_body)

    @mcp.tool()
    def join_surfaces(
        surfaces: list[str],
        hybrid_body: str | None = None,
    ) -> dict[str, Any]:
        """Join multiple surfaces into one.
        Args:
            surfaces: List of surface names to join.
            hybrid_body: Target geometrical set.
        """
        return get_catia().surface_operation("Join", surfaces, hybrid_body)
