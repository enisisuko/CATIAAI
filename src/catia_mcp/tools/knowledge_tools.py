"""MCP tools for querying the CATIA knowledge base.

These tools let the LLM search and retrieve CATIA knowledge on-demand,
enabling it to learn how to operate CATIA, understand design logic,
and follow best practices.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from catia_mcp.knowledge.manager import get_knowledge


def register(mcp: FastMCP) -> None:
    """Register knowledge base query tools."""

    @mcp.tool()
    def kb_list_topics() -> dict[str, Any]:
        """List all topics in the CATIA knowledge base.
        Use this first to see what knowledge is available."""
        km = get_knowledge()
        return {"topics": km.list_topics(), "total": len(km.list_topics())}

    @mcp.tool()
    def kb_get_topic(topic_id: str) -> dict[str, Any]:
        """Get the full content of a knowledge topic.

        Args:
            topic_id: Topic ID from kb_list_topics.
                Options: fundamentals, part_design, sketcher, assembly,
                drawing, surface_design, scripting, troubleshooting,
                best_practices
        """
        km = get_knowledge()
        topic = km.get_topic(topic_id)
        if topic is None:
            return {
                "error": f"Topic '{topic_id}' not found",
                "available": km.get_topic_ids(),
            }
        sections_summary = {
            key: sec.get("title", key) for key, sec in topic.get("sections", {}).items()
        }
        return {
            "id": topic["id"],
            "title": topic["title"],
            "summary": topic["summary"],
            "sections": sections_summary,
        }

    @mcp.tool()
    def kb_get_section(topic_id: str, section_key: str) -> dict[str, Any]:
        """Get a specific section from a knowledge topic.
        Use kb_get_topic first to see available sections.

        Args:
            topic_id: Topic ID (e.g., 'part_design').
            section_key: Section key (e.g., 'sketch_based_features').
        """
        km = get_knowledge()
        section = km.get_section(topic_id, section_key)
        if section is None:
            topic = km.get_topic(topic_id)
            if topic is None:
                return {"error": f"Topic '{topic_id}' not found"}
            return {
                "error": f"Section '{section_key}' not found in '{topic_id}'",
                "available_sections": list(topic.get("sections", {}).keys()),
            }
        return {
            "topic_id": topic_id,
            "section_key": section_key,
            "title": section.get("title", section_key),
            "content": section.get("content", ""),
        }

    @mcp.tool()
    def kb_search(query: str, max_results: int = 5) -> dict[str, Any]:
        """Search the CATIA knowledge base for relevant information.
        Use natural language or keywords.

        Args:
            query: Search query (e.g., 'how to create fillet',
                   'sketch constraints', 'assembly best practices').
            max_results: Maximum number of results (default 5).
        """
        km = get_knowledge()
        results = km.search(query, max_results)
        return {
            "query": query,
            "result_count": len(results),
            "results": results,
        }

    @mcp.tool()
    def kb_how_to(operation: str) -> dict[str, Any]:
        """Get step-by-step instructions for a specific CATIA operation.
        Searches the knowledge base and returns the most relevant guide.

        Args:
            operation: What you want to do (e.g., 'create a pad',
                      'add fillet', 'assemble two parts',
                      'create engineering drawing').
        """
        km = get_knowledge()
        results = km.search(operation, max_results=3)

        if not results:
            return {
                "operation": operation,
                "found": False,
                "suggestion": "Try broader terms or use kb_list_topics to browse.",
            }

        sections: list[dict[str, Any]] = []
        for r in results:
            section = km.get_section(r["topic_id"], r["section_key"])
            if section:
                sections.append(
                    {
                        "topic": r["topic_title"],
                        "section": section.get("title", ""),
                        "content": section.get("content", ""),
                    }
                )

        return {
            "operation": operation,
            "found": True,
            "guides": sections,
        }

    # ── Knowledge Resources ──────────────────────────────────────────

    @mcp.resource("catia://knowledge/topics")
    def knowledge_topics() -> str:
        """List of all CATIA knowledge base topics."""
        km = get_knowledge()
        return json.dumps(km.list_topics(), indent=2, ensure_ascii=False)

    @mcp.resource("catia://knowledge/{topic_id}")
    def knowledge_topic(topic_id: str) -> str:
        """Full content of a specific knowledge topic."""
        km = get_knowledge()
        topic = km.get_topic(topic_id)
        if topic is None:
            return json.dumps({"error": f"Topic '{topic_id}' not found"})
        return json.dumps(topic, indent=2, ensure_ascii=False)

    @mcp.resource("catia://knowledge/{topic_id}/{section_key}")
    def knowledge_section(topic_id: str, section_key: str) -> str:
        """Specific section of a knowledge topic."""
        km = get_knowledge()
        section = km.get_section(topic_id, section_key)
        if section is None:
            return json.dumps({"error": "Section not found"})
        return json.dumps(section, indent=2, ensure_ascii=False)
