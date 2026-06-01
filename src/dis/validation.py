"""
StructuredDocument 的硬验证门（步骤 5）

这些检查在任何 StructuredDocument 离开系统前必须通过。
"""

from __future__ import annotations

from .schema import StructuredDocument


def run_hard_validation_gates(doc: StructuredDocument) -> None:
    """
    执行执行边界冻结中定义的所有强制验证门。

    抛出：
        ValueError：若检测到任何禁止内容或断裂契约。
    """
    # 门 1：语义泄漏检查（已在模型验证器中部分实现）
    forbidden_keywords = [
        "concept", "knowledge_point", "chunk", "embedding",
        "importance", "difficulty", "teaching_value", "summary",
        "interpretation", "semantic_tag", "retrieval_hint"
    ]

    raw_dict = doc.model_dump()

    def _scan(obj: object, path: str = "") -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if any(kw in k.lower() for kw in forbidden_keywords):
                    raise ValueError(
                        f"在 {path}.{k} 检测到禁止的语义字段。 "
                        "DIS 必须产生零知识工程内容。"
                    )
                _scan(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                _scan(item, f"{path}[{i}]")

    _scan(raw_dict)

    # 门 2：引用稳定性（所有交叉引用必须优先使用稳定 ID）
    for ref in doc.cross_references:
        if ref.is_fallback and not ref.target_asset_id and not ref.target_section_id:
            raise ValueError(
                f"CrossReference {ref.id} 使用纯 bbox 回退而无稳定 ID。 "
                "这违反了引用稳定性规则。"
            )

    # 门 3：来源完整性（基本结构检查）
    if not doc.provenance:
        raise ValueError("缺少文档级来源信息。")

    # 门 4：ID 完整性
    all_asset_ids = {a.id for a in doc.assets}
    all_block_ids = {b.id for b in doc.content_blocks}

    for block in doc.content_blocks:
        for aid in block.asset_ids:
            if aid not in all_asset_ids:
                raise ValueError(f"ContentBlock {block.id} 引用了未知的 asset_id {aid}")

    for ref in doc.cross_references:
        if ref.target_asset_id and ref.target_asset_id not in all_asset_ids:
            raise ValueError(f"CrossReference {ref.id} 中存在断裂的资产引用")
        if ref.source_block_id and ref.source_block_id not in all_block_ids:
            raise ValueError(f"CrossReference {ref.id} 中存在断裂的块引用")

    # 若执行到此处，文档已通过硬门
    doc.validate_output_contract()
