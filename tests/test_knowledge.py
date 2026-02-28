"""Tests for the CATIA knowledge base."""

from __future__ import annotations

from catia_mcp.knowledge.manager import KnowledgeManager


class TestKnowledgeManager:
    def test_load_all_topics(self) -> None:
        km = KnowledgeManager()
        topics = km.list_topics()
        assert len(topics) == 9
        ids = [t["id"] for t in topics]
        assert "fundamentals" in ids
        assert "part_design" in ids
        assert "sketcher" in ids
        assert "assembly" in ids
        assert "drawing" in ids
        assert "surface_design" in ids
        assert "scripting" in ids
        assert "troubleshooting" in ids
        assert "best_practices" in ids

    def test_get_topic(self) -> None:
        km = KnowledgeManager()
        topic = km.get_topic("fundamentals")
        assert topic is not None
        assert topic["title"] == "CATIA 基础知识"
        assert "sections" in topic
        assert "workbenches" in topic["sections"]

    def test_get_topic_not_found(self) -> None:
        km = KnowledgeManager()
        assert km.get_topic("nonexistent") is None

    def test_get_section(self) -> None:
        km = KnowledgeManager()
        section = km.get_section("sketcher", "constraints")
        assert section is not None
        assert "title" in section
        assert "content" in section

    def test_get_section_not_found(self) -> None:
        km = KnowledgeManager()
        assert km.get_section("sketcher", "nonexistent") is None

    def test_search_basic(self) -> None:
        km = KnowledgeManager()
        results = km.search("fillet")
        assert len(results) > 0
        assert any(
            "fillet" in r["section_title"].lower()
            or "fillet" in r["preview"].lower()
            for r in results
        )

    def test_search_chinese(self) -> None:
        km = KnowledgeManager()
        results = km.search("草图")
        assert len(results) > 0

    def test_search_constraint(self) -> None:
        km = KnowledgeManager()
        results = km.search("constraint")
        assert len(results) > 0

    def test_search_pad(self) -> None:
        km = KnowledgeManager()
        results = km.search("pad extrude")
        assert len(results) > 0

    def test_search_empty(self) -> None:
        km = KnowledgeManager()
        results = km.search("xyznonexistent123")
        assert len(results) == 0

    def test_search_max_results(self) -> None:
        km = KnowledgeManager()
        results = km.search("design", max_results=3)
        assert len(results) <= 3


class TestKnowledgeContent:
    def test_fundamentals_has_workbenches(self) -> None:
        km = KnowledgeManager()
        section = km.get_section("fundamentals", "workbenches")
        content = section["content"]
        assert "Part Design" in content
        assert "Sketcher" in content
        assert "Assembly Design" in content

    def test_fundamentals_has_object_model(self) -> None:
        km = KnowledgeManager()
        section = km.get_section("fundamentals", "object_model")
        assert "Application" in section["content"]
        assert "Documents" in section["content"]

    def test_part_design_has_features(self) -> None:
        km = KnowledgeManager()
        section = km.get_section("part_design", "sketch_based_features")
        content = section["content"]
        assert "Pad" in content
        assert "Pocket" in content
        assert "Shaft" in content

    def test_sketcher_has_constraints(self) -> None:
        km = KnowledgeManager()
        section = km.get_section("sketcher", "constraints")
        assert "Coincidence" in section["content"] or "重合" in section["content"]

    def test_assembly_has_constraint_types(self) -> None:
        km = KnowledgeManager()
        section = km.get_section("assembly", "constraints")
        content = section["content"]
        assert "Coincidence" in content
        assert "Contact" in content
        assert "Offset" in content

    def test_scripting_has_code_templates(self) -> None:
        km = KnowledgeManager()
        section = km.get_section("scripting", "common_patterns")
        content = section["content"]
        assert "CATIA" in str(content)

    def test_troubleshooting_has_errors(self) -> None:
        km = KnowledgeManager()
        section = km.get_section("troubleshooting", "feature_errors")
        assert section is not None

    def test_best_practices_has_guidelines(self) -> None:
        km = KnowledgeManager()
        section = km.get_section("best_practices", "modeling_guidelines")
        assert isinstance(section["content"], list)
        assert len(section["content"]) > 5

    def test_surface_design_has_methods(self) -> None:
        km = KnowledgeManager()
        section = km.get_section("surface_design", "creation_methods")
        content = section["content"]
        assert "Sweep" in content
        assert "Loft" in content
