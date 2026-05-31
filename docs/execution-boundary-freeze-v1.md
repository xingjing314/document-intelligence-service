# DIS v1.1 Execution Boundary Freeze 文档

**版本**：v1.1.0  
**文档类型**：Execution Boundary Freeze Record  
**冻结日期**：2025  
**依据**：DIS v1.1 Final Execution Boundary Freeze Instruction

**目的**：
在进入任何代码实现前，完成以下三项强制冻结：
1. Layer Contract Freeze
2. StructuredDocument Canonical Lock
3. Asset Recovery Hard Boundary

本文档一经评审通过，即成为 DIS v1.1 开发阶段的最高优先级执行约束。任何实现工作均不得违反本文档内容。

---

## 一、Layer Contract Freeze

### 整体原则

- 每一层只负责其明确定义的恢复与规范化职责。
- 层与层之间通过强类型内部模型传递数据，禁止跨层直接访问原始 PDF。
- 任何一层均严禁引入知识语义（Concept、Chunk、Importance、Teaching Meaning 等）。

---

### Layer 1: Document Ingestion

**输出物**：RawDocument

#### Input
- PDF 文件（路径或二进制流）
- 处理选项（语言、DPI、是否启用公式检测等基础开关）

#### Output Schema（字段级职责）

| 字段类别           | 必须包含内容                                   | 说明 |
|--------------------|------------------------------------------------|------|
| Document Identity  | document_id, source_file_name, total_pages     | 文档基础身份 |
| Page Collection    | pages[]                                        | 每页基础信息 |
| Page Content       | page_number, page_size, rotation               | 页面物理属性 |
| Raw Elements       | elements[]                                     | 原子元素集合 |
| Element Attributes | type, bbox, content, confidence                | 元素类型、位置、原始内容、置信度 |
| Element Classification | is_text / is_image / is_table / is_formula 等 | 基础分类结果 |
| OCR / Detection Provenance | ocr_engine_version, detection_model 等     | 恢复来源记录 |

**Hard Constraints（禁止事项）**：
- 禁止对元素进行任何语义理解或归纳。
- 禁止生成标题层级或阅读顺序。
- 禁止建立任何元素之间的逻辑引用关系。
- 禁止输出任何形式的摘要或解释性文本。

---

### Layer 2: Structural Recovery

**输出物**：ReconstructedStructure

#### Input
- RawDocument（Layer 1 输出）

#### Output Schema（字段级职责）

| 字段类别              | 必须包含内容                                      | 说明 |
|-----------------------|---------------------------------------------------|------|
| Document Structure    | chapters[] / sections[]                           | 完整章节层级树 |
| Hierarchy Information | level, title, page_start, page_end, parent_id     | 层级与范围 |
| Reading Order         | logical_content_sequence[]                        | 按阅读顺序的内容块序列 |
| Content Block         | block_id, type, page, bbox, text_content          | 逻辑内容块 |
| Cross References      | references[]                                      | 图文、表文、公式引用等关系 |
| Reference Details     | source_position, target_asset_id, reference_type  | 引用源与目标 |
| Structure Provenance  | recovery_method（目录解析 / 标题推断 / 规则）     | 恢复方式记录 |

**Hard Constraints（禁止事项）**：
- 禁止对内容块进行语义分类或主题标注。
- 禁止判断章节或内容块的重要性。
- 禁止生成任何形式的知识点或概念。
- 禁止对内容进行总结或改写。

---

### Layer 3: Asset Recovery

**输出物**：AssetRecoveryResult

#### Input
- RawDocument + ReconstructedStructure

#### Output Schema（字段级职责）

| 字段类别              | 必须包含内容                                           | 说明 |
|-----------------------|--------------------------------------------------------|------|
| Assets                | assets[]                                               | 资产集合 |
| Asset Identity        | asset_id, asset_type（figure/table/formula/diagram）   | 资产唯一标识与类型 |
| Spatial Information   | page, bbox, rotation                                   | 空间位置 |
| Structural Information| table_structure / formula_structure / diagram_elements | 结构恢复结果 |
| Caption & Labeling    | caption, label, position_semantics                     | 标题、编号、位置语义 |
| Reference Links       | referenced_by[] / references_to[]                      | 与正文及其他资产的引用关系 |
| Asset Provenance      | detection_stage, confidence, quality_flags             | 恢复来源与质量 |

