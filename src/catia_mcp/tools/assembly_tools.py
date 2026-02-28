"""MCP tools for CATIA Assembly Design operations."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.catia.connection import get_catia


def register(mcp: FastMCP) -> None:
    """Register all assembly tools with the MCP server."""

    @mcp.tool()
    def insert_component(document_path: str, name: str | None = None) -> dict[str, Any]:
        """Insert a component into the active assembly.
        Args:
            document_path: Path to the .CATPart or .CATProduct file.
            name: Optional instance name for the component.
        """
        return get_catia().insert_component(document_path, name)

    @mcp.tool()
    def add_coincidence_constraint(
        component1: str,
        element1: str,
        component2: str,
        element2: str,
    ) -> dict[str, Any]:
        """Add a coincidence constraint between two assembly elements.
        Makes planes coplanar, axes coaxial, or points coincident.
        Args:
            component1: First component name.
            element1: Element on first component (e.g., 'Face.1', 'Axis.1').
            component2: Second component name.
            element2: Element on second component.
        """
        return get_catia().add_assembly_constraint(
            "Coincidence", component1, element1, component2, element2
        )

    @mcp.tool()
    def add_contact_constraint(
        component1: str,
        element1: str,
        component2: str,
        element2: str,
    ) -> dict[str, Any]:
        """Add a surface contact constraint between two components.
        Args:
            component1: First component name.
            element1: Face on first component.
            component2: Second component name.
            element2: Face on second component.
        """
        return get_catia().add_assembly_constraint(
            "Contact", component1, element1, component2, element2
        )

    @mcp.tool()
    def add_offset_constraint(
        component1: str,
        element1: str,
        component2: str,
        element2: str,
        offset: float = 0.0,
    ) -> dict[str, Any]:
        """Add an offset constraint between two planar elements.
        Args:
            component1: First component name.
            element1: Plane/face on first component.
            component2: Second component name.
            element2: Plane/face on second component.
            offset: Distance offset in mm.
        """
        return get_catia().add_assembly_constraint(
            "Offset", component1, element1, component2, element2, offset
        )

    @mcp.tool()
    def add_angle_constraint(
        component1: str,
        element1: str,
        component2: str,
        element2: str,
        angle: float = 0.0,
    ) -> dict[str, Any]:
        """Add an angle constraint between two elements.
        Args:
            component1: First component name.
            element1: Element on first component.
            component2: Second component name.
            element2: Element on second component.
            angle: Angle in degrees.
        """
        return get_catia().add_assembly_constraint(
            "Angle", component1, element1, component2, element2, angle
        )

    @mcp.tool()
    def fix_component(component_name: str) -> dict[str, str]:
        """Fix a component in place (remove all degrees of freedom).
        Args:
            component_name: Name of the component to fix.
        """
        return get_catia().fix_component(component_name)

    @mcp.tool()
    def move_component(component_name: str, x: float, y: float, z: float) -> dict[str, Any]:
        """Move a component to a new position.
        Args:
            component_name: Name of the component.
            x, y, z: New position coordinates in mm.
        """
        return get_catia().move_component(component_name, x, y, z)

    @mcp.tool()
    def get_bill_of_materials() -> dict[str, Any]:
        """Get the Bill of Materials (BOM) for the active assembly.
        Returns list of all components with quantities."""
        return get_catia().get_bom()
