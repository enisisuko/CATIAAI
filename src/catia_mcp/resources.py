"""MCP Resources for exposing CATIA state to LLMs.

Resources provide read-only context that LLM clients can request.
Following FastMCP best practices for resource definition.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.catia.connection import get_catia

logger = logging.getLogger(__name__)


def register(mcp: FastMCP) -> None:
    """Register all MCP resources."""

    @mcp.resource("catia://status")
    def catia_status() -> str:
        """Current CATIA connection status, active document, and mode."""
        c = get_catia()
        data = {
            "connected": c.connected,
            "mock_mode": c.is_mock,
            "active_document": c.active_document.name if c.active_document else None,
            "active_document_type": (
                c.active_document.doc_type.value if c.active_document else None
            ),
            "active_sketch": c.active_sketch.name if c.active_sketch else None,
        }
        return json.dumps(data, indent=2)

    @mcp.resource("catia://document/info")
    def document_info() -> str:
        """Detailed information about the active CATIA document."""
        c = get_catia()
        if not c.connected or c.active_document is None:
            return json.dumps({"error": "No active document"})
        return json.dumps(c.get_document_info(), indent=2)

    @mcp.resource("catia://document/tree")
    def feature_tree() -> str:
        """Complete specification/feature tree of the active document."""
        c = get_catia()
        if not c.connected or c.active_document is None:
            return json.dumps({"error": "No active document"})
        return json.dumps(c.get_feature_tree(), indent=2)

    @mcp.resource("catia://document/parameters")
    def parameters() -> str:
        """All user-defined parameters in the active document."""
        c = get_catia()
        if not c.connected or c.active_document is None:
            return json.dumps({"error": "No active document"})
        return json.dumps(c.get_parameters(), indent=2)

    @mcp.resource("catia://help/tools")
    def tools_reference() -> str:
        """Quick reference of all available CATIA MCP tools organized by category."""
        return json.dumps(
            {
                "categories": {
                    "system": {
                        "description": "Connection and document management",
                        "tools": [
                            "connect_catia",
                            "get_catia_status",
                            "new_part",
                            "new_assembly",
                            "new_drawing",
                            "open_document",
                            "save_document",
                            "close_document",
                            "get_document_info",
                            "get_feature_tree",
                            "get_parameters",
                            "set_parameter",
                            "undo",
                            "redo",
                            "execute_vba_macro",
                        ],
                    },
                    "sketch": {
                        "description": "2D Sketcher operations",
                        "tools": [
                            "create_sketch",
                            "close_sketch",
                            "sketch_line",
                            "sketch_circle",
                            "sketch_rectangle",
                            "sketch_arc",
                            "sketch_spline",
                            "sketch_point",
                            "sketch_constraint",
                            "sketch_fillet",
                            "sketch_trim",
                        ],
                    },
                    "part_design": {
                        "description": "3D Part Design operations",
                        "tools": [
                            "create_pad",
                            "create_pocket",
                            "create_shaft",
                            "create_groove",
                            "create_fillet",
                            "create_chamfer",
                            "create_shell",
                            "create_hole",
                            "create_pattern_rectangular",
                            "create_pattern_circular",
                            "create_mirror",
                            "create_thickness",
                            "add_body",
                            "boolean_operation",
                        ],
                    },
                    "assembly": {
                        "description": "Assembly Design constraints",
                        "tools": [
                            "insert_component",
                            "add_coincidence_constraint",
                            "add_contact_constraint",
                            "add_offset_constraint",
                            "add_angle_constraint",
                            "fix_component",
                            "move_component",
                            "get_bill_of_materials",
                        ],
                    },
                    "drawing": {
                        "description": "2D Drawing / Drafting",
                        "tools": [
                            "create_front_view",
                            "create_projection_view",
                            "create_section_view",
                            "create_detail_view",
                            "create_isometric_view",
                            "add_dimension",
                            "add_text_annotation",
                        ],
                    },
                    "surface": {
                        "description": "Generative Shape Design (surfaces)",
                        "tools": [
                            "create_extrude_surface",
                            "create_revolve_surface",
                            "create_sweep_surface",
                            "create_fill_surface",
                            "create_loft_surface",
                            "create_offset_surface",
                            "create_blend_surface",
                            "trim_surface",
                            "split_surface",
                            "join_surfaces",
                        ],
                    },
                    "measurement": {
                        "description": "Measurement and analysis",
                        "tools": [
                            "measure_distance",
                            "measure_angle",
                            "measure_properties",
                        ],
                    },
                    "vision": {
                        "description": "Screen capture and UI automation",
                        "tools": [
                            "capture_screenshot",
                            "capture_region",
                            "click_at",
                            "double_click_at",
                            "right_click_at",
                            "drag_and_drop",
                            "type_text_input",
                            "press_key",
                            "keyboard_shortcut",
                            "scroll_wheel",
                            "find_on_screen",
                            "get_catia_window_info",
                            "wait_seconds",
                        ],
                    },
                    "smart_ui": {
                        "description": "Intelligent UI automation (pywinauto)",
                        "tools": [
                            "connect_catia_ui",
                            "click_menu_item",
                            "click_toolbar",
                            "interact_dialog",
                            "read_spec_tree_ui",
                            "list_ui_controls",
                            "select_tree_node",
                            "wait_for_dialog_appear",
                        ],
                    },
                    "agent": {
                        "description": "Agent workflow and planning",
                        "tools": [
                            "plan_catia_task",
                            "analyze_current_state",
                            "suggest_next_step",
                            "validate_design",
                            "generate_catscript",
                        ],
                    },
                },
                "total_tools": "90+",
                "workflow": (
                    "1. connect_catia → 2. new_part/open_document → "
                    "3. create_sketch → 4. add geometry → "
                    "5. close_sketch → 6. create features → 7. save_document"
                ),
            },
            indent=2,
        )

    @mcp.resource("catia://help/workflow/{workflow_name}")
    def workflow_guide(workflow_name: str) -> str:
        """Step-by-step workflow guides for common CATIA tasks."""
        workflows: dict[str, Any] = {
            "create_box": {
                "title": "Create a basic box (rectangular solid)",
                "steps": [
                    "1. connect_catia()",
                    "2. new_part(name='MyBox')",
                    "3. create_sketch(plane='XY')",
                    "4. sketch_rectangle(x=-50, y=-25, width=100, height=50)",
                    "5. close_sketch()",
                    "6. create_pad(sketch_name='Sketch.1', depth=30)",
                    "7. save_document(path='MyBox.CATPart')",
                ],
            },
            "create_cylinder": {
                "title": "Create a cylinder",
                "steps": [
                    "1. connect_catia()",
                    "2. new_part(name='Cylinder')",
                    "3. create_sketch(plane='XY')",
                    "4. sketch_circle(cx=0, cy=0, radius=25)",
                    "5. close_sketch()",
                    "6. create_pad(sketch_name='Sketch.1', depth=60)",
                    "7. save_document(path='Cylinder.CATPart')",
                ],
            },
            "simple_assembly": {
                "title": "Create a simple assembly",
                "steps": [
                    "1. connect_catia()",
                    "2. new_assembly(name='MyAssembly')",
                    "3. insert_component(document_path='Part1.CATPart', name='Base')",
                    "4. insert_component(document_path='Part2.CATPart', name='Top')",
                    "5. fix_component(component_name='Base')",
                    "6. add_coincidence_constraint(component1='Base', element1='Face.1', "
                    "component2='Top', element2='Face.1')",
                    "7. save_document(path='MyAssembly.CATProduct')",
                ],
            },
            "engineering_drawing": {
                "title": "Create an engineering drawing from a part",
                "steps": [
                    "1. connect_catia()",
                    "2. new_drawing(name='PartDrawing')",
                    "3. create_front_view(source_document='MyPart.CATPart')",
                    "4. create_projection_view(direction='right')",
                    "5. create_projection_view(direction='top')",
                    "6. create_isometric_view()",
                    "7. add_dimension(view_name='FrontView.1', ...)",
                    "8. save_document(path='PartDrawing.CATDrawing')",
                ],
            },
        }
        if workflow_name in workflows:
            return json.dumps(workflows[workflow_name], indent=2)
        return json.dumps(
            {"error": f"Unknown workflow '{workflow_name}'", "available": list(workflows.keys())}
        )
