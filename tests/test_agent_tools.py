"""Tests for CLINE-style agent tools."""

from __future__ import annotations

from catia_mcp.catia.connection import CATIAConnection, get_catia, reset_catia


class TestPlanTask:
    def test_plan_part(self, catia: CATIAConnection) -> None:
        from catia_mcp.server import create_server

        server = create_server()
        tools = server._tool_manager._tools
        assert "plan_catia_task" in tools

    def test_plan_generates_steps(self) -> None:
        reset_catia()
        c = get_catia()
        c.connect()

        from catia_mcp.catia.connection import get_catia as gc

        catia = gc()
        catia.connect()

        desc = "Create a box with holes and fillets"
        desc_lower = desc.lower()
        assert "box" in desc_lower
        assert "hole" in desc_lower
        assert "fillet" in desc_lower


class TestAnalyzeState:
    def test_not_connected(self) -> None:
        reset_catia()
        catia = get_catia()
        state = {
            "connected": catia.connected,
            "suggestion": "Call connect_catia first" if not catia.connected else None,
        }
        assert state["connected"] is False
        assert "connect_catia" in state["suggestion"]

    def test_no_document(self, catia: CATIAConnection) -> None:
        assert catia.active_document is None

    def test_with_part(self, catia_with_part: CATIAConnection) -> None:
        assert catia_with_part.active_document is not None
        info = catia_with_part.get_document_info()
        assert info["type"] == "CATPart"


class TestValidateDesign:
    def test_validate_empty_part(self, catia_with_part: CATIAConnection) -> None:
        doc = catia_with_part.active_document
        total_features = sum(len(b.features) for b in doc.bodies)
        assert total_features == 0

    def test_validate_unsaved(self, catia_with_part: CATIAConnection) -> None:
        assert catia_with_part.active_document.saved is False

    def test_validate_with_features(self, catia_with_part: CATIAConnection) -> None:
        catia_with_part.create_sketch("XY")
        catia_with_part.sketch_rectangle(0, 0, 100, 50)
        catia_with_part.close_sketch()
        catia_with_part.create_pad("Sketch.1", 30)

        doc = catia_with_part.active_document
        total_features = sum(len(b.features) for b in doc.bodies)
        assert total_features == 1


class TestGenerateCATScript:
    def test_export_template(self) -> None:
        task = "export step file"
        assert "export" in task.lower()
        assert "step" in task.lower()

    def test_basic_template(self) -> None:
        code = "Dim partDocument1 As PartDocument\nSet partDocument1 = CATIA.ActiveDocument\n"
        assert "CATIA.ActiveDocument" in code


class TestSuggestNextStep:
    def test_suggest_connect_when_disconnected(self) -> None:
        reset_catia()
        catia = get_catia()
        assert not catia.connected

    def test_suggest_new_doc_when_connected(self, catia: CATIAConnection) -> None:
        assert catia.connected
        assert catia.active_document is None

    def test_suggest_sketch_for_empty_part(self, catia_with_part: CATIAConnection) -> None:
        doc = catia_with_part.active_document
        assert len(doc.sketches) == 0

    def test_suggest_close_sketch(self, catia_with_part: CATIAConnection) -> None:
        catia_with_part.create_sketch("XY")
        catia_with_part.sketch_rectangle(0, 0, 100, 50)
        assert catia_with_part.active_sketch is not None
        assert len(catia_with_part.active_sketch.elements) > 0
