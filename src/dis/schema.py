"""
DIS v1.1 - 冻结 MCDM 模式实现（阶段 3 - 步骤 1）

本模块定义 StructuredDocument 的规范数据模型。

关键约束（绝不违反）：
- 零语义 / 知识字段（无 Concept、Chunk、Importance 等）
- 所有对象必须携带完整的 Provenance
- 所有引用必须使用稳定 ID（不得使用裸 bbox/page 引用）
- 强制 extra='forbid' 以防止非规范字段泄漏
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


# =============================================================================
# Core Primitives
# =============================================================================

class AssetType(str, Enum):
    """v1 中支持的资产类型，页面中的非文本类型枚举，处理视觉资产"""
    FIGURE = "figure" # 例如图表、照片、插图
    TABLE = "table" # 例如表格
    FORMULA = "formula"# 例如数学公式
    DIAGRAM = "diagram" # 例如流程图、架构图


class Provenance(BaseModel):
    """任何可恢复元素的完整可追溯记录。
       • 来自 PDF 的哪一页（source_page）
       • 在页面上的具体位置（bbox）
       • 是被谁恢复的（recovered_by）
       • 恢复的置信度有多高（confidence）
       • 用什么方法恢复的（recovery_method）
       • 可选记录模型版本和备注
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_page: int = Field(..., ge=1, description="原始 PDF 中的 1 基页码")
    bbox: tuple[float, float, float, float] = Field(
        ..., description="PDF 坐标空间中的边界框（x0, y0, x1, y1）"
    )
    recovered_by: str = Field(..., description="产生此元素的阶段或组件")
    confidence: float = Field(..., ge=0.0, le=1.0) # 0.0（完全不确定）到 1.0（完全确定）的置信度分数，识别PDF软件自带的置信度
    recovery_method: str = Field(..., description="例如 'ocr'、'layout_analysis'、'rule_based'、'model_inference'")
    model_version: str | None = None
    notes: str | None = None  # 仅用于质量/降级说明，不含语义


class DocumentMeta(BaseModel):
    """源文档的身份与处理元数据。记录处理文档的批次以及相关信息，不涉及文档具体内容"""
    model_config = ConfigDict(extra="forbid", frozen=True)

    document_id: UUID = Field(default_factory=uuid4)
    source_filename: str
    total_pages: int = Field(..., ge=1)
    language: str = Field(default="zh-CN")
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    dis_version: str = Field(default="1.1.0")
    processing_config_hash: str | None = None  # 用于可重现性


# =============================================================================
# Structure
# =============================================================================

