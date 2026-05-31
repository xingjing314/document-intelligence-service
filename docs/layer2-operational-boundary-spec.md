# DIS v1.1 Layer 2 Operational Boundary Specification

**Version**: 1.0  
**Status**: Binding Specification (Contract Phase)  
**Layer**: Structural Recovery (Layer 2)  
**Date**: 2025

---

## 1. Purpose

This document defines the **precise operational boundaries** for Layer 2 of the Document Intelligence Service.

It serves as the authoritative rulebook for:
- What Layer 2 is allowed to do
- What Layer 2 is strictly forbidden from doing
- How to distinguish "structural recovery" from "semantic inference"

This specification takes precedence over any implementation intuition.

---

## 2. Layer 2 Core Mission (Single Sentence)

> Recover the **logical document structure** and **explicit reference relationships** from raw visual elements, using only positional, visual, and explicit textual cues — without inferring meaning or importance.

---

## 3. Definition: Structural vs Semantic

| Category          | Allowed (Structural)                          | Forbidden (Semantic / Knowledge)                     |
|-------------------|-----------------------------------------------|-------------------------------------------------------|
| **Goal**          | Reconstruct "how the document is organized"   | Understand "what the document means"                 |
| **Basis**         | Visual layout + explicit text references      | Interpretation, implication, domain knowledge        |
| **Output**        | Hierarchy, order, references                  | Concepts, summaries, importance, explanations        |
| **Judgment**      | "This text appears before that image"         | "This image explains photosynthesis"                 |

**Rule of Thumb**:
> If the operation requires understanding *why* something exists or *what it means*, it is forbidden in Layer 2.

---

## 4. Allowed Operations (Strictly Defined)

Layer 2 may perform the following operations **only**:

### 4.1 Reading Order Recovery
- Determine the logical sequence in which a human reader is expected to consume visual elements on a page and across pages.
- Basis: Visual flow (columns, reading direction), explicit numbering, positional heuristics derived from layout.
- Output: Ordered `ContentBlock` list in `ReconstructedStructure`.

**Allowed**:
- Inferring that a caption below an image should be read after the image.
- Using explicit textual cues like "as shown below" or "continued on next page".

**Forbidden**:
- Reordering content based on "importance" or "pedagogical value".
- Assuming logical flow based on domain conventions (e.g., "in biology textbooks, diagrams always come after explanations").

### 4.2 Hierarchy Recovery (TOC / Chapter / Section)
- Recover the document's section hierarchy (Chapter → Section → Subsection).
- Basis: Visual cues (font size, position, numbering patterns, table of contents if present) + explicit textual markers.
- Output: `ChapterNode` tree.

**Allowed**:
- Detecting heading levels from font size differences and positioning.
- Parsing explicit table of contents pages.
- Using numbering patterns (1.1, 1.1.1, etc.).

**Forbidden**:
- Inferring that a section is "more important" than another.
- Creating hierarchy based on semantic similarity of content.

### 4.3 Cross-Reference Recovery
- Recover explicit references between content and assets (e.g., "see Figure 3-2", "as shown in Table 1").
- Recover references between different parts of the text.
- Output: `CrossReference` objects with stable ID links.

**Allowed**:
- Parsing explicit phrases that point to figures, tables, formulas, or other sections.
- Linking the reference text to the target asset or section using stable IDs.

**Forbidden**:
- Inferring implicit relationships ("this paragraph is explaining the previous diagram").
- Creating references based on topical similarity.

### 4.4 Stable ID Assignment
- Assign globally unique, stable identifiers to:
  - Logical content units (`ContentBlock.id`)
  - Structural nodes (`ChapterNode.id`)
  - Reference relations (`CrossReference.id`)

These IDs must remain stable across pipeline runs for the same document.

---

## 5. Strictly Prohibited Operations

The following are **permanently forbidden** in Layer 2:

