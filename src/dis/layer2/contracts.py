"""
Layer 2: Structural Recovery — Contract Definitions

This file defines the precise data contracts that Layer 2 must produce.

These contracts are binding and must be respected by any future implementation.

Core Responsibilities of Layer 2 (Structural Recovery Only):
1. Recover logical reading order from raw visual elements.
2. Recover document hierarchy (chapters, sections, subsections).
3. Recover explicit and implicit cross-references between content and assets.
4. Produce stable structural identifiers that downstream layers can rely on.

Hard Constraints (from previous freezes):
- Layer 2 MUST NOT modify any objects from RawDocument (Mutation Rule).
- All new IDs (block_id, chapter_id, reference_id) must be globally stable.
- Cross references must primarily use stable IDs, not bbox/page.
- No semantic fields allowed (no concepts, no importance, no summaries).
- Output must be purely structural and referential.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..contracts import RawDocument
from ..schema import Provenance, ChapterNode, ContentBlock, CrossReference


class StructuralRecoveryInput(BaseModel):
    """
    Input contract for Layer 2.

    Layer 2 receives the complete RawDocument from Layer 1.
    It is forbidden from modifying any part of this input.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    raw_document: RawDocument


class ReconstructedStructure(BaseModel):
    """
    Primary Output Contract of Layer 2: Structural Recovery.

    This represents the recovered logical structure of the document
    based purely on visual and positional evidence + explicit textual references.

    It does NOT contain:
    - Semantic meaning of content
    - Knowledge concepts
    - Any form of chunking or RAG preparation
    - Importance or teaching value judgments

    It ONLY contains:
    - Hierarchical document structure
    - Logical reading order (as ContentBlocks)
    - Cross-document references (between text and assets)
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    # Document hierarchy recovered from visual + textual cues
    chapters: list[ChapterNode] = Field(
        default_factory=list,
        description="Recovered chapter/section tree. May be empty if no structure detected."
    )

    # Content in recovered logical reading order.
    # Each ContentBlock represents a minimal logical unit without semantic grouping.
    content_blocks: list[ContentBlock] = Field(
        default_factory=list,
        description="Elements arranged in logical reading order. Derived from RawDocument elements."
    )

    # All recovered cross-references (e.g. "see Figure 3-2", "as shown in Table 2.1")
    cross_references: list[CrossReference] = Field(
        default_factory=list,
        description="References between content and assets or other structural elements."
    )

    # Optional structural metadata (purely geometric/positional)
    structural_notes: str | None = Field(
        default=None,
        description="Non-semantic notes about structural recovery quality or ambiguities."
    )


class StructuralRecoveryOutput(BaseModel):
    """
    Full output of Layer 2.

    Contains the reconstructed structure and maintains traceability
    back to the original RawDocument via stable IDs and provenance.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    input: StructuralRecoveryInput
    structure: ReconstructedStructure

    # Layer 2 must guarantee:
    # - All ContentBlock ids are stable and unique
    # - All ChapterNode ids are stable and unique
    # - All CrossReference ids are stable and unique
    # - No RawElement from input has been mutated


# =============================================================================
# Layer 2 Interface (Contract)
# =============================================================================

class StructuralRecovery(Protocol):
    """
    Interface that any Layer 2 implementation must satisfy.

    This is the contract that higher layers and the pipeline will depend on.
    """

    def process(self, input: StructuralRecoveryInput) -> StructuralRecoveryOutput:
        """
        Perform structural recovery on the provided RawDocument.

        Must strictly follow:
        - Identity Persistence Rule
        - Mutation Rule (never modify input)
        - Reference Stability Rule
        - Zero semantic leakage
        """
        ...