class ChapterNode(BaseModel):
    """递归的章节/小节树。规范结构的一部分。  
        它的特点是递归结构（树形结构），可以表示多层级的章节关系，例如：
        • 第1章
        • 1.1 小节
            • 1.1.1 子小节
        • 1.2 小节
        • 第2章
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID = Field(default_factory=uuid4)
    title: str
    level: int = Field(..., ge=1)
    page_start: int = Field(..., ge=1)
    page_end: int = Field(..., ge=1)
    children: list[ChapterNode] = Field(default_factory=list)

    provenance: Provenance


# =============================================================================
# Content
# =============================================================================

class ContentBlock(BaseModel):
    """按阅读顺序排列的逻辑内容块（不含语义解释），处理语义资产"""
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID = Field(default_factory=uuid4)
    type: Literal["paragraph", "heading", "list_item", "caption", "formula_line", "other"]
    text: str | None = None
    page: int = Field(..., ge=1)
    bbox: tuple[float, float, float, float]

    # 对资产的引用（必须使用稳定 ID）
    asset_ids: list[UUID] = Field(default_factory=list)

    provenance: Provenance


# =============================================================================
# Assets
# =============================================================================

class Asset(BaseModel):
    """已恢复视觉/结构资产的规范表示。"""
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID = Field(default_factory=uuid4)
    type: AssetType
    page: int = Field(..., ge=1)
    bbox: tuple[float, float, float, float]

    # 基本恢复信息（仅结构 + 空间）
    caption: str | None = None #资产的标题/说明文字（例如图片下面的描述）
    label: str | None = None          # 例如 "图 3-2"、"表 2.1"
    position_semantics: str | None = None  # 例如 资产在页面上的位置语义描述（例如“在文字左侧”、“位于公式下方”），相对位置的描述

    # 类型特定的结构恢复（无解释，可选，不是必须）
    table_structure: dict | None = None   # 适用时为原始行列数据
    formula_structure: str | None = None  # 适用时为 LaTeX 或符号序列
    diagram_elements: list[dict] | None = None

    # 引用回提及此资产的内容，当前阶段通常不使用，但为未来的反向引用做好准备
    referenced_by_block_ids: list[UUID] = Field(
        default_factory=list
          # 非必须字段，在当前单纯识别阶段通常为空
        )

    provenance: Provenance


# =============================================================================
# Cross References
# =============================================================================

class CrossReference(BaseModel):
    """从文档中恢复的显式交叉引用。
        CrossReference 是用来记录文档里显式的引用关系的。

        比如文档中经常会出现下面这些句子：
        • “见图 3-2”
        • “如表 2.1 所示”
        • “详见公式（4-1）”
        • “请参考第 3 章”

        这个类就是专门用来把这些“谁引用了谁”的关系存下来的。

        ───

        核心设计思想（很重要）

        这个类有一个很严格的规则：

        │ 必须优先用稳定 ID 来建立引用关系，而不能只靠页码和位置。

        也就是说：
        • 好的做法：用 source_block_id + target_asset_id 来记录（因为 ID 是稳定的）
        • 不推荐的做法：只记录“在第 5 页的某个位置”就完事了
        这就是为什么它会有两套引用字段。

    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID = Field(default_factory=uuid4)
    reference_type: str  # "see_figure"、"as_shown_in_table"、"equation" 等

    # 必须使用稳定 ID 作为主引用
    source_block_id: UUID | None = None #是谁在引用（通常是某个内容块）引用发起方
    target_asset_id: UUID | None = None #引用了哪个资产（图、表、公式等）被引用对象
    target_section_id: UUID | None = None #被引用对象 也可以是章节/小节（ChapterNode），因此也提供了 target_section_id 字段， 比如“详见第4章”  

    # 仅回退来源（绝非主引用） 解析出现错误 保底用
    source_page: int
    source_bbox: tuple[float, float, float, float]

    is_fallback: bool = False
    fallback_reason: str | None = None

    provenance: Provenance


# =============================================================================
# Integrity & Final Document
# =============================================================================