| Category                    | Examples of Forbidden Behavior                                      | Reason |
|----------------------------|---------------------------------------------------------------------|--------|
| **Semantic Inference**     | Determining the "meaning" or "topic" of a paragraph or asset        | Violates structural-only principle |
| **Object Boundary Inference** | Deciding that multiple text spans + an image "form one logical figure explanation" | This is early segmentation for downstream use |
| **Importance / Value Judgment** | Labeling a section as "key concept", "difficult", or "exam material" | Purely pedagogical/semantic |
| **Chunking / Grouping**    | Merging raw elements into "RAG-ready" blocks                        | Directly violates No Chunking rule |
| **Knowledge Extraction**   | Identifying "concepts", "definitions", or "key terms"               | This belongs in Knowledge Engineering layers |
| **Downstream Optimization** | Adding hints for embedding, retrieval, or teaching use cases        | Violates No Forward Engineering rule |
| **Implicit Relationship Inference** | "This text probably explains that table"                         | Requires semantic understanding |
| **Layout Understanding beyond geometry** | Classifying regions as "header", "body", "sidebar" based on teaching conventions | Borderline structural but easily leaks into semantics |

---

## 6. Interaction Rules with Layer 1 (RawDocument)

Layer 2 **must** treat `RawDocument` as an immutable source of raw facts.

- **Must not** modify any `RawElement`, `RawPage`, or their fields.
- **May** reference `RawElement` via stable `element_id` when necessary for provenance.
- **Should** primarily work with the raw elements to derive higher-level structural objects (`ContentBlock`, `ChapterNode`, etc.).
- **Must not** assume any grouping or logical units already exist in the raw data.

---

## 7. Output Purity Requirements

The `ReconstructedStructure` produced by Layer 2 must satisfy:

- Contains **only** structural, hierarchical, and referential information.
- Every object must carry complete `Provenance`.
- All references between objects use stable IDs (not bbox + page as primary).
- No fields that describe "meaning", "importance", or "usage".

If a human reads only the `ReconstructedStructure`, they should be able to understand:
- The document's section organization
- The logical order of content
- Which parts reference which assets

They should **not** be able to understand:
- What the document is about
- Which parts are important
- How the content should be taught or learned

---

## 8. Decision Framework for Borderline Cases

When uncertain whether an operation is allowed, apply the following test:

> **"Can this operation be performed using only visual geometry, explicit text strings, and positional relationships — without requiring understanding of the *content's meaning*?"**

- **Yes** → Generally allowed (if it fits one of the four allowed categories in Section 4).
- **No** → Forbidden.

**Second Test** (for safety):
> "If this operation were removed, would downstream layers still be able to perform their jobs (even if less efficiently)?"

If the answer is "No, downstream would be crippled", the operation is likely doing forbidden pre-work for later layers.

---

## 9. Examples

### Allowed
- Using font size and vertical position to assign heading levels.
- Detecting the phrase "see Figure 4-1 on the next page" and linking it to the corresponding image asset via stable ID.
- Reordering two text elements on the same page because one has an explicit "continued from previous column" marker.

### Forbidden
- Merging a paragraph and the image below it into one "ContentBlock" because "they explain the same concept".
- Deciding that a large diagram should appear earlier in the reading order because "it's central to the chapter".
- Labeling a section as "核心概念" (core concept) based on its content.

---

## 10. Relationship to Other Layers and Contracts

This specification is subordinate to, and must remain consistent with:
- Permanent Boundary Audit (DIS only does Document Recovery)
- Data Flow Contract (Identity Persistence, Mutation Rule, Reference Stability)
- Layer 2 Contract Definitions (`layer2/contracts.py`)
- Overall principle: **Document Recovery System**, not Document Understanding System.

---

## 11. Status and Governance

- This document is binding during Layer 2 design and implementation.
- Any proposed change to this boundary must go through explicit re-freeze review.
- Implementation code must be auditable against this specification.

**Layer 2 exists to answer: "How is this document organized structurally?"**

It does **not** exist to answer: "What does this document mean, and how should it be used?"

---

**End of Specification**