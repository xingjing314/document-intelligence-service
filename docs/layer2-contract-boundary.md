# Layer 2: Structural Recovery — Contract Boundary

**阶段**：Layer 2 Contract Implementation  
**状态**：Contract Definition Only

## Layer 2 允许的职责（仅此而已）

- Reading Order Recovery（从视觉位置和文本线索恢复逻辑顺序）
- Hierarchy Recovery（章节/小节树状结构）
- Cross-Reference Recovery（图、表、公式等显式引用关系的恢复）
- 产生稳定的结构 ID（chapter_id, block_id, reference_id）

## 严格禁止事项（永久锁定）

- 任何语义理解或知识抽取
- Concept / Knowledge Point 相关内容
- Chunking 或任何 RAG 预处理
- 对象边界推断（Object Boundary Inference）
- Importance / Difficulty / Teaching Value 判断
- 任何为下游层（Layer 3/4）做的预处理 hint

## 数据流约束（必须遵守）

- 输入：RawDocument（来自 Layer 1）
- 输出：ReconstructedStructure
- 必须遵守：
  - Identity Persistence Rule
  - Mutation Rule（绝对不能修改 RawDocument 中的任何元素）
  - Reference Stability Rule（引用必须以稳定 ID 为主）

## 当前阶段限制

本阶段仅进行契约定义。
任何实际的 Structural Recovery 算法实现均属于后续阶段，且必须先通过本契约的评审。

---

**Layer 2 目前仅定义“结构恢复应该输出什么”，不定义“如何恢复”。**

**更详细的操作边界规范**请参考：
`docs/layer2-operational-boundary-spec.md`（当前最高优先级约束）
