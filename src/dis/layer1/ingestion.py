"""
Layer 1: Document Ingestion — Pure Perception Implementation (FROZEN)

This class has reached Perception Complete State.

Allowed operations (strictly limited to perception + basic geometry):
- Open PDF and iterate pages
- Extract raw text spans with bbox (preserving original order and breaks)
- Extract images with bbox
- Capture page-level geometry (width, height, rotation)
- Assign stable element_id
- Record raw extraction output + confidence + provenance

Strictly forbidden in this layer (and permanently):
- Any structural inference (titles, paragraphs, chapters, reading order)
- Any semantic classification
- Grouping, merging, or clustering elements
- Table / formula / region detection or boundary inference
- OCR post-correction, reconstruction, or semantic enhancement
- Any consideration of downstream layers (Layer 2/3/4)

Status: Layer 1 is now frozen. No further refinement allowed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union
from uuid import uuid4

import fitz  # PyMuPDF

from ..contracts import RawDocument, RawPage, RawElement
from ..pipeline import IngestionStub
from ..schema import DocumentMeta, Provenance


class DocumentIngestion(IngestionStub):
    """
    Layer 1 - Pure Perception Layer (FROZEN).

    This class has reached "Perception Complete State".

    It only decomposes the PDF into raw visual elements + basic page geometry.
    It does not understand document structure or meaning.

    It implements the IngestionStub protocol defined in Step 3.

    IMPORTANT: This layer is now frozen. No further enhancement is allowed.
    """

    def __init__(self, dpi: int = 200):
        """
        dpi: Rendering resolution for image-based extraction.
             Higher DPI gives better geometry accuracy but more data.
        """
        self.dpi = dpi

    def process(self, pdf_source: Union[str, bytes, Path]) -> RawDocument:
        """
        Main entry point for Layer 1 (Final Assembly Point).

        This method performs the final structural assembly of RawDocument
        from raw perception results. No new information is created here —
        only organization of already extracted facts.

        Layer 1 is frozen. This method represents the stable boundary.
        """
        # Perception + Geometry capture (already executed in _extract_raw_pages)
        raw_pages = self._extract_raw_pages(pdf_source)

        # Final RawDocument assembly (Step 4-C) — pure structural composition only
        document_meta = self._build_document_meta(pdf_source)

        raw_document = RawDocument(
            meta=document_meta,
            pages=raw_pages,
        )

        return raw_document

    # ------------------------------------------------------------------
    # Internal Perception Methods (Perception Only)
    # ------------------------------------------------------------------

    def _extract_raw_pages(self, pdf_source: Union[str, bytes, Path]) -> list[RawPage]:
        """Extract raw elements page by page without any structural interpretation."""
        doc = self._open_pdf(pdf_source)
        pages: list[RawPage] = []

        for page_index in range(len(doc)):
            page = doc[page_index]

            # Capture pure page geometry (Step 4-B: Geometry normalization)
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            page_rotation = float(page.rotation)  # 0, 90, 180, 270

            raw_elements = self._extract_elements_from_page(page, page_index + 1)

            pages.append(
                RawPage(
                    page_number=page_index + 1,
                    width=page_width,
                    height=page_height,
                    rotation=page_rotation,
                    elements=raw_elements,
                )
            )

        doc.close()
        return pages

    def _extract_elements_from_page(self, page: fitz.Page, page_number: int) -> list[RawElement]:
        """
        Extract raw visual elements from a single page.

        This method must remain strictly perceptual:
        - It reports what is visually present.
        - It does NOT decide what the element "means".
        """
        elements: list[RawElement] = []

        # 1. Text spans (raw, as returned by the extractor)
        text_dict = page.get_text("dict")
        for block in text_dict.get("blocks", []):
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    bbox = tuple(span["bbox"])
                    element = RawElement(
                        element_id=uuid4(),
                        page=page_number,
                        bbox=bbox,
                        type="text",
                        content=span["text"],
                        confidence=1.0,  # PyMuPDF text extraction is generally high confidence
                        provenance=Provenance(
                            source_page=page_number,
                            bbox=bbox,
                            recovered_by="pymupdf_text_extractor",
                            confidence=1.0,
                            recovery_method="direct_text_extraction",
                            model_version=f"fitz-{fitz.version[0]}",
                        ),
                    )
                    elements.append(element)

        # 2. Images
        for img in page.get_images(full=True):
            xref = img[0]
            bbox_list = page.get_image_rects(xref)
            for rect in bbox_list:
                bbox = (rect.x0, rect.y0, rect.x1, rect.y1)
                element = RawElement(
                    element_id=uuid4(),
                    page=page_number,
                    bbox=bbox,
                    type="image",
                    content=None,  # We do not embed image bytes in perception layer by default
                    confidence=0.95,
                    provenance=Provenance(
                        source_page=page_number,
                        bbox=bbox,
                        recovered_by="pymupdf_image_extractor",
                        confidence=0.95,
                        recovery_method="image_xref_extraction",
                        model_version=f"fitz-{fitz.version[0]}",
                    ),
                )
                elements.append(element)

        # Layer 1 remains strictly minimal by design.
        # No object boundary inference or region detection is performed.

        return elements

    def _build_document_meta(self, pdf_source: Union[str, bytes, Path]) -> DocumentMeta:
        """Build minimal document-level metadata from the PDF itself."""
        doc = self._open_pdf(pdf_source)

        meta = DocumentMeta(
            source_filename=self._get_source_name(pdf_source),
            total_pages=len(doc),
            language="unknown",  # Layer 1 does not perform language detection
        )

        doc.close()
        return meta

    # ------------------------------------------------------------------
    # Helper Methods (Pure Utility)
    # ------------------------------------------------------------------

    def _open_pdf(self, pdf_source: Union[str, bytes, Path]) -> fitz.Document:
        if isinstance(pdf_source, (str, Path)):
            return fitz.open(str(pdf_source))
        elif isinstance(pdf_source, bytes):
            return fitz.open(stream=pdf_source, filetype="pdf")
        else:
            raise TypeError(f"Unsupported pdf_source type: {type(pdf_source)}")

    def _get_source_name(self, pdf_source: Union[str, bytes, Path]) -> str:
        if isinstance(pdf_source, (str, Path)):
            return Path(pdf_source).name
        return "bytes_input.pdf"