**Hard Constraints（禁止事项）**：
- 禁止对资产进行任何语义解释或内容总结。
- 禁止将资产与知识点/概念进行映射。
- 禁止判断资产的教学价值或重要性。
- 禁止生成“该图展示了……”“该表说明了……”类描述。
- 禁止引入任何外部知识体系关联。

---

### Layer 4: Document Assembly

**输出物**：StructuredDocument（最终 MCDM）

#### Input
- ReconstructedStructure + AssetRecoveryResult

#### Output Schema（字段级职责）

| 字段类别             | 必须包含内容                                      | 说明 |
|----------------------|---------------------------------------------------|------|
| DocumentMeta         | document_id, source_info, processing_metadata     | 文档元信息与处理记录 |
| Structure            | chapter_tree                                      | 完整结构层级 |
| ContentBlocks        | logical_content_blocks[]                          | 按阅读顺序的内容块 |
| Assets               | assets[]                                          | 所有恢复的资产 |
| CrossReferences      | cross_reference_network                           | 完整引用关系网络 |
| Provenance           | full_provenance_chain（全局 + 逐对象）            | 全链路溯源 |
| IntegrityManifest    | recovery_completeness, quality_summary, issues    | 恢复完整性声明 |

**Hard Constraints（禁止事项）**：
- 禁止在任何对象中添加语义增强字段。
- 禁止引入 Concept、Chunk、Embedding 相关信息。
- 禁止添加任何“推荐切分”“知识点标签”“教学建议”类字段。
- 禁止修改或弱化 Provenance 的完整性要求。

---

## 二、StructuredDocument Canonical Lock

### 正式声明

**StructuredDocument is NOT a preprocessing format.**

**StructuredDocument is the final canonical truth of document recovery.**

它代表的是：扫描版教材 PDF 经过 DIS 处理后，所能达到的**最大程度忠实恢复 + 结构化规范化**的结果。

### v1 Schema 禁止语义增强字段清单（硬性锁定）

在 StructuredDocument 及其所有子对象中，**v1 版本永久禁止**出现以下任何字段或语义：

- Concept / KnowledgePoint / KnowledgeUnit
- Chunk / Segment / TextChunk
- Importance / Priority / Difficulty / KeyPoint
- TeachingValue / LearningObjective / EducationalMeaning
- Summary / Explanation / Interpretation
- SemanticTag / Topic / Category（知识体系分类）
- Embedding / Vector / Similarity 相关信息
- RetrievalHint / RAGOptimization 相关信息
- AgentInstruction / UsageRecommendation

任何试图在 v1 Schema 中引入上述语义的变更，均视为违反本冻结指令。

---

## 三、Asset Recovery Hard Boundary

### 允许范围（仅限以下三类）

| 类别                  | 具体内容                                           | 示例 |
|-----------------------|----------------------------------------------------|------|
| Structural Recovery   | 资产的结构信息恢复                                 | 表格行列结构、公式符号序列、图表组成元素 |
| Spatial Recovery      | 资产在文档中的物理与逻辑位置                       | page + bbox、与正文的相对位置、编号语义 |
| Provenance            | 资产恢复的全过程溯源与质量信息                     | 检测模型、置信度、质量问题标注、恢复阶段 |

### 明确禁止范围

Asset Recovery Layer **严禁**输出以下任何内容：

- Interpretation（语义解释）
  - 例如：“该图展示了光合作用的暗反应过程”
- Concept Mapping（概念映射）
  - 例如：将资产关联到“光合作用”“细胞膜”等概念
- Teaching Meaning（教学意义）
  - 例如：“本图为重点难点”“适合帮助学生理解……”
- Semantic Summarization（语义总结）
- Knowledge Relationship（知识关系推断）
- Educational Value Judgment（教育价值判断）

**判断标准**：
如果输出内容回答了“这个资产‘意味着什么’或‘有什么用’”，则属于禁止范畴。

---

## 冻结确认记录

| 冻结项                          | 状态     | 定义位置                     | 约束强度 |
|--------------------------------|----------|------------------------------|----------|
| Layer Contract Freeze          | 已定义   | 本文档第一部分               | 硬约束   |
| StructuredDocument Canonical Lock | 已锁定 | 本文档第二部分               | 硬约束   |
| Asset Recovery Hard Boundary   | 已锁定   | 本文档第三部分               | 硬约束   |

**本文档生效条件**：
需经架构评审确认后，标记为 v1.1.0 正式冻结版本。此后任何 Phase 的实现工作均必须遵守本文档中的全部约束。

---

**文档状态**：v1.1.0 草案（待评审）  
**下一步**：等待用户评审确认后锁定为正式执行边界。