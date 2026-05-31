"""
DIS v1.1 — Step 3: Pipeline Stub Implementation (Structural Skeleton Only)

CRITICAL RULES FOR THIS FILE:
- This file contains ONLY class and method skeletons.
- All methods MUST raise NotImplementedError().
- There is ZERO business logic, ZERO algorithms, ZERO data processing.
- This is a structural wiring of the frozen Layer Contracts only.
- NO intelligence of any kind is allowed in Step 3.

Purpose:
Provide the high-level data flow structure that will later be implemented,
while guaranteeing strict adherence to Step 2 contracts.
"""

from __future__ import annotations

from typing import Protocol

from .contracts import (
    RawDocument,
    ReconstructedStructure,
    AssetRecoveryResult,
    AssemblyInput,
)
from .schema import StructuredDocument
from .validation import run_hard_validation_gates


# =============================================================================
# Layer Stub Interfaces (for type safety and future implementation)
# =============================================================================

class IngestionStub(Protocol):
    """
    Layer 1 Stub: Document Ingestion

    Input : PDF (bytes or path)  — defined outside contracts for entry point
    Output: RawDocument
    """

    def process(self, pdf_source: bytes | str) -> RawDocument:
        """
        Stub method. Must raise NotImplementedError in Step 3.
        """
        raise NotImplementedError("Ingestion layer not implemented in Step 3 stub.")


class StructuralRecoveryStub(Protocol):
    """
    Layer 2 Stub: Structural Recovery

    Input : RawDocument
    Output: ReconstructedStructure
    """

    def process(self, raw: RawDocument) -> ReconstructedStructure:
        raise NotImplementedError("Structural Recovery layer not implemented in Step 3 stub.")


class AssetRecoveryStub(Protocol):
    """
    Layer 3 Stub: Asset Recovery

    Input : RawDocument + ReconstructedStructure (as per AssemblyInput needs)
    Output: AssetRecoveryResult
    """

    def process(
        self,
        raw: RawDocument,
        structure: ReconstructedStructure,
    ) -> AssetRecoveryResult:
        raise NotImplementedError("Asset Recovery layer not implemented in Step 3 stub.")


class DocumentAssemblyStub(Protocol):
    """
    Layer 4 Stub: Document Assembly

    Input : AssemblyInput (structure + assets + raw)
    Output: StructuredDocument (final MCDM)
    """

    def process(self, assembly_input: AssemblyInput) -> StructuredDocument:
        raise NotImplementedError("Document Assembly layer not implemented in Step 3 stub.")


# =============================================================================
# Main Pipeline Orchestrator (Skeleton)
# =============================================================================

class DocumentIntelligencePipeline:
    """
    Top-level pipeline skeleton.

    This class is responsible ONLY for wiring the four layer stubs
    according to the frozen contracts defined in Step 2.

    It must NOT contain any processing logic.
    """

    def __init__(
        self,
        ingestion: IngestionStub,
        structural_recovery: StructuralRecoveryStub,
        asset_recovery: AssetRecoveryStub,
        assembly: DocumentAssemblyStub,
    ):
        """
        Accepts injected stubs (Dependency Injection skeleton).
        In real implementation, concrete classes will be passed here.
        """
        self._ingestion = ingestion
        self._structural = structural_recovery
        self._asset = asset_recovery
        self._assembly = assembly

    def process(self, pdf_source: bytes | str) -> StructuredDocument:
        """
        High-level data flow skeleton.

        This method shows the exact contract flow:
        PDF → RawDocument → ReconstructedStructure → AssetRecoveryResult → StructuredDocument

        IMPORTANT:
        - This method contains NO logic.
        - It only demonstrates the structural wiring.
        - Validation gate is called at the end as a required hook.
        """
        # Step 1: Ingestion (Layer 1)
        raw_document: RawDocument = self._ingestion.process(pdf_source)

        # Step 2: Structural Recovery (Layer 2)
        reconstructed_structure: ReconstructedStructure = self._structural.process(raw_document)

        # Step 3: Asset Recovery (Layer 3)
        asset_result: AssetRecoveryResult = self._asset.process(
            raw_document, reconstructed_structure
        )

        # Prepare input for final assembly according to Step 2 contract
        assembly_input = AssemblyInput(
            structure=reconstructed_structure,
            assets=asset_result,
            raw_document=raw_document,
        )

        # Step 4: Document Assembly (Layer 4)
        structured_document: StructuredDocument = self._assembly.process(assembly_input)

        # Mandatory Validation Hook (from Step 1)
        # This must be called before returning any StructuredDocument.
        # The actual validation logic lives in validation.py and is NOT modified here.
        run_hard_validation_gates(structured_document)

        return structured_document
