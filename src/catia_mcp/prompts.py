"""MCP Prompts for CATIA agent workflows.

Prompts are reusable, parameterized message templates that guide LLMs
through CATIA operations using CLINE-style agent thinking chains.
"""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register(mcp: FastMCP) -> None:
    """Register all MCP prompts for agent-guided CATIA workflows."""

    @mcp.prompt()
    def catia_agent_system() -> str:
        """System prompt for the CATIA automation agent. Sets up the agent's
        role, capabilities, and thinking chain methodology."""
        return (
            "You are CATIA-Agent, an expert CAD/CAM/CAE automation agent. "
            "You operate CATIA V5/V6 through MCP tools to help users design "
            "mechanical parts, assemblies, and engineering drawings.\n\n"
            "## Your Capabilities\n"
            "- **Part Design**: Create 3D solid features (pad, pocket, shaft, groove, "
            "fillet, chamfer, shell, hole, patterns, mirror)\n"
            "- **Sketcher**: Draw 2D profiles (lines, circles, rectangles, arcs, splines) "
            "with constraints and dimensions\n"
            "- **Assembly**: Assemble components with constraints (coincidence, contact, "
            "offset, angle, fix)\n"
            "- **Drawing**: Create engineering drawings with views, dimensions, annotations\n"
            "- **Surface Design**: Create and manipulate surfaces (extrude, revolve, sweep, "
            "fill, loft, offset, trim, split, join)\n"
            "- **Vision/UI**: When API operations are insufficient, use screen capture "
            "and UI automation to interact with CATIA directly\n\n"
            "## Thinking Chain (CLINE-style)\n"
            "For each user request, follow this methodology:\n"
            "1. **Analyze**: Understand what the user wants to create/modify\n"
            "2. **Plan**: Break the task into ordered CATIA operations\n"
            "3. **Execute**: Call tools step by step, verifying each result\n"
            "4. **Verify**: Check the feature tree and document state\n"
            "5. **Report**: Summarize what was done and the final state\n\n"
            "## Rules\n"
            "- Always call `connect_catia` first if not connected\n"
            "- Create sketches before features that require them (pad, pocket, etc.)\n"
            "- Close sketches before creating features from them\n"
            "- Check the feature tree after complex operations\n"
            "- Save the document when the user's task is complete\n"
            "- If a COM operation fails, try the vision/UI automation approach\n"
            "- Use `plan_catia_task` to break complex designs into steps"
        )

    @mcp.prompt()
    def design_part(description: str) -> str:
        """Guide the agent to design a 3D part from a text description.

        Args:
            description: Natural language description of the part to create.
        """
        return (
            f"## Task: Design a 3D Part\n\n"
            f"**User Request**: {description}\n\n"
            f"**Instructions**:\n"
            f"1. Analyze the description to identify the base shape and features\n"
            f"2. Plan the modeling sequence (base sketch → extrusion → features)\n"
            f"3. Create a new part document\n"
            f"4. Build the geometry step by step:\n"
            f"   a. Create the base sketch on the appropriate plane\n"
            f"   b. Add sketch geometry (rectangle/circle/profile)\n"
            f"   c. Add constraints and dimensions\n"
            f"   d. Close the sketch\n"
            f"   e. Create the base feature (pad/shaft)\n"
            f"   f. Add secondary features (holes, fillets, chamfers, etc.)\n"
            f"5. Verify the feature tree\n"
            f"6. Save the document\n\n"
            f"Think step by step. Call tools one at a time and verify each result."
        )

    @mcp.prompt()
    def modify_part(modification: str) -> str:
        """Guide the agent to modify an existing part.

        Args:
            modification: Description of the modification to make.
        """
        return (
            f"## Task: Modify Existing Part\n\n"
            f"**Modification**: {modification}\n\n"
            f"**Instructions**:\n"
            f"1. First, check the current state: call `get_document_info` and `get_feature_tree`\n"
            f"2. Analyze which features need to be added/modified/deleted\n"
            f"3. Plan the modification sequence\n"
            f"4. Execute the modifications\n"
            f"5. Verify the result with `get_feature_tree`\n"
            f"6. Save the document\n\n"
            f"If modifying parameters, use `get_parameters` and `set_parameter`.\n"
            f"If the modification requires new sketches/features, create them."
        )

    @mcp.prompt()
    def create_assembly(components: str) -> str:
        """Guide the agent to create an assembly from component descriptions.

        Args:
            components: Description of components and how they fit together.
        """
        return (
            f"## Task: Create Assembly\n\n"
            f"**Components**: {components}\n\n"
            f"**Instructions**:\n"
            f"1. Create a new assembly document\n"
            f"2. Insert each component part\n"
            f"3. Fix the base/reference component\n"
            f"4. Add assembly constraints:\n"
            f"   - Coincidence for coaxial/coplanar alignment\n"
            f"   - Contact for face-to-face\n"
            f"   - Offset for specific distances\n"
            f"   - Angle for angular relationships\n"
            f"5. Verify with `get_bill_of_materials`\n"
            f"6. Save the assembly"
        )

    @mcp.prompt()
    def create_drawing(source_part: str, views: str = "front, right, top, isometric") -> str:
        """Guide the agent to create an engineering drawing.

        Args:
            source_part: Path or name of the 3D part/assembly to draw.
            views: Comma-separated list of views to create.
        """
        return (
            f"## Task: Create Engineering Drawing\n\n"
            f"**Source**: {source_part}\n"
            f"**Views**: {views}\n\n"
            f"**Instructions**:\n"
            f"1. Create a new drawing document\n"
            f"2. Create the front view from the source part\n"
            f"3. Add projection views (right, top, bottom as needed)\n"
            f"4. Add section views if cross-sections are needed\n"
            f"5. Add an isometric view for 3D perspective\n"
            f"6. Add dimensions to key features\n"
            f"7. Add annotations (material, surface finish, tolerances)\n"
            f"8. Save the drawing"
        )

    @mcp.prompt()
    def troubleshoot_catia(problem: str) -> str:
        """Guide the agent to troubleshoot a CATIA issue.

        Args:
            problem: Description of the problem or error.
        """
        return (
            f"## Task: Troubleshoot CATIA Issue\n\n"
            f"**Problem**: {problem}\n\n"
            f"**Diagnostic Steps**:\n"
            f"1. Check connection: `get_catia_status`\n"
            f"2. Check document state: `get_document_info`\n"
            f"3. Review feature tree: `get_feature_tree`\n"
            f"4. Take a screenshot to see the current UI state: `capture_screenshot`\n"
            f"5. If COM fails, try vision-based approach:\n"
            f"   a. `connect_catia_ui` to access UI elements\n"
            f"   b. `list_ui_controls` to see available controls\n"
            f"   c. Use `click_menu_item` or `click_toolbar` as needed\n"
            f"6. If standard tools fail, try VBA: `execute_vba_macro`\n\n"
            f"**Common Issues**:\n"
            f"- 'No active document' → call `new_part` or `open_document` first\n"
            f"- 'Sketch not found' → create the sketch before using it\n"
            f"- 'Not connected' → call `connect_catia` first\n"
            f"- COM error → try `undo` and retry, or use vision tools"
        )
