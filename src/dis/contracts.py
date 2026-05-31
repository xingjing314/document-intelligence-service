"""
DIS v1.1 — Step 2: Layer Contract Definitions (Frozen)

This module defines ONLY the data contracts between layers.
It contains zero algorithms, zero business logic, and zero knowledge engineering concepts.

Purpose:
- Provide immutable structural definitions for data flowing between layers.
- Serve as the single source of truth for what each layer is allowed to produce and consume.
- Enforce Identity Persistence, Mutation Rules, and Reference Stability by design.

IMPORTANT:
- These are CONTRACTS, not implementations.
- No layer is allowed to mutate the structure of upstream contracts.
- All stable IDs must be respected across layers.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .schema import (
    Provenance,
    ChapterNode,
    ContentBlock,
    Asset,
    CrossReference,
    DocumentMeta,
)


# =============================================================================
# Layer 1 — Document Ingestion Contract
# =============================================================================

class RawElement(BaseModel):
    """
    Atomic element extracted from a single page.
    This is the smallest unit produced by Layer 1.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    element_id: UUID
    page: int = Field(..., ge=1)
    bbox: tuple[float, float, float, float]
    type: str  # "text", "image", "table_region", "formula_region", "line", etc.
    content: str | bytes | None = None
    confidence: float = Field(..., ge=0.0, le=1.0)

    provenance: Provenance


class RawPage(BaseModel):
    """
    All raw elements belonging to one physical page.

    Contains only raw geometric facts about the page and its elements.
    No logical structure or semantic grouping.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    page_number: int = Field(..., ge=1)

    # Pure page geometry (non-semantic spatial facts)
    width: float
    height: float
    rotation: float = 0.0   # Rotation angle in degrees (0, 90, 180, 270)

    elements: list[RawElement]


class RawDocument(BaseModel):
    """
    Layer 1 Output Contract

    This is the complete output of the Document Ingestion layer.
    It contains only raw, unprocessed atomic facts from the PDF.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    meta: DocumentMeta
    pages: list[RawPage]

    # ID Rule: All element_id in RawElement must be globally unique and stable
    # Mutation Rule: Layer 2+ MUST NOT modify any field inside RawElement or RawPage
    # Reference Rule: No cross references exist at this layer


# =============================================================================
# Layer 2 — Structural Recovery Contract
# =============================================================================

class ReconstructedStructure(BaseModel):
    """
    Layer 2 Output Contract

    Contains the recovered logical structure and reading order of the document.
    Does NOT contain visual asset details (those belong to Layer 3).
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    # Stable structure recovered from the document
    chapters: list[ChapterNode]

    # Content in logical reading order (derived from RawDocument)
    content_blocks: list[ContentBlock]

    # Cross references discovered during structural analysis
    cross_references: list[CrossReference]

    # ID Inheritance Rules (must be followed):
    # - ChapterNode.id must be stable and unique across the entire document
    # - ContentBlock.id must be stable and unique
    # - CrossReference.id must be stable and unique
    #
    # Mutation Rules:
    # - Layer 2 MUST NOT modify any RawElement from Layer 1
    # - Layer 2 may only create new objects (ChapterNode, ContentBlock, CrossReference)
    #
    # Reference Rules:
    # - All CrossReference must use stable IDs (block_id, section_id) as primary references
    # - bbox + page may only appear inside Provenance, never as primary reference


# =============================================================================
# Layer 3 — Asset Recovery Contract
# =============================================================================

class AssetRecoveryResult(BaseModel):
    """
    Layer 3 Output Contract

    Contains all recovered visual and structural assets with their spatial
    and structural information only.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    assets: list[Asset]

    # ID Inheritance Rules:
    # - Asset.id must be globally stable and unique
    # - Assets may reference ContentBlock.id (via referenced_by_block_ids)
    #
    # Mutation Rules:
    # - Layer 3 MUST NOT modify any object produced by Layer 1 or Layer 2
    # - Layer 3 only creates and populates Asset objects
    #
    # Reference Rules:
    # - All asset references in downstream layers must use Asset.id
    # - No asset may be referenced by bbox/page alone


# =============================================================================
# Layer 4 — Document Assembly Contract
# =============================================================================

class AssemblyInput(BaseModel):
    """
    Combined input required by Layer 4 (Document Assembly).

    This is not a layer output, but the agreed contract of what Layer 4 consumes.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    structure: ReconstructedStructure
    assets: AssetRecoveryResult
    raw_document: RawDocument  # Used only for document-level provenance and integrity checks


class DocumentAssemblyContract(BaseModel):
    """
    Layer 4 Output Contract

    Layer 4 is responsible only for assembling the final StructuredDocument.
    It does not create new knowledge — it only composes what previous layers produced.

    Final output must be a valid StructuredDocument (see schema.py).
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    # The only allowed output of the entire pipeline
    structured_document: "StructuredDocument"  # Forward reference

    # Assembly must enforce:
    # - All stable IDs from previous layers are preserved
    # - No new semantic fields are introduced
    # - All cross references use stable IDs
    # - Full provenance coverage


# =============================================================================
# Cross-Layer Consistency Rules (Must be satisfied by all layers)
# =============================================================================

"""
Global Rules (enforced by contract design):

1. Identity Persistence Rule
   - element_id (from RawElement) remains stable if referenced downstream.
   - block_id, chapter_id, asset_id, reference_id are globally stable once assigned.

2. Mutation Rule
   - No layer is allowed to mutate objects produced by previous layers.
   - Enrichment is only allowed by creating new objects that reference upstream IDs.

3. Reference Stability Rule
   - Primary references between objects MUST use stable IDs.
   - bbox + page is only permitted inside Provenance objects as supporting evidence.
   - Any fallback usage must be explicitly marked (is_fallback=True).

4. No Knowledge Leakage
   - None of these contracts may contain fields related to concepts, chunks,
     embeddings, importance, teaching value, or any form of semantic interpretation.
"""

# Rebuild forward references
DocumentAssemblyContract.model_rebuild()