class IntegrityManifest(BaseModel):
    """关于恢复质量和完整性的客观声明。
       对最终恢复出来的文档质量做一个客观的“体检报告”。
    
    
    
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    structure_completeness: float = Field(..., ge=0.0, le=1.0) # 结构完整性分数，0.0（完全不完整）到 1.0（完全完整）
    asset_coverage: float = Field(..., ge=0.0, le=1.0) # 资产图表覆盖率分数，0.0（完全未覆盖）到 1.0（完全覆盖）
    cross_reference_coverage: float = Field(..., ge=0.0, le=1.0) # 交叉引用覆盖率分数，0.0（完全未覆盖）到 1.0（完全覆盖）

    missing_pages: list[int] = Field(default_factory=list) # 例如： 丢失的页码列表  [5, 12]，表示第5页和第12页完全未恢复
    degraded_elements: list[str] = Field(default_factory=list)  #  质量较差的元素记录 例如 "page_47_ocr_low_quality"

    overall_confidence: float = Field(..., ge=0.0, le=1.0) # 整体质量置信度分数，0.0（完全不可信）到 1.0（完全可信）
    notes: str | None = None #  补充说明 质量说明备注，例如“第5页图表完全丢失，第12页文本 OCR 质量较差”


class StructuredDocument(BaseModel):
    """
    DIS 的唯一规范输出。
    是整个 Document Intelligence Service（DIS）的最终输出结果
    这是被恢复文档的最终、自描述真相。
    它绝不能包含任何知识工程产物。
    """
    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True) #extra="forbid"：不允许多余字段，validate_assignment=True：在赋值时进行验证， frozen=True：创建后不可修改

    schema_version: Literal["1.1.0"] = "1.1.0" #模式版本，必须固定为 "1.1.0"，以便未来版本升级时进行兼容性检查
    meta: DocumentMeta #文档的基本身份信息（来源文件名、总页数、处理时间等），必填

    structure: list[ChapterNode] = Field(default_factory=list) # 文档的章节层级树结构  
    content_blocks: list[ContentBlock] = Field(default_factory=list)#按逻辑阅读顺序排列的所有内容块（文字为主，不含语义解释）
    assets: list[Asset] = Field(default_factory=list) # 所有被恢复出来的图、表、公式、示意图等 
    cross_references: list[CrossReference] = Field(default_factory=list) #文档中所有显式的交叉引用关系  

    provenance: Provenance  # 文档级来源
    integrity: IntegrityManifest  # 恢复质量声明

    # ==================================================================
    # 硬验证门（步骤 5） 
    # • 这是一个自动触发的验证器。
    # • 作用：严格禁止在以上四个列表中出现任何带有语义、知识工程性质的字段（比如 importance、concept、embedding 等）。
    # • 这是防止“知识泄漏”的第一道防线。• 这是一个需要手动调用的方法。
    # • 作用：在最终输出 StructuredDocument 之前，进行一系列硬性检查，包括：
    # • 检查所有引用是否断裂
    # • 检查 provenance 是否存在
    # • 调用更底层的验证逻辑
    # • 通常由 validation.py 中的 run_hard_validation_gates 函数调用。

    # ==================================================================
    @field_validator("content_blocks", "assets", "cross_references", "structure", mode="before")
    @classmethod
    def _forbid_semantic_fields(cls, v: list) -> list:
        """防止意外注入知识工程字段。"""
        forbidden_keywords = {
            "concept", "knowledge", "chunk", "embedding", "importance",
            "difficulty", "teaching", "summary", "interpretation", "semantic"
        }

        if not isinstance(v, list):
            return v

        for item in v:
            if isinstance(item, dict):
                for key in item.keys():
                    if any(kw in key.lower() for kw in forbidden_keywords):
                        raise ValueError(
                            f"检测到禁止的语义字段：'{key}'。 "
                            "StructuredDocument 必须包含零知识工程内容。"
                        )
        return v

    def validate_output_contract(self) -> None:
        """
        步骤 5 - 硬验证门。
        必须在返回任何 StructuredDocument 之前调用。
        """
        # 1. 无语义泄漏
        # （已由上面的验证器 + extra='forbid' 部分强制）

        # 2. 所有引用必须基于稳定 ID（基本检查）
        asset_ids = {a.id for a in self.assets}
        block_ids = {b.id for b in self.content_blocks}
        chapter_ids = {c.id for c in self._flatten_chapters(self.structure)}

        for ref in self.cross_references:
            if ref.target_asset_id and ref.target_asset_id not in asset_ids:
                raise ValueError(f"断裂引用：未找到 target_asset_id {ref.target_asset_id}")
            if ref.source_block_id and ref.source_block_id not in block_ids:
                raise ValueError(f"断裂引用：未找到 source_block_id {ref.source_block_id}")

        # 3. 来源覆盖（基本）
        if not self.provenance:
            raise ValueError("缺少文档级来源信息")

        # 更全面的检查可在后续步骤中添加

    @staticmethod
    def _flatten_chapters(nodes: list[ChapterNode]) -> list[ChapterNode]:
        result = []
        for node in nodes:
            result.append(node)
            result.extend(StructuredDocument._flatten_chapters(node.children))
        return result
