"""
文档智能服务 (DIS)
阶段 3 实现 - 冻结架构

本包仅实现文档恢复系统。
它以 StructuredDocument (MCDM) 作为唯一的规范输出。
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
