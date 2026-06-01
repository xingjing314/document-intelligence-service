# schema.py 模型类详解

> 本文档记录了对 `src/dis/schema.py` 中核心 Pydantic 模型的详细解释与设计分析。

## 概述

`schema.py` 定义了 Document Intelligence Service（DIS）的核心数据模型。`StructuredDocument` 是整个系统的最终规范输出，所有其他模型均服务于此。

本文档按类逐个进行说明，重点关注字段含义、约束条件以及设计意图。

---

1. AssetType

```python
class AssetType(str, Enum):
    FIGURE = "figure"
    TABLE = "table"
    FORMULA = "formula"
    DIAGRAM = "diagram"
说明：
• 这是一个字符串枚举，用于定义可恢复的资产类型。
• 为什么没有 TEXT 类型？
  • 文字内容由 ContentBlock 负责承载。
  • Asset 仅用于表示独立于文字流的视觉/结构对象（图、表、公式、示意图等）。
  • 这是内容与资产分离的设计体现。
2. Provenance 
class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_page: int = Field(..., ge=1)
    bbox: tuple[float, float, float, float] = Field(...)
    recovered_by: str = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0)
    recovery_method: str = Field(...)
    model_version: str | None = None
    notes: str | None = None 
    核心作用：记录任意可恢复元素的来源与恢复过程信息。

关键字段说明：
• source_page + bbox：元素在原始 PDF 中的位置信息。
• recovered_by：由哪个组件/阶段产生。
• confidence：置信度（0~1）。
• recovery_method：恢复方法（如 direct_text_extraction）。
• notes：仅用于质量说明，不包含语义信息。
3. DocumentMeta
class DocumentMeta(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    document_id: UUID = Field(default_factory=uuid4)
    source_filename: str
    total_pages: int = Field(..., ge=1)
    language: str = Field(default="zh-CN")
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    dis_version: str = Field(default="1.1.0")
    processing_config_hash: str | None = None
 核心作用：记录源文档的身份与处理元数据。

特别说明 - processing_config_hash：
• 用于记录处理时所使用的配置哈希值。
• 主要目的是支持可复现性（Reproducibility）。
• 当需要验证两次处理是否使用完全相同的配置时，可通过此字段进行比对。
• 当前为可选字段（可为 None）
4. ChapterNode
class ChapterNode(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID = Field(default_factory=uuid4)
    title: str
    level: int = Field(..., ge=1)
    page_start: int = Field(..., ge=1)
    page_end: int = Field(..., ge=1)
    children: list[ChapterNode] = Field(default_factory=list)
    provenance: Provenance

核心特点：
• 递归结构，用于表示文档的章节层级树。
• children 字段实现多级嵌套。
• level 表示层级深度（1 为章，2 为节等）
5. Asset

class Asset(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID = Field(default_factory=uuid4)
    type: AssetType
    page: int = Field(..., ge=1)
    bbox: tuple[float, float, float, float]

    caption: str | None = None
    label: str | None = None
    position_semantics: str | None = None

    table_structure: dict | None = None
    formula_structure: str | None = None
    diagram_elements: list[dict] | None = None

    referenced_by_block_ids: list[UUID] = Field(default_factory=list)
    provenance: Provenance

重要字段说明：

• position_semantics：描述资产与周围内容的相对位置关系（如 "left of text"、"below formula"）。
  设计目的是在精确坐标（bbox）之外，提供可读的相对空间信息，辅助后续结构恢复与引用建立。

• referenced_by_block_ids：反向引用，记录哪些 ContentBlock 引用了该资产。
  与 ContentBlock 中的 asset_ids 形成双向关联。
  当前阶段（仅 Layer 1）通常不使用，属于非必须字段。

───

6. CrossReference

class CrossReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID = Field(default_factory=uuid4)
    reference_type: str

    source_block_id: UUID | None = None
    target_asset_id: UUID | None = None
    target_section_id: UUID | None = None

    source_page: int
    source_bbox: tuple[float, float, float, float]

    is_fallback: bool = False
    fallback_reason: str | None = None

    provenance: Provenance

核心设计原则：
• 必须优先使用稳定 ID 作为主引用（source_block_id、target_asset_id、target_section_id）。
• source_page + source_bbox 仅作为回退（Fallback）使用，绝非主引用。

回退场景：
• 结构恢复阶段未能识别出稳定的 ContentBlock。
• 文档质量较差（OCR 错误、排版混乱）。
• 当前仅实现 Layer 1 的阶段。
• 使用时必须将 is_fallback 设为 True，并填写 fallback_reason。

───

7. IntegrityManifest

class IntegrityManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    structure_completeness: float = Field(..., ge=0.0, le=1.0)
    asset_coverage: float = Field(..., ge=0.0, le=1.0)
    cross_reference_coverage: float = Field(..., ge=0.0, le=1.0)

    missing_pages: list[int] = Field(default_factory=list)
    degraded_elements: list[str] = Field(default_factory=list)

    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    notes: str | None = None

核心作用：
• 对最终恢复结果的质量进行客观量化声明。
• 包含三大覆盖率指标和具体问题清单。
• 是 StructuredDocument 的必填组成部分。

───

8. StructuredDocument

class StructuredDocument(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    schema_version: Literal["1.1.0"] = "1.1.0"
    meta: DocumentMeta

    structure: list[ChapterNode] = Field(default_factory=list)
    content_blocks: list[ContentBlock] = Field(default_factory=list)
    assets: list[Asset] = Field(default_factory=list)
    cross_references: list[CrossReference] = Field(default_factory=list)

    provenance: Provenance
    integrity: IntegrityManifest

定位：
• 整个 DIS 系统的唯一规范最终输出。
• 必须自包含、零语义泄漏、具备完整可追溯性。

───

9. 关键方法：_forbid_semantic_fields

@field_validator("content_blocks", "assets", "cross_references", "structure", mode="before")
@classmethod
def _forbid_semantic_fields(cls, v: list) -> list:

作用：
• 在数据进入模型前，自动检查并禁止任何包含语义/知识工程特征的字段。
• 监控四个核心列表，防止出现 importance、concept、embedding、chunk 等字段。

设计目的：
• 强制执行“零知识工程内容”原则。
• 属于模型层面的硬性防护机制。

───

附注

• 所有模型均使用 extra="forbid" 和 frozen=True 配置，确保数据严格且不可变。
• 系统强调稳定 ID 优先和来源可追溯原则。
• referenced_by_block_ids 等字段在当前仅实现 Layer 1 的阶段暂不使用。

───

本文档由对话内容整理生成，供后续查阅与参考。   
