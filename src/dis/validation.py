"""
Hard Validation Gates for StructuredDocument (Step 5)

These checks MUST pass before any StructuredDocument can leave the system.
"""

from __future__ import annotations

from .schema import StructuredDocument


def run_hard_validation_gates(doc: StructuredDocument) -> None:
    """
    Executes all mandatory validation gates defined in the Execution Boundary Freeze.

    Raises:
        ValueError: If any forbidden content or broken contract is detected.
    """
    # Gate 1: Semantic leakage check (already partially in model validator)
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
                        f"Forbidden semantic field detected at {path}.{k}. "
                        "DIS must produce zero knowledge engineering content."
                    )
                _scan(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                _scan(item, f"{path}[{i}]")

    _scan(raw_dict)

    # Gate 2: Reference stability (all cross references must prefer stable IDs)
    for ref in doc.cross_references:
        if ref.is_fallback and not ref.target_asset_id and not ref.target_section_id:
            raise ValueError(
                f"CrossReference {ref.id} is using pure bbox fallback without stable ID. "
                "This violates Reference Stability Rule."
            )

    # Gate 3: Provenance completeness (basic structural check)
    if not doc.provenance:
        raise ValueError("Document-level provenance is missing.")

    # Gate 4: ID integrity
    all_asset_ids = {a.id for a in doc.assets}
    all_block_ids = {b.id for b in doc.content_blocks}

    for block in doc.content_blocks:
        for aid in block.asset_ids:
            if aid not in all_asset_ids:
                raise ValueError(f"ContentBlock {block.id} references unknown asset_id {aid}")

    for ref in doc.cross_references:
        if ref.target_asset_id and ref.target_asset_id not in all_asset_ids:
            raise ValueError(f"Broken asset reference in CrossReference {ref.id}")
        if ref.source_block_id and ref.source_block_id not in all_block_ids:
            raise ValueError(f"Broken block reference in CrossReference {ref.id}")

    # If we reach here, the document passes the hard gates
    doc.validate_output_contract()
