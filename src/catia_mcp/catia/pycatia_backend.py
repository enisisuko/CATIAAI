"""Real CATIA backend using the pycatia open-source library.

pycatia (https://github.com/evereux/pycatia) provides a comprehensive Python
wrapper around the CATIA V5 COM automation API. This module maps our
CATIAConnection interface to pycatia API calls.

Only loaded on Windows when pycatia is installed and CATIA is running.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

PYCATIA_AVAILABLE = False
try:
    from pycatia import catia  # noqa: F401

    PYCATIA_AVAILABLE = True
    logger.info("pycatia library loaded successfully")
except ImportError:
    logger.info("pycatia not available — will use mock or direct COM")


class PyCATIABackend:
    """CATIA automation backend powered by pycatia (evereux/pycatia).

    Maps high-level operations to pycatia's typed API, which wraps
    the CATIA V5 COM objects with proper Python classes.

    Reference: https://pycatia.readthedocs.io/
    """

    def __init__(self) -> None:
        self._app: Any = None
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self) -> dict[str, Any]:
        if not PYCATIA_AVAILABLE:
            raise RuntimeError("pycatia is not installed. pip install pycatia")
        try:
            from pycatia import catia as catia_connect

            self._app = catia_connect()
            self._connected = True
            version = "V5"
            try:
                sc = self._app.system_configuration
                version = sc.version if sc else "V5"
            except Exception:
                pass
            return {"status": "connected", "mock": False, "backend": "pycatia", "version": version}
        except Exception as e:
            raise RuntimeError(f"Failed to connect via pycatia: {e}") from e

    def disconnect(self) -> None:
        self._app = None
        self._connected = False

    def _require_app(self) -> Any:
        if not self._connected or self._app is None:
            raise RuntimeError("Not connected to CATIA via pycatia")
        return self._app

    # ── Document Management ──────────────────────────────────────────

    def new_part(self, name: str | None = None) -> dict[str, Any]:
        app = self._require_app()
        documents = app.documents
        documents.add("Part")
        doc = app.active_document
        part_name = doc.name if doc else (name or "Part1")
        return {"name": part_name, "type": "CATPart"}

    def new_product(self, name: str | None = None) -> dict[str, Any]:
        app = self._require_app()
        app.documents.add("Product")
        doc = app.active_document
        return {"name": doc.name if doc else (name or "Product1"), "type": "CATProduct"}

    def new_drawing(self, name: str | None = None) -> dict[str, Any]:
        app = self._require_app()
        app.documents.add("Drawing")
        doc = app.active_document
        return {"name": doc.name if doc else (name or "Drawing1"), "type": "CATDrawing"}

    def open_document(self, path: str) -> dict[str, Any]:
        app = self._require_app()
        app.documents.open(path)
        doc = app.active_document
        return {"name": doc.name, "path": path}

    def save_document(self, path: str | None = None) -> dict[str, str]:
        app = self._require_app()
        doc = app.active_document
        if path:
            doc.save_as(path)
        else:
            doc.save()
        return {"status": "saved", "path": path or doc.full_name}

    def close_document(self) -> dict[str, str]:
        app = self._require_app()
        doc = app.active_document
        name = doc.name
        doc.close()
        return {"status": "closed", "name": name}

    def get_active_document_info(self) -> dict[str, Any]:
        app = self._require_app()
        doc = app.active_document
        info: dict[str, Any] = {
            "name": doc.name,
            "full_name": doc.full_name,
            "saved": doc.saved,
        }
        try:
            part = doc.part
            info["type"] = "CATPart"
            info["bodies_count"] = part.bodies.count
            info["has_part"] = True
        except Exception:
            try:
                product = doc.product
                info["type"] = "CATProduct"
                info["products_count"] = product.products.count
            except Exception:
                info["type"] = "CATDrawing"
        return info

    # ── Sketch Operations (pycatia sketcher_interfaces) ──────────────

    def create_sketch_on_plane(self, plane_name: str = "XY") -> dict[str, Any]:
        app = self._require_app()
        doc = app.active_document
        part = doc.part
        bodies = part.bodies
        body = bodies.item(1)

        planes = part.origin_elements
        plane_map = {
            "XY": planes.plane_xy,
            "YZ": planes.plane_yz,
            "XZ": planes.plane_zx,
        }
        ref_plane = plane_map.get(plane_name.upper())
        if ref_plane is None:
            ref_plane = plane_map["XY"]

        reference = part.create_reference_from_object(ref_plane)
        sketches = body.sketches
        sketch = sketches.add(reference)
        return {"name": sketch.name, "plane": plane_name, "status": "editing"}

    def sketch_create_line(self, x1: float, y1: float, x2: float, y2: float) -> dict[str, Any]:
        app = self._require_app()
        doc = app.active_document
        sketch = doc.part.bodies.item(1).sketches.item(doc.part.bodies.item(1).sketches.count)
        factory = sketch.open_edition()
        factory.create_line(x1, y1, x2, y2)
        sketch.close_edition()
        return {"type": "line", "from": [x1, y1], "to": [x2, y2]}

    def sketch_create_circle(self, cx: float, cy: float, radius: float) -> dict[str, Any]:
        app = self._require_app()
        doc = app.active_document
        part = doc.part
        sketch = part.bodies.item(1).sketches.item(part.bodies.item(1).sketches.count)
        factory = sketch.open_edition()
        factory.create_closed_circle(cx, cy, radius)
        sketch.close_edition()
        return {"type": "circle", "center": [cx, cy], "radius": radius}

    # ── Part Design (pycatia part_interfaces) ────────────────────────

    def create_pad(self, sketch_name: str, depth: float) -> dict[str, Any]:
        app = self._require_app()
        doc = app.active_document
        part = doc.part
        body = part.bodies.item(1)

        sketches = body.sketches
        sketch = None
        for i in range(1, sketches.count + 1):
            s = sketches.item(i)
            if s.name == sketch_name:
                sketch = s
                break
        if sketch is None:
            raise RuntimeError(f"Sketch '{sketch_name}' not found")

        shape_factory = part.shape_factory
        pad = shape_factory.add_new_pad(sketch, depth)
        part.update()
        return {"name": pad.name, "sketch": sketch_name, "depth": depth}

    def create_pocket(self, sketch_name: str, depth: float) -> dict[str, Any]:
        app = self._require_app()
        doc = app.active_document
        part = doc.part
        body = part.bodies.item(1)
        sketches = body.sketches

        sketch = None
        for i in range(1, sketches.count + 1):
            s = sketches.item(i)
            if s.name == sketch_name:
                sketch = s
                break
        if sketch is None:
            raise RuntimeError(f"Sketch '{sketch_name}' not found")

        shape_factory = part.shape_factory
        pocket = shape_factory.add_new_pocket(sketch, depth)
        part.update()
        return {"name": pocket.name, "sketch": sketch_name, "depth": depth}

    def create_fillet(self, radius: float) -> dict[str, Any]:
        """Create fillet on selected edges. Edges must be pre-selected via CATIA Selection."""
        app = self._require_app()
        doc = app.active_document
        part = doc.part
        shape_factory = part.shape_factory
        fillet = shape_factory.add_new_edge_fillet_with_varying_radius(
            radius,
            1,  # catConstantRadius
        )
        part.update()
        return {"name": fillet.name, "radius": radius}

    def create_chamfer(self, distance: float) -> dict[str, Any]:
        app = self._require_app()
        doc = app.active_document
        part = doc.part
        shape_factory = part.shape_factory
        chamfer = shape_factory.add_new_chamfer(distance, 0, 45.0)
        part.update()
        return {"name": chamfer.name, "distance": distance}

    # ── Measurement (pycatia spa_interfaces) ─────────────────────────

    def measure_inertia(self) -> dict[str, Any]:
        """Measure mass/inertia of the active part using pycatia spa_interfaces."""
        app = self._require_app()
        doc = app.active_document
        part = doc.part

        try:
            spa = doc.spa_workbench()
            ref = part.create_reference_from_object(part.bodies.item(1))
            measurable = spa.get_measurable(ref)
            return {
                "area": measurable.area,
                "volume": measurable.volume,
                "center_of_gravity": list(measurable.get_cog()),
            }
        except Exception as e:
            return {"error": str(e), "note": "Measurement requires a solid body"}

    # ── Feature Tree ─────────────────────────────────────────────────

    def get_feature_tree(self) -> dict[str, Any]:
        app = self._require_app()
        doc = app.active_document
        tree: dict[str, Any] = {"document": doc.name}
        try:
            part = doc.part
            tree["type"] = "CATPart"
            tree["bodies"] = []
            for i in range(1, part.bodies.count + 1):
                body = part.bodies.item(i)
                body_info: dict[str, Any] = {"name": body.name, "features": []}
                try:
                    shapes = body.shapes
                    for j in range(1, shapes.count + 1):
                        shape = shapes.item(j)
                        body_info["features"].append({"name": shape.name})
                except Exception:
                    pass
                tree["bodies"].append(body_info)
        except Exception:
            try:
                product = doc.product
                tree["type"] = "CATProduct"
                tree["components"] = []
                for i in range(1, product.products.count + 1):
                    p = product.products.item(i)
                    tree["components"].append({"name": p.name})
            except Exception:
                tree["type"] = "unknown"
        return tree

    # ── Parameters ───────────────────────────────────────────────────

    def get_parameters(self) -> dict[str, Any]:
        app = self._require_app()
        doc = app.active_document
        part = doc.part
        params = part.parameters
        result: dict[str, Any] = {}
        for i in range(1, params.count + 1):
            try:
                p = params.item(i)
                result[p.name] = p.value
            except Exception:
                pass
        return result

    def set_parameter(self, name: str, value: Any) -> dict[str, Any]:
        app = self._require_app()
        doc = app.active_document
        part = doc.part
        params = part.parameters
        param = params.item(name)
        old_value = param.value
        param.value = value
        part.update()
        return {"name": name, "old_value": old_value, "new_value": value}

    # ── Assembly (pycatia product_interfaces) ────────────────────────

    def insert_component(self, path: str) -> dict[str, Any]:
        app = self._require_app()
        doc = app.active_document
        product = doc.product
        products = product.products
        component = products.add_component_from_files(path, "All")
        return {"name": component.name, "path": path}

    # ── VBA Macro Execution ──────────────────────────────────────────

    def execute_macro(self, code: str, language: str = "VBScript") -> dict[str, Any]:
        app = self._require_app()
        system_service = app.system_service
        result = system_service.evaluate(code, 1 if language == "CATScript" else 0, "CYCL")
        return {"status": "executed", "result": str(result) if result else None}
