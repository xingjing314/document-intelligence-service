"""
DIS v1.1 Layer 1: Document Ingestion (Pure Perception Layer) — FROZEN

Status: Perception Complete State

This module is responsible ONLY for:
- PDF page rendering
- Raw visual element extraction (text spans, images)
- Basic page geometry capture (width, height, rotation)
- Preservation of raw extraction output

Strict boundaries (permanently locked):
- No structure understanding
- No semantic classification
- No object boundary inference / grouping / segmentation
- No table or formula region detection
- Raw output preservation
- No awareness of downstream layers

Layer 1 is now frozen. No further refinement is allowed.
"""