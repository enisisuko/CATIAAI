"""MCP tools for CATIA system/document operations."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.catia.connection import get_catia


def register(mcp: FastMCP) -> None:
    """Register all system/document tools with the MCP server."""

    @mcp.tool()
    def connect_catia() -> dict[str, Any]:
        """Connect to a running CATIA instance.
        Must be called before any other CATIA operation.
        Automatically uses mock mode when CATIA is not available."""
        return get_catia().connect()

    @mcp.tool()
    def get_catia_status() -> dict[str, Any]:
        """Get the current CATIA connection status."""
        catia = get_catia()
        return {
            "connected": catia.connected,
            "mock_mode": catia.is_mock,
            "active_document": catia.active_document.name if catia.active_document else None,
            "active_sketch": catia.active_sketch.name if catia.active_sketch else None,
        }

    @mcp.tool()
    def new_part(name: str | None = None) -> dict[str, Any]:
        """Create a new CATIA Part document for 3D modeling.
        Args:
            name: Optional name for the part. Auto-generated if not provided.
        """
        from catia_mcp.catia.connection import DocumentType

        return get_catia().new_document(DocumentType.PART, name)

    @mcp.tool()
    def new_assembly(name: str | None = None) -> dict[str, Any]:
        """Create a new CATIA Assembly (Product) document.
        Args:
            name: Optional name for the assembly.
        """
        from catia_mcp.catia.connection import DocumentType

        return get_catia().new_document(DocumentType.PRODUCT, name)

    @mcp.tool()
    def new_drawing(name: str | None = None) -> dict[str, Any]:
        """Create a new CATIA Drawing document for 2D drafting.
        Args:
            name: Optional name for the drawing.
        """
        from catia_mcp.catia.connection import DocumentType

        return get_catia().new_document(DocumentType.DRAWING, name)

    @mcp.tool()
    def open_document(path: str) -> dict[str, Any]:
        """Open an existing CATIA document (.CATPart, .CATProduct, .CATDrawing).
        Args:
            path: Full file path to the document.
        """
        return get_catia().open_document(path)

    @mcp.tool()
    def save_document(path: str | None = None) -> dict[str, str]:
        """Save the active document. Use path for Save As.
        Args:
            path: Optional new file path for Save As.
        """
        return get_catia().save_document(path)

    @mcp.tool()
    def close_document() -> dict[str, str]:
        """Close the active document."""
        return get_catia().close_document()

    @mcp.tool()
    def get_document_info() -> dict[str, Any]:
        """Get detailed information about the active document including
        bodies, sketches, features, parameters, components, or sheets."""
        return get_catia().get_document_info()

    @mcp.tool()
    def get_feature_tree() -> dict[str, Any]:
        """Get the complete specification/feature tree of the active document.
        Shows all bodies, features, sketches, components, or views."""
        return get_catia().get_feature_tree()

    @mcp.tool()
    def get_parameters() -> dict[str, Any]:
        """Get all user-defined parameters of the active document."""
        return get_catia().get_parameters()

    @mcp.tool()
    def set_parameter(name: str, value: float | str) -> dict[str, Any]:
        """Set a parameter value in the active document.
        Args:
            name: Parameter name (e.g., 'Length', 'Radius').
            value: New value for the parameter.
        """
        return get_catia().set_parameter(name, value)

    @mcp.tool()
    def undo() -> dict[str, str]:
        """Undo the last operation in CATIA."""
        return get_catia().undo()

    @mcp.tool()
    def redo() -> dict[str, str]:
        """Redo the last undone operation in CATIA."""
        return get_catia().redo()

    @mcp.tool()
    def execute_vba_macro(code: str, language: str = "VBScript") -> dict[str, Any]:
        """Execute a VBA/VBScript macro in CATIA. Use for operations
        not covered by other tools.
        Args:
            code: The macro code to execute.
            language: Script language, 'VBScript' or 'CATScript'.
        """
        return get_catia().execute_macro(code, language)
