"""
Document Intelligence Service (DIS)
Phase 3 Implementation - Frozen Architecture

This package implements the Document Recovery System only.
It produces StructuredDocument (MCDM) as the single canonical output.
"""

from .schema import (
    StructuredDocument,
    DocumentMeta,
    ChapterNode,
    ContentBlock,
    Asset,
    AssetType,
    CrossReference,
    Provenance,
    IntegrityManifest,
)
from .validation import run_hard_validation_gates
from .contracts import (
    RawDocument,
    RawElement,
    RawPage,
    ReconstructedStructure,
    AssetRecoveryResult,
    AssemblyInput,
)
from .pipeline import (
    DocumentIntelligencePipeline,
    IngestionStub,
    StructuralRecoveryStub,
    AssetRecoveryStub,
    DocumentAssemblyStub,
)
from .stubs import (
    FakeIngestionStub,
    FakeStructuralRecoveryStub,
    FakeAssetRecoveryStub,
    FakeAssemblyStub,
)
from .layer1.ingestion import DocumentIngestion
from .layer2.contracts import (
    StructuralRecoveryInput,
    ReconstructedStructure,
    StructuralRecoveryOutput,
    StructuralRecovery,
)

__all__ = [
    "StructuredDocument",
    "DocumentMeta",
    "ChapterNode",
    "ContentBlock",
    "Asset",
    "AssetType",
    "CrossReference",
    "Provenance",
    "IntegrityManifest",
    "run_hard_validation_gates",
    "RawDocument",
    "RawElement",
    "RawPage",
    "ReconstructedStructure",
    "AssetRecoveryResult",
    "AssemblyInput",
    "DocumentIntelligencePipeline",
    "IngestionStub",
    "StructuralRecoveryStub",
    "AssetRecoveryStub",
    "DocumentAssemblyStub",
    "FakeIngestionStub",
    "FakeStructuralRecoveryStub",
    "FakeAssetRecoveryStub",
    "FakeAssemblyStub",
    "DocumentIngestion",
    "StructuralRecoveryInput",
    "StructuralRecoveryOutput",
    "StructuralRecovery",
]
