"""
DIS v1.1 — Step 3: Concrete Stub Implementations (Still No Logic)

These are minimal concrete classes that satisfy the Protocol interfaces.
They exist ONLY so the pipeline skeleton can be instantiated and type-checked.

All methods still raise NotImplementedError().
No real processing is performed.
"""

from .contracts import (
    RawDocument,
    ReconstructedStructure,
    AssetRecoveryResult,
    AssemblyInput,
)
from .pipeline import (
    IngestionStub,
    StructuralRecoveryStub,
    AssetRecoveryStub,
    DocumentAssemblyStub,
)
from .schema import StructuredDocument


class FakeIngestionStub(IngestionStub):
    """Minimal concrete stub for Layer 1. Contains zero logic."""

    def process(self, pdf_source: bytes | str) -> RawDocument:
        raise NotImplementedError("FakeIngestionStub.process() is a Step 3 skeleton only.")


class FakeStructuralRecoveryStub(StructuralRecoveryStub):
    """Minimal concrete stub for Layer 2."""

    def process(self, raw: RawDocument) -> ReconstructedStructure:
        raise NotImplementedError("FakeStructuralRecoveryStub.process() is a Step 3 skeleton only.")


class FakeAssetRecoveryStub(AssetRecoveryStub):
    """Minimal concrete stub for Layer 3."""

    def process(
        self,
        raw: RawDocument,
        structure: ReconstructedStructure,
    ) -> AssetRecoveryResult:
        raise NotImplementedError("FakeAssetRecoveryStub.process() is a Step 3 skeleton only.")


class FakeAssemblyStub(DocumentAssemblyStub):
    """Minimal concrete stub for Layer 4."""

    def process(self, assembly_input: AssemblyInput) -> StructuredDocument:
        raise NotImplementedError("FakeAssemblyStub.process() is a Step 3 skeleton only.")
