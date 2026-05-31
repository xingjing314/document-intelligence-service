# Document Intelligence Service (DIS)

> 将扫描版教材 PDF 转换为**结构化、可追溯、Agent-ready** 的 JSON 知识表示

**当前阶段**：AI Tool Service 架构设计阶段（已完成）

---

## 核心定位

本服务作为 **LLM Agent 的专业 Tool**，目标是：

- 输入：扫描版 / 图片版教材 PDF
- 输出：高质量结构化知识 JSON（带完整溯源）
- 使用场景：RAG 检索 + Agent Tool Calling

**严格边界**（请勿越界设计）：
- 单服务优先，拒绝过度微服务化
- 不做多 Agent 系统
- 不引入知识图谱数据库（Neo4j 等）
- 不设计 UI
- 不做企业中台

---

## 已交付设计文档

**系统架构设计文档**（v0.1.0）：

[docs/system-architecture.md](docs/system-architecture.md)

**架构最终边界审计**（v1.1 - **永久边界最高约束**）：

[docs/architecture-boundary-audit-v1.1.md](docs/architecture-boundary-audit-v1.1.md)

> **本次审计核心成果**（必须作为最高优先级约束）：
> - StructuredDocument 必须确立为 **Minimum Canonical Document Model (MCDM)**
> - 明确定义了 MCDM 的七类一级对象职责
> - Asset Recovery Layer 的“禁止知识解释”红线
> - **DIS 永久边界（Permanent Boundary）** 完整定义（问题5）
> - 十年内无论诱惑多大都不能进入 DIS 的领域清单

**当前阶段**：**Phase 3 — Implementation**（已通过所有冻结审计）

已完成内容：
- Permanent Boundary Audit ✓
- MCDM Schema Freeze ✓
- Execution & Data Flow Contract Freeze ✓

**已实现（Step 1）**：
- 核心 MCDM Schema（`src/dis/schema.py`）
- Hard Validation Gates（`src/dis/validation.py`）

**已完成（Step 2）**：
- Layer Contract Definitions（`src/dis/contracts.py`）

**已完成（Step 3 - Stub Skeleton）**：
- Pipeline structural skeleton（`src/dis/pipeline.py`）
- Fake stub implementations for wiring（`src/dis/stubs.py`）
- All methods are pure stubs (raise NotImplementedError)
- Only data flow structure + validation hook wiring exists
- Zero business logic / algorithms / intelligence

**Step 4 - Layer 1: Document Ingestion 已冻结（Frozen）**

状态：Perception Complete State 已达到

Layer 1 现已锁定为稳定感知边界。

---

**当前阶段：Layer 2 Contract Implementation**

- 已创建 `src/dis/layer2/` 模块
- 已定义 Layer 2 核心契约（`src/dis/layer2/contracts.py`）
- **已发布权威操作边界规范**：
  - `docs/layer2-operational-boundary-spec.md` ← **当前 Layer 2 最高优先级约束文档**

此规范明确定义了 Layer 2 允许与禁止的所有操作，强调“strict structural-only, no semantic inference”。

Layer 2 目前仍处于契约定义阶段，尚未开始任何实现。

**开发纪律**（严格执行）：
- 仅实现 Document Recovery 逻辑
- 永远禁止引入 Concept / Chunk / Semantic / Knowledge 相关内容
- 必须通过 `run_hard_validation_gates()` 才能输出 StructuredDocument

继续执行顺序：Step 2 → Layer Contracts → Pipeline Implementation。

包含内容：
1. 系统整体架构图（Mermaid）
2. 严格 4 层架构设计
3. 每层输入/输出职责
4. 核心数据结构（`StructuredKnowledge` JSON Schema）
5. 完整数据流
6. 面向 Agent 的 Tool API 设计
7. 关键设计原则（铁律级约束）

---

## 快速开始（未来）

```bash
# 安装
uv sync

# 运行服务
uv run uvicorn src.service:app --reload
```

---

## 下一步建议

在进入实现阶段前，强烈建议先完成以下工作：

1. 冻结 `StructuredKnowledge` v1.0.0 JSON Schema（使用 Pydantic）
2. 定义内部 Layer 1~3 的强类型模型
3. 搭建基础 Pipeline 骨架（只跑通，不追求效果）
4. 建立 Schema 兼容性测试

---

**设计原则**：Schema 稳定性 > 一切 | Provenance 必须全覆盖 | Chunking 必须结构感知 | 单服务先跑通
