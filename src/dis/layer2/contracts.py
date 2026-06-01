"""
Layer 2: 结构恢复 — 契约定义

本文件定义 Layer 2 必须产生的精确数据契约。

这些契约具有约束力，任何未来实现都必须遵守。

Layer 2 的核心职责（仅限结构恢复）：
1. 从原始视觉元素中恢复逻辑阅读顺序。
2. 恢复文档层级（章节、小节、子小节）。
3. 恢复内容与资产之间的显式和隐式交叉引用。
4. 产生下游层可依赖的稳定结构标识符。

硬性约束（来自之前的冻结）：
- Layer 2 不得修改 RawDocument 中的任何对象（变更规则）。
- 所有新 ID（block_id、chapter_id、reference_id）必须全局稳定。
- 交叉引用必须优先使用稳定 ID，而非 bbox/page。
- 不允许语义字段（无概念、无重要性、无摘要）。
- 输出必须保持纯结构与引用性质。
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..contracts import RawDocument
from ..schema import Provenance, ChapterNode, ContentBlock, CrossReference


class StructuralRecoveryInput(BaseModel):
    """
    Layer 2 的输入契约。

    Layer 2 从 Layer 1 接收完整的 RawDocument。
    禁止修改此输入的任何部分。
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    raw_document: RawDocument


class ReconstructedStructure(BaseModel):
    """
    Layer 2 的主要输出契约：结构恢复。

    表示基于纯视觉与位置证据 + 显式文本引用
    恢复出的文档逻辑结构。

    它不包含：
    - 内容的语义含义
    - 知识概念
    - 任何形式的分块或 RAG 准备
    - 重要性或教学价值判断

    它仅包含：
    - 文档层级结构
    - 逻辑阅读顺序（以 ContentBlock 表示）
    - 文本与资产之间的交叉文档引用
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    # 从视觉 + 文本线索恢复的文档层级
    chapters: list[ChapterNode] = Field(
        default_factory=list,
        description="恢复出的章节/小节树。若未检测到结构则可能为空。"
    )

    # 按恢复的逻辑阅读顺序排列的内容。
    # 每个 ContentBlock 代表一个最小逻辑单元，不含语义分组。
    content_blocks: list[ContentBlock] = Field(
        default_factory=list,
        description="按逻辑阅读顺序排列的元素。源自 RawDocument 中的元素。"
    )

    # 所有恢复出的交叉引用（例如“见图 3-2”、“如表 2.1 所示”）
    cross_references: list[CrossReference] = Field(
        default_factory=list,
        description="内容与资产或其他结构元素之间的引用。"
    )

    # 可选的结构元数据（纯几何/位置性质）
    structural_notes: str | None = Field(
        default=None,
        description="关于结构恢复质量或歧义的非语义说明。"
    )


class StructuralRecoveryOutput(BaseModel):
    """
    Layer 2 的完整输出。

    包含重建的结构，并通过稳定 ID 和来源信息
    保持与原始 RawDocument 的可追溯性。
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    input: StructuralRecoveryInput
    structure: ReconstructedStructure

    # Layer 2 必须保证：
    # - 所有 ContentBlock id 稳定且唯一
    # - 所有 ChapterNode id 稳定且唯一
    # - 所有 CrossReference id 稳定且唯一
    # - 输入中的任何 RawElement 均未被修改


# =============================================================================
# Layer 2 Interface (Contract)
# =============================================================================

class StructuralRecovery(Protocol):
    """
    任何 Layer 2 实现都必须满足的接口。

    这是高层和流水线将依赖的契约。
    """

    def process(self, input: StructuralRecoveryInput) -> StructuralRecoveryOutput:
        """
        对提供的 RawDocument 执行结构恢复。

        必须严格遵守：
        - 身份持久性规则
        - 变更规则（永不修改输入）
        - 引用稳定性规则
        - 零语义泄漏
        """
        ...