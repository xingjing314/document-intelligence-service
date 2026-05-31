# Layer 1: Document Ingestion — Perception Freeze Declaration

**版本**：v1.1  
**状态**：**Frozen**（Perception Complete State）

## 冻结声明

Layer 1（Document Ingestion）已正式达到以下状态：

- Raw Perception Extraction：完成
- Geometry normalization（基础必要部分）：完成
- 无任何 object inference、grouping、segmentation 或 semantic 内容

## 边界锁定

从本文档发布之日起，Layer 1 进入永久冻结状态：

- 禁止继续增强 geometry normalization
- 禁止引入 table / formula / region detection
- 禁止任何 object boundary inference
- 禁止为下游层做任何预处理或优化

## 核心原则（已锁定）

> Layer 1 can describe space, but cannot decide objects.

## 职责范围（最终版）

Layer 1 只负责：

1. Page Rendering Decomposition
2. Raw Element Extraction（text spans, images）
3. Basic Page Geometry Capture（width, height, rotation）
4. Raw Output + Provenance Preservation

## 验收标准

Layer 1 输出（RawDocument）必须满足：

- 可还原 PDF 页面的视觉元素分布
- 不丢失原始视觉信息
- 不包含任何结构推断
- 不包含任何语义信息

---

**Layer 1 现已冻结。后续任何对 Layer 1 的修改均需重新启动架构变更流程。**

**日期**：2025
**签署**：DIS Architecture Implementation Lead
