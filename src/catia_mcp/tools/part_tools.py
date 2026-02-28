"""MCP tools for CATIA Part Design operations."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.catia.connection import get_catia


def register(mcp: FastMCP) -> None:
    """Register all part design tools with the MCP server."""

    @mcp.tool()
    def create_pad(
        sketch_name: str,
        depth: float,
        direction: str = "normal",
        symmetric: bool = False,
        body_name: str | None = None,
    ) -> dict[str, Any]:
        """Extrude a sketch profile to create a solid pad.
        Args:
            sketch_name: Name of the sketch to extrude (e.g., 'Sketch.1').
            depth: Extrusion depth in mm.
            direction: 'normal' (default), 'reverse', or 'both'.
            symmetric: If True, extrude equally in both directions.
            body_name: Target body name. Uses PartBody if not specified.
        """
        return get_catia().create_pad(sketch_name, depth, direction, symmetric, body_name)

    @mcp.tool()
    def create_pocket(
        sketch_name: str,
        depth: float,
        direction: str = "normal",
        body_name: str | None = None,
    ) -> dict[str, Any]:
        """Cut material by extruding a sketch profile (pocket/slot).
        Args:
            sketch_name: Name of the sketch defining the cut profile.
            depth: Cut depth in mm.
            direction: 'normal', 'reverse', or 'up_to_next'.
            body_name: Target body name.
        """
        return get_catia().create_pocket(sketch_name, depth, direction, body_name)

    @mcp.tool()
    def create_shaft(
        sketch_name: str,
        angle: float = 360.0,
        axis: str = "sketch_axis",
        body_name: str | None = None,
    ) -> dict[str, Any]:
        """Revolve a sketch profile around an axis to create a solid.
        Args:
            sketch_name: Sketch to revolve.
            angle: Revolution angle in degrees (default 360 = full revolution).
            axis: Revolution axis - 'sketch_axis' or element name.
            body_name: Target body name.
        """
        return get_catia().create_shaft(sketch_name, angle, axis, body_name)

    @mcp.tool()
    def create_groove(
        sketch_name: str,
        angle: float = 360.0,
        axis: str = "sketch_axis",
        body_name: str | None = None,
    ) -> dict[str, Any]:
        """Cut material by revolving a sketch profile (groove).
        Args:
            sketch_name: Sketch defining the cut profile.
            angle: Revolution angle in degrees.
            axis: Revolution axis.
            body_name: Target body name.
        """
        return get_catia().create_groove(sketch_name, angle, axis, body_name)

    @mcp.tool()
    def create_fillet(
        edges: list[str],
        radius: float,
        body_name: str | None = None,
    ) -> dict[str, Any]:
        """Add fillet (rounded edge) to one or more edges.
        Args:
            edges: List of edge names to fillet.
            radius: Fillet radius in mm.
            body_name: Target body name.
        """
        return get_catia().create_fillet(edges, radius, body_name)

    @mcp.tool()
    def create_chamfer(
        edges: list[str],
        distance: float,
        angle: float = 45.0,
        body_name: str | None = None,
    ) -> dict[str, Any]:
        """Add chamfer to one or more edges.
        Args:
            edges: List of edge names to chamfer.
            distance: Chamfer distance in mm.
            angle: Chamfer angle in degrees (default 45).
            body_name: Target body name.
        """
        return get_catia().create_chamfer(edges, distance, angle, body_name)

    @mcp.tool()
    def create_shell(
        thickness: float,
        faces_to_remove: list[str] | None = None,
        body_name: str | None = None,
    ) -> dict[str, Any]:
        """Hollow out a solid, keeping a shell of specified thickness.
        Args:
            thickness: Shell wall thickness in mm.
            faces_to_remove: Faces to remove (open). If None, creates closed shell.
            body_name: Target body name.
        """
        return get_catia().create_shell(thickness, faces_to_remove, body_name)

    @mcp.tool()
    def create_hole(
        x: float,
        y: float,
        diameter: float,
        depth: float,
        hole_type: str = "simple",
        body_name: str | None = None,
    ) -> dict[str, Any]:
        """Create a hole at specified coordinates.
        Args:
            x, y: Hole center position in mm.
            diameter: Hole diameter in mm.
            depth: Hole depth in mm.
            hole_type: 'simple', 'tapered', 'counterbored', 'countersunk', 'threaded'.
            body_name: Target body name.
        """
        return get_catia().create_hole(x, y, diameter, depth, hole_type, body_name)

    @mcp.tool()
    def create_pattern_rectangular(
        feature_name: str,
        dir1_count: int,
        dir1_spacing: float,
        dir2_count: int = 1,
        dir2_spacing: float = 0.0,
        body_name: str | None = None,
    ) -> dict[str, Any]:
        """Create a rectangular pattern of a feature.
        Args:
            feature_name: Feature to pattern.
            dir1_count: Number of instances in direction 1.
            dir1_spacing: Spacing in direction 1 (mm).
            dir2_count: Number of instances in direction 2.
            dir2_spacing: Spacing in direction 2 (mm).
            body_name: Target body name.
        """
        return get_catia().create_pattern_rectangular(
            feature_name, dir1_count, dir1_spacing, dir2_count, dir2_spacing, body_name
        )

    @mcp.tool()
    def create_pattern_circular(
        feature_name: str,
        count: int,
        angle_spacing: float = 0.0,
        full_circle: bool = True,
        body_name: str | None = None,
    ) -> dict[str, Any]:
        """Create a circular pattern of a feature.
        Args:
            feature_name: Feature to pattern.
            count: Number of instances.
            angle_spacing: Angle between instances (degrees). Ignored if full_circle=True.
            full_circle: If True, distribute evenly around 360 degrees.
            body_name: Target body name.
        """
        return get_catia().create_pattern_circular(
            feature_name, count, angle_spacing, full_circle, body_name
        )

    @mcp.tool()
    def create_mirror(
        feature_name: str,
        plane: str = "XY",
        body_name: str | None = None,
    ) -> dict[str, Any]:
        """Mirror a feature about a plane.
        Args:
            feature_name: Feature to mirror.
            plane: Mirror plane - 'XY', 'YZ', 'XZ', or named plane.
            body_name: Target body name.
        """
        return get_catia().create_mirror(feature_name, plane, body_name)

    @mcp.tool()
    def create_thickness(
        faces: list[str],
        offset: float,
        body_name: str | None = None,
    ) -> dict[str, Any]:
        """Add thickness/offset to faces.
        Args:
            faces: List of face names.
            offset: Thickness offset in mm.
            body_name: Target body name.
        """
        return get_catia().create_thickness(faces, offset, body_name)

    @mcp.tool()
    def add_body(name: str | None = None) -> dict[str, str]:
        """Add a new body to the part.
        Args:
            name: Optional body name.
        """
        return get_catia().add_body(name)

    @mcp.tool()
    def boolean_operation(body1: str, body2: str, operation: str = "add") -> dict[str, Any]:
        """Perform a boolean operation between two bodies.
        Args:
            body1: First body name.
            body2: Second body name.
            operation: 'add' (union), 'remove' (subtract), or 'intersect'.
        """
        return get_catia().boolean_operation(body1, body2, operation)
