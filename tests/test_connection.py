"""Tests for CATIA connection and document management."""

from __future__ import annotations

import pytest

from catia_mcp.catia.connection import CATIAConnection, DocumentType, get_catia, reset_catia


class TestConnection:
    def test_connect_mock(self, catia: CATIAConnection) -> None:
        assert catia.connected is True
        assert catia.is_mock is True

    def test_double_connect(self, catia: CATIAConnection) -> None:
        result = catia.connect()
        assert result["status"] == "already_connected"

    def test_disconnect(self, catia: CATIAConnection) -> None:
        catia.disconnect()
        assert catia.connected is False

    def test_singleton(self) -> None:
        c1 = get_catia()
        c2 = get_catia()
        assert c1 is c2

    def test_reset_singleton(self) -> None:
        c1 = get_catia()
        reset_catia()
        c2 = get_catia()
        assert c1 is not c2


class TestDocumentManagement:
    def test_new_part(self, catia: CATIAConnection) -> None:
        result = catia.new_document(DocumentType.PART, "MyPart")
        assert result["name"] == "MyPart"
        assert result["type"] == "CATPart"
        assert catia.active_document is not None
        assert catia.active_document.name == "MyPart"

    def test_new_assembly(self, catia: CATIAConnection) -> None:
        result = catia.new_document(DocumentType.PRODUCT, "MyAssembly")
        assert result["type"] == "CATProduct"

    def test_new_drawing(self, catia: CATIAConnection) -> None:
        result = catia.new_document(DocumentType.DRAWING, "MyDrawing")
        assert result["type"] == "CATDrawing"

    def test_auto_name(self, catia: CATIAConnection) -> None:
        result = catia.new_document(DocumentType.PART)
        assert "CATPart" in result["name"]

    def test_open_document(self, catia: CATIAConnection) -> None:
        result = catia.open_document("C:/models/test.CATPart")
        assert result["name"] == "test.CATPart"
        assert result["type"] == "CATPart"

    def test_save_document(self, catia_with_part: CATIAConnection) -> None:
        result = catia_with_part.save_document("C:/output/test.CATPart")
        assert result["status"] == "saved"
        assert catia_with_part.active_document.saved is True

    def test_save_without_path_raises(self, catia_with_part: CATIAConnection) -> None:
        with pytest.raises(RuntimeError, match="No path"):
            catia_with_part.save_document()

    def test_close_document(self, catia_with_part: CATIAConnection) -> None:
        result = catia_with_part.close_document()
        assert result["status"] == "closed"
        assert catia_with_part.active_document is None

    def test_multiple_documents(self, catia: CATIAConnection) -> None:
        catia.new_document(DocumentType.PART, "Part1")
        catia.new_document(DocumentType.PART, "Part2")
        assert catia.active_document.name == "Part2"
        catia.close_document()
        assert catia.active_document.name == "Part1"

    def test_get_document_info(self, catia_with_part: CATIAConnection) -> None:
        info = catia_with_part.get_document_info()
        assert info["name"] == "TestPart"
        assert info["type"] == "CATPart"
        assert "PartBody" in info["bodies"]

    def test_get_feature_tree(self, catia_with_part: CATIAConnection) -> None:
        tree = catia_with_part.get_feature_tree()
        assert tree["document"] == "TestPart"
        assert len(tree["bodies"]) >= 1

    def test_no_document_raises(self, catia: CATIAConnection) -> None:
        with pytest.raises(RuntimeError, match="No active document"):
            catia.get_document_info()

    def test_not_connected_raises(self) -> None:
        conn = CATIAConnection()
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.new_document(DocumentType.PART)


class TestParameters:
    def test_set_and_get(self, catia_with_part: CATIAConnection) -> None:
        catia_with_part.set_parameter("Length", 100.0)
        params = catia_with_part.get_parameters()
        assert params["parameters"]["Length"] == 100.0

    def test_set_overwrites(self, catia_with_part: CATIAConnection) -> None:
        catia_with_part.set_parameter("Width", 50.0)
        result = catia_with_part.set_parameter("Width", 75.0)
        assert result["old_value"] == 50.0
        assert result["new_value"] == 75.0


class TestUndoRedo:
    def test_undo(self, catia_with_part: CATIAConnection) -> None:
        catia_with_part.set_parameter("X", 10)
        result = catia_with_part.undo()
        assert result["status"] == "undone"

    def test_redo(self, catia_with_part: CATIAConnection) -> None:
        catia_with_part.set_parameter("X", 10)
        catia_with_part.undo()
        result = catia_with_part.redo()
        assert result["status"] == "redone"

    def test_nothing_to_undo(self, catia: CATIAConnection) -> None:
        result = catia.undo()
        assert result["status"] == "nothing_to_undo"
