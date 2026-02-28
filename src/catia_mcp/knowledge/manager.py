"""Knowledge Base manager — indexes, searches, and retrieves CATIA knowledge."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_manager: KnowledgeManager | None = None


class KnowledgeManager:
    """Central manager for the CATIA knowledge base.

    Loads all knowledge modules and provides search/retrieval capabilities
    for MCP resources and agent tools.
    """

    def __init__(self) -> None:
        self._topics: dict[str, dict[str, Any]] = {}
        self._load_all()

    def _load_all(self) -> None:
        from catia_mcp.knowledge import (
            assembly,
            best_practices,
            drawing,
            fundamentals,
            part_design,
            scripting,
            sketcher,
            surface_design,
            troubleshooting,
        )

        for module in [
            fundamentals,
            part_design,
            sketcher,
            assembly,
            drawing,
            surface_design,
            scripting,
            troubleshooting,
            best_practices,
        ]:
            data = module.KNOWLEDGE
            self._topics[data["id"]] = data
        logger.info("Loaded %d knowledge topics", len(self._topics))

    # ── Query API ────────────────────────────────────────────────────

    def list_topics(self) -> list[dict[str, str]]:
        """Return a summary list of all knowledge topics."""
        return [
            {"id": t["id"], "title": t["title"], "summary": t["summary"]}
            for t in self._topics.values()
        ]

    def get_topic(self, topic_id: str) -> dict[str, Any] | None:
        """Retrieve a full knowledge topic by its ID."""
        return self._topics.get(topic_id)

    def get_section(self, topic_id: str, section_key: str) -> Any | None:
        """Retrieve a specific section within a topic."""
        topic = self._topics.get(topic_id)
        if topic is None:
            return None
        sections = topic.get("sections", {})
        return sections.get(section_key)

    def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        """Search the knowledge base for entries matching the query.

        Searches across topic titles, section titles, and content text.
        """
        query_lower = query.lower()
        keywords = query_lower.split()
        results: list[dict[str, Any]] = []

        for topic in self._topics.values():
            topic_score = 0
            if query_lower in topic["title"].lower():
                topic_score += 10
            if query_lower in topic.get("summary", "").lower():
                topic_score += 5

            for key, section in topic.get("sections", {}).items():
                section_score = topic_score
                section_title = section.get("title", key)
                section_content = section.get("content", "")

                if isinstance(section_content, list):
                    section_text = " ".join(
                        str(item) for item in section_content
                    )
                elif isinstance(section_content, dict):
                    section_text = " ".join(
                        f"{k} {v}" for k, v in section_content.items()
                    )
                else:
                    section_text = str(section_content)

                combined = f"{section_title} {section_text}".lower()
                for kw in keywords:
                    if kw in combined:
                        section_score += 3

                if section_score > 0:
                    results.append({
                        "topic_id": topic["id"],
                        "topic_title": topic["title"],
                        "section_key": key,
                        "section_title": section_title,
                        "score": section_score,
                        "preview": section_text[:200] if section_text else "",
                    })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]

    def get_topic_ids(self) -> list[str]:
        return list(self._topics.keys())


def get_knowledge() -> KnowledgeManager:
    """Get or create the global KnowledgeManager singleton."""
    global _manager
    if _manager is None:
        _manager = KnowledgeManager()
    return _manager
