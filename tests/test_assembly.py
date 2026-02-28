"""Tests for CATIA Assembly operations."""

from __future__ import annotations

import pytest

from catia_mcp.catia.connection import CATIAConnection


class TestAssembly:
    def test_insert_component(self, catia_with_assembly: CATIAConnection) -> None:
        result = catia_with_assembly.insert_component("C:/parts/shaft.CATPart", "Shaft")
        assert result["name"] == "Shaft"
        assert len(catia_with_assembly.active_document.components) == 1

    def test_insert_multiple(self, catia_with_assembly: CATIAConnection) -> None:
        catia_with_assembly.insert_component("shaft.CATPart", "Shaft")
        catia_with_assembly.insert_component("bearing.CATPart", "Bearing")
        assert len(catia_with_assembly.active_document.components) == 2

    def test_auto_name(self, catia_with_assembly: CATIAConnection) -> None:
        result = catia_with_assembly.insert_component("C:/models/gear.CATPart")
        assert result["name"] == "gear"


class TestAssemblyConstraints:
    @pytest.fixture(autouse=True)
    def _setup(self, catia_with_assembly: CATIAConnection) -> None:
        self.catia = catia_with_assembly
        self.catia.insert_component("base.CATPart", "Base")
        self.catia.insert_component("shaft.CATPart", "Shaft")

    def test_coincidence(self) -> None:
        result = self.catia.add_assembly_constraint(
            "Coincidence", "Base", "Axis.1", "Shaft", "Axis.1"
        )
        assert result["type"] == "Coincidence"

    def test_contact(self) -> None:
        result = self.catia.add_assembly_constraint(
            "Contact", "Base", "Face.Top", "Shaft", "Face.Bottom"
        )
        assert result["type"] == "Contact"

    def test_offset(self) -> None:
        result = self.catia.add_assembly_constraint(
            "Offset", "Base", "Plane.1", "Shaft", "Plane.1", 10.0
        )
        assert result["type"] == "Offset"
        assert result["value"] == 10.0

    def test_fix(self) -> None:
        result = self.catia.fix_component("Base")
        assert result["status"] == "fixed"

    def test_fix_nonexistent_raises(self) -> None:
        with pytest.raises(RuntimeError, match="not found"):
            self.catia.fix_component("DoesNotExist")

    def test_move(self) -> None:
        result = self.catia.move_component("Shaft", 100, 0, 50)
        assert result["position"] == [100, 0, 50]

    def test_bom(self) -> None:
        bom = self.catia.get_bom()
        assert bom["total_parts"] == 2
        assert len(bom["items"]) == 2
