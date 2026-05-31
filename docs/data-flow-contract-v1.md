# DIS v1.1 Data Flow Contract

**版本**：v1.0.0  
**文档类型**：Phase 2 Required Final Contract  
**状态**：待评审确认（进入编码前必须通过）  
**关联文档**：
- [execution-boundary-freeze-v1.md](execution-boundary-freeze-v1.md)
- [mcdm-structured-document-schema-definition-v1.md](mcdm-structured-document-schema-definition-v1.md)

**目的**：
在 Layer Contract 已经冻结的基础上，进一步定义跨层数据流动的核心不变性规则，确保 StructuredDocument 作为最终 Canonical Model 的完整性、可追溯性和稳定性。

本文档定义以下三项强制规则：
1. Identity Persistence Rule
2. Mutation Rule
3. Reference Stability Rule

---

## 1. Identity Persistence Rule

### 核心原则

**关键标识符必须在整个 Pipeline 中保持稳定（Stable Identity）。**

稳定 ID 是实现 Provenance 全链路追溯、Cross Reference 可靠性和 StructuredDocument 作为长期 Canonical Model 的基础。

### 具体规定

| 标识符类型          | 最早分配层级     | 跨层稳定性要求                          | 说明 |
|---------------------|------------------|-----------------------------------------|------|
| `element_id`        | Layer 1         | **必须全局稳定**                        | 原始原子元素 ID 一经分配，全 Pipeline 不可改变 |
| `asset_id`          | Layer 3         | **必须全局稳定**                        | 资产 ID 一经在 Asset Recovery Layer 分配，后续不可改变 |
| `block_id`          | Layer 2         | **必须全局稳定**                        | 逻辑内容块 ID 一经分配，后续不可改变 |
| `reference_id`      | Layer 2         | **必须全局稳定**                        | 交叉引用关系 ID 一经建立，后续不可改变 |
| `chapter_id` / `section_id` | Layer 2     | **必须全局稳定**                        | 结构节点 ID 一经分配，后续不可改变 |
| `document_id`       | Layer 1 / 外部  | **必须全局稳定**                        | 整个文档的唯一身份 |

### 硬性约束

- 禁止在下游 Layer 重新生成或覆盖上游已分配的稳定 ID。
- 禁止使用临时 ID 或仅在本层有效的局部 ID 作为最终输出中的主标识。
- 所有稳定 ID 必须能够支持从 StructuredDocument 反向追溯到原始 PDF 物理位置。

---

## 2. Mutation Rule

### 核心原则

**上游 Layer 的输出对象应保持高度不变性（Immutability）。下游 Layer 应以追加（Enrich）而非修改（Mutate）的方式进行处理。**

### 逐层 Mutation 规则

| 层级 | 输出物                    | 是否允许修改上游字段 | 允许的修改类型                     | 严格禁止的行为 |
|------|---------------------------|----------------------|------------------------------------|----------------|
| Layer 1 | RawDocument              | 不适用（源头）      | 仅创建，不修改                     | - |
| Layer 2 | ReconstructedStructure   | **有限允许**        | 仅允许对自身创建的对象添加字段；**禁止修改** Layer 1 的 `elements[]` 中任何字段 | 禁止修改 Layer 1 元素的 bbox、content、confidence 等原始字段 |
| Layer 3 | AssetRecoveryResult      | **严格限制**        | 仅允许对新创建的 `assets[]` 写入信息；**禁止修改** Layer 2 的 Structure 或 ContentBlocks 字段 | 禁止修改上游的 logical_content_blocks、cross references 等 |
| Layer 4 | StructuredDocument       | **极严格限制**      | 仅允许组装（Assembly）操作；**禁止修改** Layer 2 和 Layer 3 已输出的任何对象字段 | 禁止在组装阶段修改任何上游对象的属性值 |

### 允许的“Enrichment”边界

