"""Tests for MCP Resources."""

from __future__ import annotations

from catia_mcp.catia.connection import CATIAConnection, get_catia, reset_catia


class TestResources:
    def test_status_resource_disconnected(self) -> None:
        reset_catia()
        catia = get_catia()
        data = {
            "connected": catia.connected,
            "mock_mode": catia.is_mock,
            "active_document": None,
        }
        assert data["connected"] is False

    def test_status_resource_connected(self, catia_with_part: CATIAConnection) -> None:
        data = {
            "connected": catia_with_part.connected,
            "active_document": catia_with_part.active_document.name,
        }
        assert data["connected"] is True
        assert data["active_document"] == "TestPart"

    def test_document_info_resource(self, catia_with_part: CATIAConnection) -> None:
        info = catia_with_part.get_document_info()
        assert info["name"] == "TestPart"
        assert info["type"] == "CATPart"

    def test_feature_tree_resource(self, catia_with_part: CATIAConnection) -> None:
        tree = catia_with_part.get_feature_tree()
        assert tree["document"] == "TestPart"
        assert len(tree["bodies"]) >= 1

    def test_parameters_resource(self, catia_with_part: CATIAConnection) -> None:
        catia_with_part.set_parameter("Length", 100.0)
        params = catia_with_part.get_parameters()
        assert params["parameters"]["Length"] == 100.0

    def test_tools_reference(self) -> None:
        from catia_mcp.server import create_server

        server = create_server()
        assert server is not None
