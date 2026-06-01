"""
DIS v1.1 — 步骤 3：流水线桩实现（仅结构骨架）

本文件的严格规则：
- 本文件仅包含类与方法骨架。
- 所有方法必须抛出 NotImplementedError()。
- 零业务逻辑、零算法、零数据处理。
- 仅为冻结的 Layer 契约进行结构化连接。
- 步骤 3 中不允许任何形式的智能处理。

目的：
提供后续将要实现的高层数据流结构，
同时保证严格遵守步骤 2 的契约。
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
    Layer 1 桩：文档摄取

    输入 : PDF（bytes 或路径）— 入口点在契约外定义
    输出: RawDocument
    """

    def process(self, pdf_source: bytes | str) -> RawDocument:
        """
        桩方法。步骤 3 中必须抛出 NotImplementedError。
        """
        raise NotImplementedError("摄取层在步骤 3 桩中未实现。")


class StructuralRecoveryStub(Protocol):
    """
    Layer 2 桩：结构恢复

    输入 : RawDocument
    输出: ReconstructedStructure
    """

    def process(self, raw: RawDocument) -> ReconstructedStructure:
        raise NotImplementedError("结构恢复层在步骤 3 桩中未实现。")


class AssetRecoveryStub(Protocol):
    """
    Layer 3 桩：资产恢复

    输入 : RawDocument + ReconstructedStructure（按 AssemblyInput 需求）
    输出: AssetRecoveryResult
    """

    def process(
        self,
        raw: RawDocument,
        structure: ReconstructedStructure,
    ) -> AssetRecoveryResult:
        raise NotImplementedError("资产恢复层在步骤 3 桩中未实现。")


class DocumentAssemblyStub(Protocol):
    """
    Layer 4 桩：文档组装

    输入 : AssemblyInput（结构 + 资产 + 原始数据）
    输出: StructuredDocument（最终 MCDM）
    """

    def process(self, assembly_input: AssemblyInput) -> StructuredDocument:
        raise NotImplementedError("文档组装层在步骤 3 桩中未实现。")


# =============================================================================
# Main Pipeline Orchestrator (Skeleton)
# =============================================================================

class DocumentIntelligencePipeline:
    """
    顶层流水线骨架。

    本类仅负责按照步骤 2 中冻结的契约，
    将四个层桩连接起来。

    不得包含任何处理逻辑。
    """

    def __init__(
        self,
        ingestion: IngestionStub,
        structural_recovery: StructuralRecoveryStub,
        asset_recovery: AssetRecoveryStub,
        assembly: DocumentAssemblyStub,
    ):
        """
        接受注入的桩（依赖注入骨架）。
        实际实现中会传入具体类。
        """
        self._ingestion = ingestion
        self._structural = structural_recovery
        self._asset = asset_recovery
        self._assembly = assembly

    def process(self, pdf_source: bytes | str) -> StructuredDocument:
        """
        高层数据流骨架。

        本方法展示精确的契约流：
        PDF → RawDocument → ReconstructedStructure → AssetRecoveryResult → StructuredDocument

        重要说明：
        - 本方法不包含任何逻辑。
        - 仅演示结构连接。
        - 末尾会调用验证门作为必需钩子。
        """
        # 步骤 1：摄取（Layer 1）
        raw_document: RawDocument = self._ingestion.process(pdf_source)

        # 步骤 2：结构恢复（Layer 2）
        reconstructed_structure: ReconstructedStructure = self._structural.process(raw_document)

        # 步骤 3：资产恢复（Layer 3）
        asset_result: AssetRecoveryResult = self._asset.process(
            raw_document, reconstructed_structure
        )

        # 按照步骤 2 契约准备最终组装输入
        assembly_input = AssemblyInput(
            structure=reconstructed_structure,
            assets=asset_result,
            raw_document=raw_document,
        )

        # 步骤 4：文档组装（Layer 4）
        structured_document: StructuredDocument = self._assembly.process(assembly_input)

        # 强制验证钩子（来自步骤 1）
        # 必须在返回任何 StructuredDocument 之前调用。
        # 实际验证逻辑位于 validation.py，此处不修改。
        run_hard_validation_gates(structured_document)

        return structured_document
