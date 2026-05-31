"""
DIS v1.1 - Frozen MCDM Schema Implementation (Phase 3 - Step 1)

This module defines the canonical data model for StructuredDocument.

CRITICAL CONSTRAINTS (Never Violate):
- Zero semantic / knowledge fields (no Concept, Chunk, Importance, etc.)
- All objects must carry complete Provenance
- All references must use stable IDs (no bare bbox/page references)
- extra='forbid' is enforced to prevent leakage of non-canonical fields
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


# =============================================================================
# Core Primitives
# =============================================================================

class AssetType(str, Enum):
    """Supported asset types in v1."""
    FIGURE = "figure"
    TABLE = "table"
    FORMULA = "formula"
    DIAGRAM = "diagram"


class Provenance(BaseModel):
    """Full traceability record for any recoverable element."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_page: int = Field(..., ge=1, description="1-based page number in original PDF")
    bbox: tuple[float, float, float, float] = Field(
        ..., description="Bounding box (x0, y0, x1, y1) in PDF coordinate space"
    )
    recovered_by: str = Field(..., description="Stage or component that produced this element")
    confidence: float = Field(..., ge=0.0, le=1.0)
    recovery_method: str = Field(..., description="e.g. 'ocr', 'layout_analysis', 'rule_based', 'model_inference'")
    model_version: str | None = None
    notes: str | None = None  # Only for quality/degradation notes, never semantics


class DocumentMeta(BaseModel):
    """Identity and processing metadata of the source document."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    document_id: UUID = Field(default_factory=uuid4)
    source_filename: str
    total_pages: int = Field(..., ge=1)
    language: str = Field(default="zh-CN")
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    dis_version: str = Field(default="1.1.0")
    processing_config_hash: str | None = None  # For reproducibility


# =============================================================================
# Structure
# =============================================================================

class ChapterNode(BaseModel):
    """Recursive chapter/section tree. Part of the canonical structure."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID = Field(default_factory=uuid4)
    title: str
    level: int = Field(..., ge=1)
    page_start: int = Field(..., ge=1)
    page_end: int = Field(..., ge=1)
    children: list[ChapterNode] = Field(default_factory=list)

    provenance: Provenance


# =============================================================================
# Content
# =============================================================================

class ContentBlock(BaseModel):
    """Logical content block in reading order (no semantic interpretation)."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID = Field(default_factory=uuid4)
    type: Literal["paragraph", "heading", "list_item", "caption", "formula_line", "other"]
    text: str | None = None
    page: int = Field(..., ge=1)
    bbox: tuple[float, float, float, float]

    # References to assets (must use stable IDs)
    asset_ids: list[UUID] = Field(default_factory=list)

    provenance: Provenance


# =============================================================================
# Assets
# =============================================================================

class Asset(BaseModel):
    """Canonical representation of a recovered visual/structural asset."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID = Field(default_factory=uuid4)
    type: AssetType
    page: int = Field(..., ge=1)
    bbox: tuple[float, float, float, float]

    # Basic recovered information (structural + spatial only)
    caption: str | None = None
    label: str | None = None          # e.g. "图 3-2", "表 2.1"
    position_semantics: str | None = None  # e.g. "left of text", "below formula"

    # Type-specific structural recovery (no interpretation)
    table_structure: dict | None = None   # Raw row/col data if applicable
    formula_structure: str | None = None  # LaTeX or symbol sequence if applicable
    diagram_elements: list[dict] | None = None

    # References back to content that mentions this asset
    referenced_by_block_ids: list[UUID] = Field(default_factory=list)

    provenance: Provenance


# =============================================================================
# Cross References
# =============================================================================

class CrossReference(BaseModel):
    """Explicit cross-reference recovered from the document."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID = Field(default_factory=uuid4)
    reference_type: str  # "see_figure", "as_shown_in_table", "equation", etc.

    # Must use stable IDs as primary reference
    source_block_id: UUID | None = None
    target_asset_id: UUID | None = None
    target_section_id: UUID | None = None

    # Fallback provenance only (never primary)
    source_page: int
    source_bbox: tuple[float, float, float, float]

    is_fallback: bool = False
    fallback_reason: str | None = None

    provenance: Provenance


# =============================================================================
# Integrity & Final Document
# =============================================================================

class IntegrityManifest(BaseModel):
    """Objective statement about recovery quality and completeness."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    structure_completeness: float = Field(..., ge=0.0, le=1.0)
    asset_coverage: float = Field(..., ge=0.0, le=1.0)
    cross_reference_coverage: float = Field(..., ge=0.0, le=1.0)

    missing_pages: list[int] = Field(default_factory=list)
    degraded_elements: list[str] = Field(default_factory=list)  # e.g. "page_47_ocr_low_quality"

    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    notes: str | None = None


class StructuredDocument(BaseModel):
    """
    The single canonical output of DIS.

    This is the final, self-describing truth of the recovered document.
    It must never contain any knowledge engineering artifacts.
    """
    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    schema_version: Literal["1.1.0"] = "1.1.0"
    meta: DocumentMeta

    structure: list[ChapterNode] = Field(default_factory=list)
    content_blocks: list[ContentBlock] = Field(default_factory=list)
    assets: list[Asset] = Field(default_factory=list)
    cross_references: list[CrossReference] = Field(default_factory=list)

    provenance: Provenance  # Document-level provenance
    integrity: IntegrityManifest

    # ==================================================================
    # Hard Validation Gates (Step 5)
    # ==================================================================
    @field_validator("content_blocks", "assets", "cross_references", "structure", mode="before")
    @classmethod
    def _forbid_semantic_fields(cls, v: list) -> list:
        """Prevent accidental injection of knowledge engineering fields."""
        forbidden_keywords = {
            "concept", "knowledge", "chunk", "embedding", "importance",
            "difficulty", "teaching", "summary", "interpretation", "semantic"
        }

        if not isinstance(v, list):
            return v

        for item in v:
            if isinstance(item, dict):
                for key in item.keys():
                    if any(kw in key.lower() for kw in forbidden_keywords):
                        raise ValueError(
                            f"Forbidden semantic field detected: '{key}'. "
                            "StructuredDocument must contain zero knowledge engineering content."
                        )
        return v

    def validate_output_contract(self) -> None:
        """
        Step 5 - Hard Validation Gate.
        Must be called before returning any StructuredDocument.
        """
        # 1. No semantic leakage
        # (already partially enforced by validator above + extra='forbid')

        # 2. All references must be based on stable IDs (basic check)
        asset_ids = {a.id for a in self.assets}
        block_ids = {b.id for b in self.content_blocks}
        chapter_ids = {c.id for c in self._flatten_chapters(self.structure)}

        for ref in self.cross_references:
            if ref.target_asset_id and ref.target_asset_id not in asset_ids:
                raise ValueError(f"Broken reference: target_asset_id {ref.target_asset_id} not found")
            if ref.source_block_id and ref.source_block_id not in block_ids:
                raise ValueError(f"Broken reference: source_block_id {ref.source_block_id} not found")

        # 3. Provenance coverage (basic)
        if not self.provenance:
            raise ValueError("Document-level provenance is missing")

        # More comprehensive checks can be added in later steps

    @staticmethod
    def _flatten_chapters(nodes: list[ChapterNode]) -> list[ChapterNode]:
        result = []
        for node in nodes:
            result.append(node)
            result.extend(StructuredDocument._flatten_chapters(node.children))
        return result