- 下游 Layer 可以在**新对象**中引用上游 ID，并添加本层产生的附加信息（例如 Provenance 补充、质量标记）。
- **禁止** 在上游对象上直接追加字段（例如给 Layer 1 的 element 增加 `semantic_tag` 或 `enriched_text`）。
- 推荐做法：通过关联 ID 的方式在下游对象中携带额外信息，而非污染上游对象。

### 硬性约束

- 任何对上游输出对象的字段修改行为，均视为违反本合约。
- Layer 4（Document Assembly）**不得**对 ReconstructedStructure 或 AssetRecoveryResult 中的任何字段进行改写。

---

## 3. Reference Stability Rule

### 核心原则

**跨层和跨对象的引用，必须以稳定 ID 作为主引用方式。**

bbox + page 仅作为辅助的 Provenance 信息，不得作为主要引用机制。

### 具体规定

| 引用类型               | 主引用方式         | 是否允许 bbox/page 作为主引用 | bbox/page 角色定位             | 说明 |
|------------------------|--------------------|-------------------------------|--------------------------------|------|
| 内容块 ↔ 资产          | `asset_id`         | 禁止                          | 仅用于 Provenance              | 必须通过 asset_id 建立关系 |
| 文本引用图/表/公式     | `reference_id` + `asset_id` | 禁止                     | 仅用于 Provenance              | 引用关系必须绑定稳定 ID |
| 章节/小节内部引用      | `block_id` / `section_id` | 禁止                     | 仅用于 Provenance              | 必须使用稳定结构 ID |
| 资产内部引用（极少数） | `asset_id`         | 禁止                          | 仅用于 Provenance              | - |
| 最终 StructuredDocument 中的引用 | 稳定 ID 组合     | 仅允许作为 fallback         | 辅助追溯信息                   | 任何引用关系失效时可降级使用 bbox/page，但必须标记为 fallback |

### 允许的 Fallback 使用场景（严格限定）

- 仅当稳定 ID 引用因数据损坏或极端异常无法解析时，允许使用 `page + bbox` 作为降级引用。
- 所有使用 bbox/page 作为引用的地方，必须同时携带以下信息：
  - `is_fallback: true`
  - 原始稳定 ID（如果存在）
  - 降级原因说明

### 硬性约束

- **禁止** 将 bbox + page 设计为常规的引用机制。
- **禁止** 在 StructuredDocument 的 CrossReferences 中存在仅依赖 bbox/page 而不绑定稳定 ID 的引用记录。
- 所有 Cross Reference 必须优先尝试通过稳定 ID 建立关系。

---

## 4. 整体 Data Flow 不变性原则

为支持以上三项规则，补充以下整体约束：

1. **追加优于修改**：整个 Pipeline 应采用“创建新对象 + 通过 ID 关联”的模式，而非“就地修改上游对象”。
2. **ID 分配前置原则**：稳定 ID 应尽可能在最早可确定的层级分配（例如元素在 Layer 1、逻辑块在 Layer 2、资产在 Layer 3）。
3. **引用完整性优先**：在 Layer 4 组装最终 StructuredDocument 时，必须验证所有引用的稳定 ID 是否存在且有效。
4. **降级必须可审计**：任何使用 fallback 引用的情况，都必须在 IntegrityManifest 中被显式记录。

---

## 冻结状态

| 规则名称                    | 状态     | 定义完成度 | 约束强度 |
|-----------------------------|----------|------------|----------|
| Identity Persistence Rule   | 已定义   | 完整       | 硬约束   |
| Mutation Rule               | 已定义   | 完整（逐层）| 硬约束   |
| Reference Stability Rule    | 已定义   | 完整       | 硬约束   |

**本文档与 `execution-boundary-freeze-v1.md` 共同构成进入 Phase 3（Pipeline Stub Implementation）前的最终合约包。**

---

**文档状态**：v1.0.0 草案（待评审）  
**下一步**：请用户评审本合约。如无异议，确认后将与 Layer Contract 一起标记为正式冻结版本。