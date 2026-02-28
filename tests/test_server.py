"""Tests for MCP server initialization and tool registration."""

from __future__ import annotations

from catia_mcp.server import create_server


class TestServerSetup:
    def test_create_server(self) -> None:
        server = create_server()
        assert server is not None
        assert server.name == "CATIA MCP Server"

    def test_tools_registered(self) -> None:
        server = create_server()
        tools = server._tool_manager._tools
        tool_names = list(tools.keys())

        expected_tools = [
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
            "create_sketch",
            "close_sketch",
            "sketch_line",
            "sketch_circle",
            "sketch_rectangle",
            "create_pad",
            "create_pocket",
            "create_fillet",
            "create_chamfer",
            "create_shell",
            "insert_component",
            "fix_component",
            "create_front_view",
            "create_extrude_surface",
            "measure_distance",
            "capture_screenshot",
            "click_at",
        ]

        for name in expected_tools:
            assert name in tool_names, f"Tool '{name}' not registered"

    def test_minimum_tool_count(self) -> None:
        server = create_server()
        tools = server._tool_manager._tools
        assert len(tools) >= 50, f"Expected at least 50 tools, got {len(tools)}"
