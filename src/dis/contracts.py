"""
DIS v1.1 — 步骤 2：层契约定义（已冻结）

本模块仅定义层与层之间的数据契约。
它不包含任何算法、业务逻辑或知识工程概念。

目的：
- 为层间流动的数据提供不可变结构定义。
- 作为各层允许产生和消费内容的唯一事实来源。
- 通过设计强制身份持久性、变更规则和引用稳定性。

重要说明：
- 这些是契约，而非实现。
- 任何层都不得修改上游契约的结构。
- 所有稳定 ID 必须在各层间被尊重。
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
# Layer 1 — 文档摄取契约
# =============================================================================

class RawElement(BaseModel):
    """
    从单页中提取的原子元素。
    这是 Layer 1 产生的最小单元。
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    element_id: UUID
    page: int = Field(..., ge=1)
    bbox: tuple[float, float, float, float]
    type: str  # "text", "image", "table_region", "formula_region", "line" 等
    content: str | bytes | None = None
    confidence: float = Field(..., ge=0.0, le=1.0)

    provenance: Provenance


class RawPage(BaseModel):
    """
    属于单个物理页的所有原始元素。

    仅包含关于该页及其元素的原始几何事实。
    不含逻辑结构或语义分组。
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    page_number: int = Field(..., ge=1)

    # 纯页面几何（非语义空间事实）
    width: float
    height: float
    rotation: float = 0.0   # 旋转角度（度），取值 0, 90, 180, 270

    elements: list[RawElement]


class RawDocument(BaseModel):
    """
    Layer 1 输出契约

    这是文档摄取层的完整输出。
    它仅包含来自 PDF 的原始、未处理的原子事实。
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    meta: DocumentMeta
    pages: list[RawPage]

    # ID 规则：RawElement 中的所有 element_id 必须全局唯一且稳定
    # 变更规则：Layer 2+ 不得修改 RawElement 或 RawPage 中的任何字段
    # 引用规则：本层不存在交叉引用


# =============================================================================
# Layer 2 — 结构恢复契约
# =============================================================================

class ReconstructedStructure(BaseModel):
    """
    Layer 2 输出契约

    包含从文档中恢复的逻辑结构与阅读顺序。
    不包含视觉资产详情（那些属于 Layer 3）。
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    # 从文档中恢复的稳定结构
    chapters: list[ChapterNode]

    # 按逻辑阅读顺序排列的内容（源自 RawDocument）
    content_blocks: list[ContentBlock]

    # 在结构分析过程中发现的交叉引用
    cross_references: list[CrossReference]

    # ID 继承规则（必须遵守）：
    # - ChapterNode.id 在整个文档中必须稳定且唯一
    # - ContentBlock.id 必须稳定且唯一
    # - CrossReference.id 必须稳定且唯一
    #
    # 变更规则：
    # - Layer 2 不得修改来自 Layer 1 的任何 RawElement
    # - Layer 2 只能创建新对象（ChapterNode、ContentBlock、CrossReference）
    #
    # 引用规则：
    # - 所有 CrossReference 必须使用稳定 ID（block_id、section_id）作为主引用
    # - bbox + page 仅允许出现在 Provenance 中，不得作为主引用


# =============================================================================
# Layer 3 — 资产恢复契约
# =============================================================================

class AssetRecoveryResult(BaseModel):
    """
    Layer 3 输出契约

    仅包含所有已恢复的视觉与结构资产及其空间和结构信息。
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    assets: list[Asset]

    # ID 继承规则：
    # - Asset.id 必须全局稳定且唯一
    # - 资产可通过 referenced_by_block_ids 引用 ContentBlock.id
    #
    # 变更规则：
    # - Layer 3 不得修改 Layer 1 或 Layer 2 产生的任何对象
    # - Layer 3 仅创建并填充 Asset 对象
    #
    # 引用规则：
    # - 下游层中的所有资产引用必须使用 Asset.id
    # - 不得仅通过 bbox/page 引用资产


# =============================================================================
# Layer 4 — 文档组装契约
# =============================================================================

class AssemblyInput(BaseModel):
    """
    Layer 4（文档组装）所需的组合输入。

    这不是层的输出，而是 Layer 4 所消费内容的约定契约。
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    structure: ReconstructedStructure
    assets: AssetRecoveryResult
    raw_document: RawDocument  # 仅用于文档级来源和完整性检查


class DocumentAssemblyContract(BaseModel):
    """
    Layer 4 输出契约

    Layer 4 仅负责组装最终的 StructuredDocument。
    它不创建新知识——仅组合之前各层产生的内容。

    最终输出必须是有效的 StructuredDocument（参见 schema.py）。
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    # 整个流水线唯一允许的输出
    structured_document: "StructuredDocument"  # 前向引用

    # 组装必须强制：
    # - 保留之前各层的所有稳定 ID
    # - 不引入新的语义字段
    # - 所有交叉引用使用稳定 ID
    # - 完整的来源覆盖


# =============================================================================
# 跨层一致性规则（所有层必须满足）
# =============================================================================

"""
全局规则（由契约设计强制执行）：

1. 身份持久性规则
   - 若 element_id（来自 RawElement）被下游引用，则保持稳定。
   - block_id、chapter_id、asset_id、reference_id 一旦分配即全局稳定。

2. 变更规则
   - 任何层都不得修改由之前各层产生的对象。
   - 仅允许通过创建引用上游 ID 的新对象来进行丰富。

3. 引用稳定性规则
   - 对象之间的主引用必须使用稳定 ID。
   - bbox + page 仅允许在 Provenance 对象中作为支持证据出现。
   - 任何回退用法必须显式标记（is_fallback=True）。

4. 无知识泄漏
   - 这些契约中不得包含与概念、分块、嵌入、重要性、教学价值
     或任何形式语义解释相关的字段。
"""

# Rebuild forward references
DocumentAssemblyContract.model_rebuild()
