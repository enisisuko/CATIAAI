"""Integration test: simulate a full modeling workflow through CATIA connection."""

from __future__ import annotations

from catia_mcp.catia.connection import CATIAConnection, DocumentType


class TestFullPartWorkflow:
    """Simulate creating a complete part: box with holes, fillets, and a shell."""

    def test_complete_box_with_features(self, catia: CATIAConnection) -> None:
        catia.new_document(DocumentType.PART, "BoxWithHoles")
        doc = catia.active_document
        assert doc.name == "BoxWithHoles"

        catia.create_sketch("XY")
        catia.sketch_rectangle(-50, -25, 100, 50)
        catia.sketch_constraint("length", ["line_1"], value=100.0)
        catia.sketch_constraint("length", ["line_2"], value=50.0)
        catia.close_sketch()
        assert len(doc.sketches) == 1
        assert doc.sketches[0].closed is True

        pad = catia.create_pad("Sketch.1", 30.0)
        assert pad["name"] == "Pad.1"

        hole1 = catia.create_hole(-30, 0, 8, 30, "threaded")
        hole2 = catia.create_hole(30, 0, 8, 30, "threaded")
        assert hole1["name"] == "Hole.1"
        assert hole2["name"] == "Hole.2"

        fillet = catia.create_fillet(["Edge.1", "Edge.2", "Edge.3", "Edge.4"], 3.0)
        assert fillet["edge_count"] == 4

        shell = catia.create_shell(2.0, ["Face.Top"])
        assert shell["thickness"] == 2.0

        tree = catia.get_feature_tree()
        body_features = tree["bodies"][0]["features"]
        assert len(body_features) == 5  # Pad + 2 Holes + Fillet + Shell

        catia.save_document("C:/output/BoxWithHoles.CATPart")
        assert doc.saved is True


class TestFullAssemblyWorkflow:
    """Simulate assembling multiple components."""

    def test_simple_assembly(self, catia: CATIAConnection) -> None:
        catia.new_document(DocumentType.PRODUCT, "GearBox")

        catia.insert_component("housing.CATPart", "Housing")
        catia.insert_component("shaft.CATPart", "Shaft")
        catia.insert_component("gear.CATPart", "Gear_1")
        catia.insert_component("gear.CATPart", "Gear_2")
        catia.insert_component("bearing.CATPart", "Bearing_L")
        catia.insert_component("bearing.CATPart", "Bearing_R")

        catia.fix_component("Housing")
        catia.add_assembly_constraint("Coincidence", "Housing", "Axis.Center", "Shaft", "Axis.1")
        catia.add_assembly_constraint(
            "Contact", "Housing", "Face.BearingSeat_L", "Bearing_L", "Face.Outer"
        )
        catia.add_assembly_constraint("Coincidence", "Shaft", "Axis.1", "Gear_1", "Axis.1")
        catia.add_assembly_constraint("Offset", "Housing", "Plane.Mid", "Gear_1", "Plane.1", 20.0)

        bom = catia.get_bom()
        assert bom["total_parts"] == 6

        tree = catia.get_feature_tree()
        assert len(tree["components"]) == 6
        housing = next(c for c in tree["components"] if c["name"] == "Housing")
        assert housing["fixed"] is True


class TestFullDrawingWorkflow:
    """Simulate creating a technical drawing."""

    def test_engineering_drawing(self, catia: CATIAConnection) -> None:
        catia.new_document(DocumentType.DRAWING, "BoxDrawing")

        catia.create_view("Front", "BoxWithHoles.CATPart")
        catia.create_view("Projection", direction="right")
        catia.create_view("Projection", direction="top")
        catia.create_view("Isometric")
        catia.create_view("Section", plane="XZ")

        catia.add_drawing_dimension("FrontView.1", "distance", ["Edge.1", "Edge.3"])
        catia.add_drawing_dimension("FrontView.1", "diameter", ["Circle.1"])
        catia.add_annotation("FrontView.1", "MATERIAL: AL 6061-T6", 10, 10)

        tree = catia.get_feature_tree()
        assert len(tree["sheets"][0]["views"]) == 5
