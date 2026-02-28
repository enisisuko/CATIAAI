"""CATIA COM connection management with automatic mock fallback."""

from __future__ import annotations

import logging
import platform
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)

_catia_instance: CATIAConnection | None = None


class DocumentType(StrEnum):
    PART = "CATPart"
    PRODUCT = "CATProduct"
    DRAWING = "CATDrawing"


@dataclass
class SketchElement:
    id: str
    element_type: str  # line, circle, arc, rectangle, spline, point
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class Constraint:
    id: str
    constraint_type: str
    elements: list[str] = field(default_factory=list)
    value: float | None = None


@dataclass
class Sketch:
    name: str
    plane: str
    elements: list[SketchElement] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)
    closed: bool = False

    def add_element(self, element_type: str, **params: Any) -> SketchElement:
        elem = SketchElement(
            id=f"{element_type}_{len(self.elements) + 1}", element_type=element_type, params=params
        )
        self.elements.append(elem)
        return elem


@dataclass
class Feature:
    name: str
    feature_type: str
    params: dict[str, Any] = field(default_factory=dict)
    children: list[Feature] = field(default_factory=list)


@dataclass
class Body:
    name: str
    features: list[Feature] = field(default_factory=list)


@dataclass
class Component:
    name: str
    document_path: str
    constraints: list[dict[str, Any]] = field(default_factory=list)
    fixed: bool = False
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class DrawingView:
    name: str
    view_type: str
    params: dict[str, Any] = field(default_factory=dict)
    dimensions: list[dict[str, Any]] = field(default_factory=list)
    annotations: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DrawingSheet:
    name: str
    views: list[DrawingView] = field(default_factory=list)


@dataclass
class CATIADocument:
    name: str
    doc_type: DocumentType
    path: str | None = None
    saved: bool = False
    bodies: list[Body] = field(default_factory=list)
    sketches: list[Sketch] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)
    components: list[Component] = field(default_factory=list)
    sheets: list[DrawingSheet] = field(default_factory=list)
    hybrid_bodies: list[Body] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.doc_type == DocumentType.PART and not self.bodies:
            self.bodies.append(Body(name="PartBody"))
            self.hybrid_bodies.append(Body(name="Geometrical Set.1"))
        elif self.doc_type == DocumentType.DRAWING and not self.sheets:
            self.sheets.append(DrawingSheet(name="Sheet.1"))


