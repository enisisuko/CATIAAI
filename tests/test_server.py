"""Tests for MCP server initialization and tool/resource/prompt registration."""

from __future__ import annotations

from catia_mcp.server import create_server


class TestServerSetup:
    def test_create_server(self) -> None:
        server = create_server()
        assert server is not None
        assert server.name == "CATIA MCP Server"

    def test_core_tools_registered(self) -> None:
        server = create_server()
        tools = server._tool_manager._tools
        tool_names = list(tools.keys())

        core_tools = [
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

        for name in core_tools:
            assert name in tool_names, f"Core tool '{name}' not registered"

    def test_smart_ui_tools_registered(self) -> None:
        server = create_server()
        tools = server._tool_manager._tools
        smart_tools = [
            "connect_catia_ui",
            "click_menu_item",
            "click_toolbar",
            "interact_dialog",
            "read_spec_tree_ui",
            "list_ui_controls",
            "select_tree_node",
            "wait_for_dialog_appear",
        ]
        for name in smart_tools:
            assert name in tools, f"Smart UI tool '{name}' not registered"

    def test_agent_tools_registered(self) -> None:
        server = create_server()
        tools = server._tool_manager._tools
        agent_tools = [
            "plan_catia_task",
            "analyze_current_state",
            "suggest_next_step",
            "validate_design",
            "generate_catscript",
        ]
        for name in agent_tools:
            assert name in tools, f"Agent tool '{name}' not registered"

    def test_minimum_tool_count(self) -> None:
        server = create_server()
        tools = server._tool_manager._tools
        assert len(tools) >= 90, f"Expected at least 90 tools, got {len(tools)}"

    def test_resources_registered(self) -> None:
        server = create_server()
        resource_manager = server._resource_manager
        assert resource_manager is not None

    def test_prompts_registered(self) -> None:
        server = create_server()
        prompt_manager = server._prompt_manager
        assert prompt_manager is not None
