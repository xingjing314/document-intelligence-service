"""
DIS v1.1 — 步骤 3：具体桩实现（仍无业务逻辑）

这些是最小的具体类，用于满足 Protocol 接口。
它们仅用于让流水线骨架能够被实例化和类型检查。

所有方法仍抛出 NotImplementedError()。
不执行任何真实处理。
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
    """Layer 1 的最小具体桩。包含零逻辑。"""

    def process(self, pdf_source: bytes | str) -> RawDocument:
        raise NotImplementedError("FakeIngestionStub.process() 仅为步骤 3 骨架。")


class FakeStructuralRecoveryStub(StructuralRecoveryStub):
    """Layer 2 的最小具体桩。"""

    def process(self, raw: RawDocument) -> ReconstructedStructure:
        raise NotImplementedError("FakeStructuralRecoveryStub.process() 仅为步骤 3 骨架。")


class FakeAssetRecoveryStub(AssetRecoveryStub):
    """Layer 3 的最小具体桩。"""

    def process(
        self,
        raw: RawDocument,
        structure: ReconstructedStructure,
    ) -> AssetRecoveryResult:
        raise NotImplementedError("FakeAssetRecoveryStub.process() 仅为步骤 3 骨架。")


class FakeAssemblyStub(DocumentAssemblyStub):
    """Layer 4 的最小具体桩。"""

    def process(self, assembly_input: AssemblyInput) -> StructuredDocument:
        raise NotImplementedError("FakeAssemblyStub.process() 仅为步骤 3 骨架。")