class CATIAConnection:
    """Manages connection to CATIA V5/V6 via COM or mock for testing."""

    def __init__(self) -> None:
        self._com_app: Any = None
        self._pycatia: Any = None
        self._backend: str = "mock"
        self._is_mock = False
        self._connected = False
        self._documents: list[CATIADocument] = []
        self._active_doc_index: int = -1
        self._active_sketch: Sketch | None = None
        self._undo_stack: list[str] = []
        self._redo_stack: list[str] = []

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def is_mock(self) -> bool:
        return self._is_mock

    @property
    def active_document(self) -> CATIADocument | None:
        if 0 <= self._active_doc_index < len(self._documents):
            return self._documents[self._active_doc_index]
        return None

    @property
    def active_sketch(self) -> Sketch | None:
        return self._active_sketch

    def connect(self) -> dict[str, Any]:
        """Connect to CATIA instance.

        Connection priority:
        1. pycatia library (recommended, best API coverage)
        2. Direct win32com (fallback)
        3. Mock mode (non-Windows or CATIA not available)
        """
        if self._connected:
            return {"status": "already_connected", "mock": self._is_mock}

        if platform.system() == "Windows":
            # Try pycatia first (evereux/pycatia — best CATIA Python automation)
            try:
                from catia_mcp.catia.pycatia_backend import PyCATIABackend

                self._pycatia = PyCATIABackend()
                result = self._pycatia.connect()
                self._connected = True
                self._is_mock = False
                self._backend = "pycatia"
                logger.info("Connected to CATIA via pycatia library")
                return result
            except Exception as e:
                logger.info("pycatia not available: %s. Trying direct COM.", e)

            # Fallback to direct COM
            try:
                import win32com.client

                self._com_app = win32com.client.Dispatch("CATIA.Application")
                self._connected = True
                self._is_mock = False
                self._backend = "win32com"
                logger.info("Connected to CATIA via direct COM")
                return {
                    "status": "connected",
                    "mock": False,
                    "backend": "win32com",
                    "version": str(self._com_app.SystemConfiguration.Version),
                }
            except Exception as e:
                logger.warning("Failed to connect to CATIA COM: %s. Using mock mode.", e)

        self._connected = True
        self._is_mock = True
        self._backend = "mock"
        logger.info("Using mock CATIA (non-Windows or CATIA not available)")
        return {"status": "connected", "mock": True, "version": "V5-6R2024 (Mock)"}

    def disconnect(self) -> dict[str, str]:
        self._connected = False
        self._com_app = None
        return {"status": "disconnected"}

    def _require_connection(self) -> None:
        if not self._connected:
            raise RuntimeError("Not connected to CATIA. Call connect_catia first.")

    def _require_document(self, doc_type: DocumentType | None = None) -> CATIADocument:
        self._require_connection()
        doc = self.active_document
        if doc is None:
            raise RuntimeError("No active document. Open or create a document first.")
        if doc_type and doc.doc_type != doc_type:
            raise RuntimeError(
                f"Active document is {doc.doc_type.value}, expected {doc_type.value}"
            )
        return doc

    def _push_undo(self, action: str) -> None:
        self._undo_stack.append(action)
        self._redo_stack.clear()

    # ── Document Management ──────────────────────────────────────────────

    def new_document(self, doc_type: DocumentType, name: str | None = None) -> dict[str, Any]:
        self._require_connection()
        if name is None:
            name = f"New_{doc_type.value}_{len(self._documents) + 1}"

        if not self._is_mock and self._com_app:
            self._com_app.Documents.Add(doc_type.value)

        doc = CATIADocument(name=name, doc_type=doc_type)
        self._documents.append(doc)
        self._active_doc_index = len(self._documents) - 1
        self._push_undo(f"new_{doc_type.value}")
        return {"name": doc.name, "type": doc.doc_type.value, "index": self._active_doc_index}

    def open_document(self, path: str) -> dict[str, Any]:
        self._require_connection()
        ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        type_map = {
            "catpart": DocumentType.PART,
            "catproduct": DocumentType.PRODUCT,
            "catdrawing": DocumentType.DRAWING,
        }
        doc_type = type_map.get(ext, DocumentType.PART)
        name = path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]

        if not self._is_mock and self._com_app:
            self._com_app.Documents.Open(path)

        doc = CATIADocument(name=name, doc_type=doc_type, path=path)
        self._documents.append(doc)
        self._active_doc_index = len(self._documents) - 1
        return {"name": doc.name, "type": doc.doc_type.value, "path": path}

    def save_document(self, path: str | None = None) -> dict[str, str]:
        doc = self._require_document()
        if path:
            doc.path = path
        if doc.path is None:
            raise RuntimeError("No path specified. Use save_document_as with a path.")

        if not self._is_mock and self._com_app:
            self._com_app.ActiveDocument.SaveAs(doc.path)

        doc.saved = True
        return {"status": "saved", "path": doc.path}

    def close_document(self) -> dict[str, str]:
        doc = self._require_document()
        name = doc.name

        if not self._is_mock and self._com_app:
            self._com_app.ActiveDocument.Close()

        self._documents.pop(self._active_doc_index)
        self._active_doc_index = len(self._documents) - 1
        self._active_sketch = None
        return {"status": "closed", "name": name}

    def get_document_info(self) -> dict[str, Any]:
        doc = self._require_document()
        info: dict[str, Any] = {
            "name": doc.name,
            "type": doc.doc_type.value,
            "path": doc.path,
            "saved": doc.saved,
        }
        if doc.doc_type == DocumentType.PART:
            info["bodies"] = [b.name for b in doc.bodies]
            info["sketches"] = [s.name for s in doc.sketches]
            info["feature_count"] = sum(len(b.features) for b in doc.bodies)
            info["parameter_count"] = len(doc.parameters)
        elif doc.doc_type == DocumentType.PRODUCT:
            info["components"] = [c.name for c in doc.components]
        elif doc.doc_type == DocumentType.DRAWING:
            info["sheets"] = [s.name for s in doc.sheets]
        return info

    def get_feature_tree(self) -> dict[str, Any]:
        doc = self._require_document()
        tree: dict[str, Any] = {"document": doc.name, "type": doc.doc_type.value}

        if doc.doc_type == DocumentType.PART:
            tree["bodies"] = []
            for body in doc.bodies:
                body_info = {"name": body.name, "features": []}
                for feat in body.features:
                    body_info["features"].append({"name": feat.name, "type": feat.feature_type})
                tree["bodies"].append(body_info)
            tree["sketches"] = [
                {"name": s.name, "plane": s.plane, "element_count": len(s.elements)}
                for s in doc.sketches
            ]
            tree["hybrid_bodies"] = [
                {
                    "name": hb.name,
                    "features": [{"name": f.name, "type": f.feature_type} for f in hb.features],
                }
                for hb in doc.hybrid_bodies
            ]
        elif doc.doc_type == DocumentType.PRODUCT:
            tree["components"] = [
                {"name": c.name, "path": c.document_path, "fixed": c.fixed} for c in doc.components
            ]
        elif doc.doc_type == DocumentType.DRAWING:
            tree["sheets"] = []
            for sheet in doc.sheets:
                sheet_info = {
                    "name": sheet.name,
                    "views": [{"name": v.name, "type": v.view_type} for v in sheet.views],
                }
                tree["sheets"].append(sheet_info)
        return tree

    def get_parameters(self) -> dict[str, Any]:
        doc = self._require_document()
        return {"document": doc.name, "parameters": doc.parameters}

    def set_parameter(self, name: str, value: Any) -> dict[str, Any]:
        doc = self._require_document()
        old_value = doc.parameters.get(name)
        doc.parameters[name] = value
        self._push_undo(f"set_param_{name}")
        return {"name": name, "old_value": old_value, "new_value": value}

    def undo(self) -> dict[str, str]:
        self._require_connection()
        if not self._undo_stack:
            return {"status": "nothing_to_undo"}
        action = self._undo_stack.pop()
        self._redo_stack.append(action)
        return {"status": "undone", "action": action}

    def redo(self) -> dict[str, str]:
        self._require_connection()
        if not self._redo_stack:
            return {"status": "nothing_to_redo"}
        action = self._redo_stack.pop()
        self._undo_stack.append(action)
        return {"status": "redone", "action": action}

    # ── Sketch Operations ────────────────────────────────────────────────

    def create_sketch(self, plane: str = "XY") -> dict[str, Any]:
        doc = self._require_document(DocumentType.PART)
        name = f"Sketch.{len(doc.sketches) + 1}"
        sketch = Sketch(name=name, plane=plane)
        doc.sketches.append(sketch)
        self._active_sketch = sketch
        self._push_undo(f"create_sketch_{name}")
        return {"name": name, "plane": plane, "status": "editing"}

    def close_sketch(self) -> dict[str, str]:
        if self._active_sketch is None:
            raise RuntimeError("No active sketch to close.")
        name = self._active_sketch.name
        self._active_sketch.closed = True
        self._active_sketch = None
        return {"name": name, "status": "closed"}

    def _require_sketch(self) -> Sketch:
        if self._active_sketch is None:
            raise RuntimeError("No active sketch. Create or edit a sketch first.")
        return self._active_sketch

    def sketch_line(self, x1: float, y1: float, x2: float, y2: float) -> dict[str, Any]:
        sketch = self._require_sketch()
        elem = sketch.add_element("line", x1=x1, y1=y1, x2=x2, y2=y2)
        return {"id": elem.id, "type": "line", "from": [x1, y1], "to": [x2, y2]}

    def sketch_circle(self, cx: float, cy: float, radius: float) -> dict[str, Any]:
        sketch = self._require_sketch()
        elem = sketch.add_element("circle", cx=cx, cy=cy, radius=radius)
        return {"id": elem.id, "type": "circle", "center": [cx, cy], "radius": radius}

    def sketch_rectangle(self, x: float, y: float, width: float, height: float) -> dict[str, Any]:
        sketch = self._require_sketch()
        lines = [
            sketch.add_element("line", x1=x, y1=y, x2=x + width, y2=y),
            sketch.add_element("line", x1=x + width, y1=y, x2=x + width, y2=y + height),
            sketch.add_element("line", x1=x + width, y1=y + height, x2=x, y2=y + height),
            sketch.add_element("line", x1=x, y1=y + height, x2=x, y2=y),
        ]
        return {
            "ids": [el.id for el in lines],
            "type": "rectangle",
            "origin": [x, y],
            "size": [width, height],
        }

    def sketch_arc(
        self, cx: float, cy: float, radius: float, start_angle: float, end_angle: float
    ) -> dict[str, Any]:
        sketch = self._require_sketch()
        elem = sketch.add_element(
            "arc", cx=cx, cy=cy, radius=radius, start_angle=start_angle, end_angle=end_angle
        )
        return {
            "id": elem.id,
            "type": "arc",
            "center": [cx, cy],
            "radius": radius,
            "angles": [start_angle, end_angle],
        }

    def sketch_spline(self, points: list[tuple[float, float]]) -> dict[str, Any]:
        sketch = self._require_sketch()
        elem = sketch.add_element("spline", points=points)
        return {"id": elem.id, "type": "spline", "point_count": len(points)}

    def sketch_point(self, x: float, y: float) -> dict[str, Any]:
        sketch = self._require_sketch()
        elem = sketch.add_element("point", x=x, y=y)
        return {"id": elem.id, "type": "point", "position": [x, y]}

    def sketch_constraint(
        self, constraint_type: str, elements: list[str], value: float | None = None
    ) -> dict[str, Any]:
        sketch = self._require_sketch()
        c = Constraint(
            id=f"cst_{len(sketch.constraints) + 1}",
            constraint_type=constraint_type,
            elements=elements,
            value=value,
        )
        sketch.constraints.append(c)
        return {"id": c.id, "type": constraint_type, "elements": elements, "value": value}

    def sketch_fillet(self, element1: str, element2: str, radius: float) -> dict[str, Any]:
        sketch = self._require_sketch()
        elem = sketch.add_element("fillet_2d", element1=element1, element2=element2, radius=radius)
        return {"id": elem.id, "type": "fillet_2d", "radius": radius}

    def sketch_trim(self, element: str, point_x: float, point_y: float) -> dict[str, Any]:
        self._require_sketch()
        return {"element": element, "trim_point": [point_x, point_y], "status": "trimmed"}

    # ── Part Design Operations ───────────────────────────────────────────

    def _get_body(self, body_name: str | None = None) -> Body:
        doc = self._require_document(DocumentType.PART)
        if body_name:
            for b in doc.bodies:
                if b.name == body_name:
                    return b
            raise RuntimeError(f"Body '{body_name}' not found.")
        return doc.bodies[0]

    def _find_sketch(self, sketch_name: str) -> Sketch:
        doc = self._require_document(DocumentType.PART)
        for s in doc.sketches:
            if s.name == sketch_name:
                return s
        raise RuntimeError(f"Sketch '{sketch_name}' not found.")

    def create_pad(
        self,
        sketch_name: str,
        depth: float,
        direction: str = "normal",
        symmetric: bool = False,
        body_name: str | None = None,
    ) -> dict[str, Any]:
        self._find_sketch(sketch_name)
        body = self._get_body(body_name)
        name = f"Pad.{sum(1 for f in body.features if f.feature_type == 'Pad') + 1}"
        feat = Feature(
            name=name,
            feature_type="Pad",
            params={
                "sketch": sketch_name,
                "depth": depth,
                "direction": direction,
                "symmetric": symmetric,
            },
        )
        body.features.append(feat)
        self._push_undo(f"create_pad_{name}")
        return {"name": name, "sketch": sketch_name, "depth": depth}

    def create_pocket(
        self,
        sketch_name: str,
        depth: float,
        direction: str = "normal",
        body_name: str | None = None,
    ) -> dict[str, Any]:
        self._find_sketch(sketch_name)
        body = self._get_body(body_name)
        name = f"Pocket.{sum(1 for f in body.features if f.feature_type == 'Pocket') + 1}"
        feat = Feature(
            name=name,
            feature_type="Pocket",
            params={"sketch": sketch_name, "depth": depth, "direction": direction},
        )
        body.features.append(feat)
        self._push_undo(f"create_pocket_{name}")
        return {"name": name, "sketch": sketch_name, "depth": depth}

    def create_shaft(
        self,
        sketch_name: str,
        angle: float = 360.0,
        axis: str = "sketch_axis",
        body_name: str | None = None,
    ) -> dict[str, Any]:
        self._find_sketch(sketch_name)
        body = self._get_body(body_name)
        name = f"Shaft.{sum(1 for f in body.features if f.feature_type == 'Shaft') + 1}"
        feat = Feature(
            name=name,
            feature_type="Shaft",
            params={"sketch": sketch_name, "angle": angle, "axis": axis},
        )
        body.features.append(feat)
        self._push_undo(f"create_shaft_{name}")
        return {"name": name, "sketch": sketch_name, "angle": angle}

    def create_groove(
        self,
        sketch_name: str,
        angle: float = 360.0,
        axis: str = "sketch_axis",
        body_name: str | None = None,
    ) -> dict[str, Any]:
        self._find_sketch(sketch_name)
        body = self._get_body(body_name)
        name = f"Groove.{sum(1 for f in body.features if f.feature_type == 'Groove') + 1}"
        feat = Feature(
            name=name,
            feature_type="Groove",
            params={"sketch": sketch_name, "angle": angle, "axis": axis},
        )
        body.features.append(feat)
        self._push_undo(f"create_groove_{name}")
        return {"name": name, "sketch": sketch_name, "angle": angle}

    def create_fillet(
        self, edges: list[str], radius: float, body_name: str | None = None
    ) -> dict[str, Any]:
        body = self._get_body(body_name)
        name = f"EdgeFillet.{sum(1 for f in body.features if f.feature_type == 'EdgeFillet') + 1}"
        feat = Feature(
            name=name, feature_type="EdgeFillet", params={"edges": edges, "radius": radius}
        )
        body.features.append(feat)
        self._push_undo(f"create_fillet_{name}")
        return {"name": name, "radius": radius, "edge_count": len(edges)}

    def create_chamfer(
        self, edges: list[str], distance: float, angle: float = 45.0, body_name: str | None = None
    ) -> dict[str, Any]:
        body = self._get_body(body_name)
        name = f"Chamfer.{sum(1 for f in body.features if f.feature_type == 'Chamfer') + 1}"
        feat = Feature(
            name=name,
            feature_type="Chamfer",
            params={"edges": edges, "distance": distance, "angle": angle},
        )
        body.features.append(feat)
        self._push_undo(f"create_chamfer_{name}")
        return {"name": name, "distance": distance, "angle": angle}

    def create_shell(
        self,
        thickness: float,
        faces_to_remove: list[str] | None = None,
        body_name: str | None = None,
    ) -> dict[str, Any]:
        body = self._get_body(body_name)
        name = f"Shell.{sum(1 for f in body.features if f.feature_type == 'Shell') + 1}"
        feat = Feature(
            name=name,
            feature_type="Shell",
            params={"thickness": thickness, "faces_to_remove": faces_to_remove or []},
        )
        body.features.append(feat)
        self._push_undo(f"create_shell_{name}")
        return {"name": name, "thickness": thickness}

    def create_hole(
        self,
        x: float,
        y: float,
        diameter: float,
        depth: float,
        hole_type: str = "simple",
        body_name: str | None = None,
    ) -> dict[str, Any]:
        body = self._get_body(body_name)
        name = f"Hole.{sum(1 for f in body.features if f.feature_type == 'Hole') + 1}"
        feat = Feature(
            name=name,
            feature_type="Hole",
            params={"x": x, "y": y, "diameter": diameter, "depth": depth, "hole_type": hole_type},
        )
        body.features.append(feat)
        self._push_undo(f"create_hole_{name}")
        return {"name": name, "diameter": diameter, "depth": depth, "type": hole_type}

    def create_pattern_rectangular(
        self,
        feature_name: str,
        dir1_count: int,
        dir1_spacing: float,
        dir2_count: int = 1,
        dir2_spacing: float = 0.0,
        body_name: str | None = None,
    ) -> dict[str, Any]:
        body = self._get_body(body_name)
        name = f"RectPattern.{sum(1 for f in body.features if f.feature_type == 'RectPattern') + 1}"
        feat = Feature(
            name=name,
            feature_type="RectPattern",
            params={
                "feature": feature_name,
                "dir1": {"count": dir1_count, "spacing": dir1_spacing},
                "dir2": {"count": dir2_count, "spacing": dir2_spacing},
            },
        )
        body.features.append(feat)
        self._push_undo(f"create_rect_pattern_{name}")
        return {"name": name, "total_instances": dir1_count * dir2_count}

    def create_pattern_circular(
        self,
        feature_name: str,
        count: int,
        angle_spacing: float = 0.0,
        full_circle: bool = True,
        body_name: str | None = None,
    ) -> dict[str, Any]:
        body = self._get_body(body_name)
        name = f"CircPattern.{sum(1 for f in body.features if f.feature_type == 'CircPattern') + 1}"
        spacing = 360.0 / count if full_circle else angle_spacing
        feat = Feature(
            name=name,
            feature_type="CircPattern",
            params={"feature": feature_name, "count": count, "spacing": spacing},
        )
        body.features.append(feat)
        self._push_undo(f"create_circ_pattern_{name}")
        return {"name": name, "instances": count, "spacing": spacing}

    def create_mirror(
        self, feature_name: str, plane: str = "XY", body_name: str | None = None
    ) -> dict[str, Any]:
        body = self._get_body(body_name)
        name = f"Mirror.{sum(1 for f in body.features if f.feature_type == 'Mirror') + 1}"
        feat = Feature(
            name=name, feature_type="Mirror", params={"feature": feature_name, "plane": plane}
        )
        body.features.append(feat)
        self._push_undo(f"create_mirror_{name}")
        return {"name": name, "feature": feature_name, "plane": plane}

    def create_thickness(
        self, faces: list[str], offset: float, body_name: str | None = None
    ) -> dict[str, Any]:
        body = self._get_body(body_name)
        name = f"Thickness.{sum(1 for f in body.features if f.feature_type == 'Thickness') + 1}"
        feat = Feature(
            name=name, feature_type="Thickness", params={"faces": faces, "offset": offset}
        )
        body.features.append(feat)
        self._push_undo(f"create_thickness_{name}")
        return {"name": name, "offset": offset}

    def add_body(self, name: str | None = None) -> dict[str, str]:
        doc = self._require_document(DocumentType.PART)
        if name is None:
            name = f"Body.{len(doc.bodies) + 1}"
        doc.bodies.append(Body(name=name))
        return {"name": name, "status": "created"}

    def boolean_operation(self, body1: str, body2: str, operation: str = "add") -> dict[str, Any]:
        self._require_document(DocumentType.PART)
        self._push_undo(f"boolean_{operation}")
        return {"body1": body1, "body2": body2, "operation": operation, "status": "completed"}

    # ── Assembly Operations ──────────────────────────────────────────────

    def insert_component(self, document_path: str, name: str | None = None) -> dict[str, Any]:
        doc = self._require_document(DocumentType.PRODUCT)
        if name is None:
            name = document_path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].rsplit(".", 1)[0]
        comp = Component(name=name, document_path=document_path)
        doc.components.append(comp)
        self._push_undo(f"insert_{name}")
        return {"name": name, "path": document_path, "index": len(doc.components) - 1}

    def add_assembly_constraint(
        self,
        constraint_type: str,
        component1: str,
        element1: str,
        component2: str,
        element2: str,
        value: float | None = None,
    ) -> dict[str, Any]:
        doc = self._require_document(DocumentType.PRODUCT)
        cst_id = f"Cst.{sum(len(c.constraints) for c in doc.components) + 1}"
        cst_data = {
            "id": cst_id,
            "type": constraint_type,
            "comp1": component1,
            "elem1": element1,
            "comp2": component2,
            "elem2": element2,
            "value": value,
        }
        for comp in doc.components:
            if comp.name == component1:
                comp.constraints.append(cst_data)
                break
        self._push_undo(f"constraint_{constraint_type}")
        return cst_data

    def fix_component(self, component_name: str) -> dict[str, str]:
        doc = self._require_document(DocumentType.PRODUCT)
        for comp in doc.components:
            if comp.name == component_name:
                comp.fixed = True
                return {"component": component_name, "status": "fixed"}
        raise RuntimeError(f"Component '{component_name}' not found.")

    def move_component(self, component_name: str, x: float, y: float, z: float) -> dict[str, Any]:
        doc = self._require_document(DocumentType.PRODUCT)
        for comp in doc.components:
            if comp.name == component_name:
                comp.position = (x, y, z)
                return {"component": component_name, "position": [x, y, z]}
        raise RuntimeError(f"Component '{component_name}' not found.")

    def get_bom(self) -> dict[str, Any]:
        doc = self._require_document(DocumentType.PRODUCT)
        items = [{"name": c.name, "path": c.document_path, "quantity": 1} for c in doc.components]
        return {"document": doc.name, "items": items, "total_parts": len(items)}

    # ── Drawing Operations ───────────────────────────────────────────────

    def _get_sheet(self, sheet_name: str | None = None) -> DrawingSheet:
        doc = self._require_document(DocumentType.DRAWING)
        if sheet_name:
            for s in doc.sheets:
                if s.name == sheet_name:
                    return s
            raise RuntimeError(f"Sheet '{sheet_name}' not found.")
        return doc.sheets[0]

    def create_view(
        self,
        view_type: str,
        source_doc: str | None = None,
        sheet_name: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        sheet = self._get_sheet(sheet_name)
        name = f"{view_type}View.{len(sheet.views) + 1}"
        view = DrawingView(name=name, view_type=view_type, params={"source": source_doc, **params})
        sheet.views.append(view)
        self._push_undo(f"create_view_{name}")
        return {"name": name, "type": view_type, "sheet": sheet.name}

    def add_drawing_dimension(
        self, view_name: str, dim_type: str, elements: list[str], sheet_name: str | None = None
    ) -> dict[str, Any]:
        sheet = self._get_sheet(sheet_name)
        for view in sheet.views:
            if view.name == view_name:
                dim = {
                    "id": f"dim_{len(view.dimensions) + 1}",
                    "type": dim_type,
                    "elements": elements,
                }
                view.dimensions.append(dim)
                return dim
        raise RuntimeError(f"View '{view_name}' not found.")

    def add_annotation(
        self, view_name: str, text: str, x: float, y: float, sheet_name: str | None = None
    ) -> dict[str, Any]:
        sheet = self._get_sheet(sheet_name)
        for view in sheet.views:
            if view.name == view_name:
                ann = {"id": f"ann_{len(view.annotations) + 1}", "text": text, "position": [x, y]}
                view.annotations.append(ann)
                return ann
        raise RuntimeError(f"View '{view_name}' not found.")

    # ── Surface Design Operations ────────────────────────────────────────

    def _get_hybrid_body(self, name: str | None = None) -> Body:
        doc = self._require_document(DocumentType.PART)
        if name:
            for hb in doc.hybrid_bodies:
                if hb.name == name:
                    return hb
            raise RuntimeError(f"Geometrical Set '{name}' not found.")
        if not doc.hybrid_bodies:
            hb = Body(name="Geometrical Set.1")
            doc.hybrid_bodies.append(hb)
        return doc.hybrid_bodies[0]

    def create_surface(
        self,
        surface_type: str,
        sketch_name: str | None = None,
        hybrid_body: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        hb = self._get_hybrid_body(hybrid_body)
        name = f"{surface_type}.{sum(1 for f in hb.features if f.feature_type == surface_type) + 1}"
        feat = Feature(
            name=name, feature_type=surface_type, params={"sketch": sketch_name, **params}
        )
        hb.features.append(feat)
        self._push_undo(f"create_surface_{name}")
        return {"name": name, "type": surface_type}

    def surface_operation(
        self, operation: str, elements: list[str], hybrid_body: str | None = None, **params: Any
    ) -> dict[str, Any]:
        hb = self._get_hybrid_body(hybrid_body)
        name = f"{operation}.{sum(1 for f in hb.features if f.feature_type == operation) + 1}"
        feat = Feature(name=name, feature_type=operation, params={"elements": elements, **params})
        hb.features.append(feat)
        self._push_undo(f"surface_op_{name}")
        return {"name": name, "operation": operation, "elements": elements}

    # ── Measurement Operations ───────────────────────────────────────────

    def measure_distance(self, element1: str, element2: str) -> dict[str, Any]:
        self._require_document()
        dist = 42.5  # mock
        return {"element1": element1, "element2": element2, "distance": dist, "unit": "mm"}

    def measure_angle(self, element1: str, element2: str) -> dict[str, Any]:
        self._require_document()
        return {"element1": element1, "element2": element2, "angle": 90.0, "unit": "deg"}

    def measure_properties(self, element: str) -> dict[str, Any]:
        self._require_document()
        return {
            "element": element,
            "area": 1256.64,
            "volume": 5235.99,
            "center_of_gravity": [0.0, 0.0, 25.0],
            "unit_length": "mm",
        }

    # ── Macro Execution ──────────────────────────────────────────────────

    def execute_macro(self, code: str, language: str = "VBScript") -> dict[str, Any]:
        self._require_connection()
        self._push_undo("execute_macro")
        return {"status": "executed", "language": language, "code_length": len(code)}


def get_catia() -> CATIAConnection:
    """Get or create the global CATIA connection singleton."""
    global _catia_instance
    if _catia_instance is None:
        _catia_instance = CATIAConnection()
    return _catia_instance


def reset_catia() -> None:
    """Reset the global instance (for testing)."""
    global _catia_instance
    _catia_instance = None
