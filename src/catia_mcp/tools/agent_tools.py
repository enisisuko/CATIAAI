"""MCP tools for CLINE-style agent planning and workflow automation.

These tools enable the LLM to reason about CATIA tasks, plan operations,
validate designs, and generate CATScript/VBA macros.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.catia.connection import DocumentType, get_catia


def register(mcp: FastMCP) -> None:
    """Register agent workflow tools."""

    @mcp.tool()
    def plan_catia_task(task_description: str) -> dict[str, Any]:
        """Analyze a CATIA task and generate an ordered execution plan.
        Use this to break complex designs into step-by-step operations.

        Args:
            task_description: Natural language description of what to build/modify.

        Returns:
            Structured plan with ordered steps, required tools, and estimated complexity.
        """
        desc_lower = task_description.lower()

        steps: list[dict[str, Any]] = [{"step": 1, "action": "connect_catia", "args": {}}]

        needs_part = any(
            kw in desc_lower
            for kw in [
                "part",
                "box",
                "cylinder",
                "plate",
                "shaft",
                "gear",
                "bracket",
                "housing",
                "flange",
                "model",
                "solid",
                "create",
                "design",
                "make",
            ]
        )
        needs_assembly = any(kw in desc_lower for kw in ["assembly", "assemble", "mount", "fit"])
        needs_drawing = any(
            kw in desc_lower for kw in ["drawing", "draft", "2d", "view", "dimension"]
        )

        if needs_assembly:
            steps.append({"step": 2, "action": "new_assembly", "args": {}})
            steps.append({"step": 3, "action": "insert_component", "note": "for each part"})
            steps.append({"step": 4, "action": "fix_component", "note": "fix the base part"})
            steps.append(
                {
                    "step": 5,
                    "action": "add_*_constraint",
                    "note": "add constraints between components",
                }
            )
        elif needs_drawing:
            steps.append({"step": 2, "action": "new_drawing", "args": {}})
            steps.append({"step": 3, "action": "create_front_view", "args": {}})
            steps.append({"step": 4, "action": "create_projection_view", "note": "add projections"})
            steps.append({"step": 5, "action": "add_dimension", "note": "dimension key features"})
        elif needs_part:
            steps.append({"step": 2, "action": "new_part", "args": {}})
            steps.append({"step": 3, "action": "create_sketch", "args": {"plane": "XY"}})
            steps.append({"step": 4, "action": "sketch_*", "note": "draw the base profile"})
            steps.append({"step": 5, "action": "close_sketch", "args": {}})
            steps.append({"step": 6, "action": "create_pad/shaft", "note": "create base feature"})

            if any(kw in desc_lower for kw in ["hole", "bore", "drill"]):
                steps.append({"step": len(steps) + 1, "action": "create_hole", "note": "add holes"})
            if any(kw in desc_lower for kw in ["fillet", "round", "radius"]):
                steps.append(
                    {"step": len(steps) + 1, "action": "create_fillet", "note": "add fillets"}
                )
            if any(kw in desc_lower for kw in ["chamfer", "bevel"]):
                steps.append(
                    {"step": len(steps) + 1, "action": "create_chamfer", "note": "add chamfers"}
                )
            if any(kw in desc_lower for kw in ["shell", "hollow", "thin wall"]):
                steps.append(
                    {"step": len(steps) + 1, "action": "create_shell", "note": "hollow out"}
                )
            if any(kw in desc_lower for kw in ["pattern", "array", "repeat"]):
                steps.append(
                    {
                        "step": len(steps) + 1,
                        "action": "create_pattern_*",
                        "note": "pattern features",
                    }
                )
            if any(kw in desc_lower for kw in ["mirror", "symmetric"]):
                steps.append({"step": len(steps) + 1, "action": "create_mirror", "note": "mirror"})

        steps.append(
            {
                "step": len(steps) + 1,
                "action": "get_feature_tree",
                "note": "verify result",
            }
        )
        steps.append({"step": len(steps) + 1, "action": "save_document", "note": "save"})

        return {
            "task": task_description,
            "total_steps": len(steps),
            "estimated_complexity": (
                "high" if len(steps) > 10 else "medium" if len(steps) > 6 else "low"
            ),
            "plan": steps,
        }

    @mcp.tool()
    def analyze_current_state() -> dict[str, Any]:
        """Analyze the current CATIA state and provide a summary.
        Use this to understand what has been done and what can be done next.
        Useful for the agent's 'thinking' step."""
        catia = get_catia()
        state: dict[str, Any] = {
            "connected": catia.connected,
            "mock_mode": catia.is_mock,
        }

        if not catia.connected:
            state["suggestion"] = "Call connect_catia first"
            return state

        doc = catia.active_document
        if doc is None:
            state["suggestion"] = "No document open. Call new_part, new_assembly, or open_document"
            return state

        state["document"] = catia.get_document_info()
        state["feature_tree"] = catia.get_feature_tree()

        if catia.active_sketch:
            state["active_sketch"] = {
                "name": catia.active_sketch.name,
                "element_count": len(catia.active_sketch.elements),
                "constraint_count": len(catia.active_sketch.constraints),
            }
            state["suggestion"] = (
                "Sketch is open. Add geometry (sketch_line, sketch_circle, etc.) "
                "or close_sketch to create features."
            )
        elif doc.doc_type == DocumentType.PART:
            feature_count = sum(len(b.features) for b in doc.bodies)
            if feature_count == 0:
                state["suggestion"] = (
                    "Empty part. Create a sketch first with create_sketch(plane='XY'), "
                    "then add geometry and create features."
                )
            else:
                state["suggestion"] = (
                    f"Part has {feature_count} features. You can add more sketches/features, "
                    "modify parameters, or save the document."
                )
        elif doc.doc_type == DocumentType.PRODUCT:
            comp_count = len(doc.components)
            state["suggestion"] = (
                f"Assembly with {comp_count} components. Insert more components or add constraints."
            )
        elif doc.doc_type == DocumentType.DRAWING:
            view_count = sum(len(s.views) for s in doc.sheets)
            state["suggestion"] = (
                f"Drawing with {view_count} views. Add more views, dimensions, or annotations."
            )

        return state

    @mcp.tool()
    def suggest_next_step() -> dict[str, Any]:
        """Based on the current CATIA state, suggest the most logical next
        operation. Implements the 'thinking' part of the agent chain."""
        catia = get_catia()

        if not catia.connected:
            return {
                "next_tool": "connect_catia",
                "args": {},
                "reason": "Must connect to CATIA before any operation",
            }

        if catia.active_document is None:
            return {
                "next_tool": "new_part",
                "args": {"name": "NewPart"},
                "reason": "No document open. Creating a new part to start modeling.",
                "alternatives": ["new_assembly", "new_drawing", "open_document"],
            }

        doc = catia.active_document

        if catia.active_sketch:
            sketch = catia.active_sketch
            if len(sketch.elements) == 0:
                return {
                    "next_tool": "sketch_rectangle or sketch_circle",
                    "reason": "Empty sketch. Add geometry to define the profile.",
                    "examples": [
                        "sketch_rectangle(x=-50, y=-25, width=100, height=50)",
                        "sketch_circle(cx=0, cy=0, radius=25)",
                    ],
                }
            return {
                "next_tool": "close_sketch",
                "args": {},
                "reason": f"Sketch has {len(sketch.elements)} elements. "
                "Close it to create 3D features from it.",
                "alternative": "Add more geometry or constraints before closing",
            }

        if doc.doc_type == DocumentType.PART:
            feature_count = sum(len(b.features) for b in doc.bodies)
            sketch_count = len(doc.sketches)

            if sketch_count == 0:
                return {
                    "next_tool": "create_sketch",
                    "args": {"plane": "XY"},
                    "reason": "No sketches yet. Create one on XY plane to start.",
                }

            closed_unused = [
                s
                for s in doc.sketches
                if s.closed
                and not any(s.name in str(f.params) for b in doc.bodies for f in b.features)
            ]
            if closed_unused:
                return {
                    "next_tool": "create_pad",
                    "args": {"sketch_name": closed_unused[0].name, "depth": 20.0},
                    "reason": f"Sketch '{closed_unused[0].name}' is ready. "
                    "Extrude it into a solid.",
                }

            if feature_count > 0:
                return {
                    "next_tool": "save_document or add more features",
                    "reason": f"Part has {feature_count} features. "
                    "Consider adding fillets, holes, or saving.",
                }

        return {
            "next_tool": "get_feature_tree",
            "reason": "Check current state before deciding next action.",
        }

    @mcp.tool()
    def validate_design() -> dict[str, Any]:
        """Validate the current design for common issues.
        Checks for empty sketches, unused features, missing constraints, etc."""
        catia = get_catia()
        issues: list[dict[str, str]] = []
        warnings: list[dict[str, str]] = []
        info: list[dict[str, str]] = []

        if not catia.connected:
            issues.append({"severity": "error", "message": "Not connected to CATIA"})
            return {"valid": False, "issues": issues}

        doc = catia.active_document
        if doc is None:
            issues.append({"severity": "error", "message": "No active document"})
            return {"valid": False, "issues": issues}

        if catia.active_sketch:
            warnings.append(
                {
                    "severity": "warning",
                    "message": f"Sketch '{catia.active_sketch.name}' is still open. Close it.",
                }
            )

        if doc.doc_type == DocumentType.PART:
            for sketch in doc.sketches:
                if len(sketch.elements) == 0:
                    warnings.append(
                        {
                            "severity": "warning",
                            "message": f"Sketch '{sketch.name}' is empty.",
                        }
                    )
                if not sketch.closed and catia.active_sketch != sketch:
                    warnings.append(
                        {
                            "severity": "warning",
                            "message": f"Sketch '{sketch.name}' was never closed.",
                        }
                    )

            total_features = sum(len(b.features) for b in doc.bodies)
            if total_features == 0:
                warnings.append(
                    {
                        "severity": "warning",
                        "message": "Part has no features yet.",
                    }
                )

            info.append(
                {
                    "severity": "info",
                    "message": f"Part has {len(doc.bodies)} bodies, "
                    f"{len(doc.sketches)} sketches, {total_features} features.",
                }
            )

        elif doc.doc_type == DocumentType.PRODUCT:
            unconstrained = [c for c in doc.components if not c.fixed and not c.constraints]
            for comp in unconstrained:
                warnings.append(
                    {
                        "severity": "warning",
                        "message": f"Component '{comp.name}' has no constraints.",
                    }
                )

        if not doc.saved:
            warnings.append(
                {
                    "severity": "warning",
                    "message": "Document has not been saved.",
                }
            )

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "info": info,
        }

    @mcp.tool()
    def generate_catscript(
        task_description: str,
        script_type: str = "VBScript",
    ) -> dict[str, Any]:
        """Generate a CATScript/VBA macro for a CATIA task.
        Use for complex or repetitive operations not easily done tool-by-tool.

        Args:
            task_description: What the macro should do.
            script_type: 'VBScript' or 'CATScript'.

        Returns:
            Generated macro code ready for execute_vba_macro.
        """
        templates: dict[str, str] = {
            "export_step": (
                "Dim partDocument1 As PartDocument\n"
                "Set partDocument1 = CATIA.ActiveDocument\n"
                'partDocument1.ExportData "C:\\\\output\\\\export.stp", "stp"\n'
            ),
            "export_iges": (
                "Dim partDocument1 As PartDocument\n"
                "Set partDocument1 = CATIA.ActiveDocument\n"
                'partDocument1.ExportData "C:\\\\output\\\\export.igs", "igs"\n'
            ),
            "update_all": (
                "Dim partDocument1 As PartDocument\n"
                "Set partDocument1 = CATIA.ActiveDocument\n"
                "Dim part1 As Part\n"
                "Set part1 = partDocument1.Part\n"
                "part1.Update\n"
            ),
            "screenshot": ('CATIA.StartCommand "Image Capture"\n'),
            "fit_all": (
                "Dim specsAndGeomWindow1 As SpecsAndGeomWindow\n"
                "Set specsAndGeomWindow1 = CATIA.ActiveWindow\n"
                "Dim viewer3D1 As Viewer3D\n"
                "Set viewer3D1 = specsAndGeomWindow1.ActiveViewer\n"
                "viewer3D1.Reframe\n"
            ),
            "rename_part": (
                "Dim partDocument1 As PartDocument\n"
                "Set partDocument1 = CATIA.ActiveDocument\n"
                "Dim product1 As Product\n"
                "Set product1 = partDocument1.Product\n"
                'product1.PartNumber = "NewPartName"\n'
            ),
        }

        desc_lower = task_description.lower()
        selected_template = None
        for key, template in templates.items():
            if key.replace("_", " ") in desc_lower or any(
                word in desc_lower for word in key.split("_")
            ):
                selected_template = template
                break

        if selected_template:
            return {
                "script_type": script_type,
                "code": selected_template,
                "note": "Generated from template. Review before execution.",
                "usage": "Pass the 'code' field to execute_vba_macro",
            }

        basic_code = (
            f"' Auto-generated {script_type} for: {task_description}\n"
            "' TODO: Implement the specific logic\n"
            "Dim partDocument1 As PartDocument\n"
            "Set partDocument1 = CATIA.ActiveDocument\n"
            "Dim part1 As Part\n"
            "Set part1 = partDocument1.Part\n"
            "' Add operations here\n"
            "part1.Update\n"
        )

        return {
            "script_type": script_type,
            "code": basic_code,
            "note": "Basic template generated. Customize the operations section.",
            "available_templates": list(templates.keys()),
        }
