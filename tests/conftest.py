"""Shared test fixtures for CATIA MCP tests."""

from __future__ import annotations

import pytest

from catia_mcp.catia.connection import CATIAConnection, DocumentType, reset_catia


@pytest.fixture(autouse=True)
def _reset_global():
    """Reset global CATIA instance between tests."""
    reset_catia()
    yield
    reset_catia()


@pytest.fixture
def catia() -> CATIAConnection:
    """Connected CATIA instance in mock mode."""
    conn = CATIAConnection()
    conn.connect()
    return conn


@pytest.fixture
def catia_with_part(catia: CATIAConnection) -> CATIAConnection:
    """CATIA with an active Part document."""
    catia.new_document(DocumentType.PART, "TestPart")
    return catia


@pytest.fixture
def catia_with_assembly(catia: CATIAConnection) -> CATIAConnection:
    """CATIA with an active Assembly (Product) document."""
    catia.new_document(DocumentType.PRODUCT, "TestAssembly")
    return catia


@pytest.fixture
def catia_with_drawing(catia: CATIAConnection) -> CATIAConnection:
    """CATIA with an active Drawing document."""
    catia.new_document(DocumentType.DRAWING, "TestDrawing")
    return catia
