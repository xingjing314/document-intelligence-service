"""
Layer 1: 文档摄取 — 纯感知实现（已冻结）

本类已达到感知完成状态。

允许的操作（严格限制在感知 + 基础几何范围内）：
- 打开 PDF 并遍历页面
- 提取带 bbox 的原始文本片段（保留原始顺序与断行）
- 提取带 bbox 的图像
- 捕获页面级几何信息（宽度、高度、旋转）
- 分配稳定 element_id
- 记录原始提取输出 + 置信度 + 来源

本层（且永久）严格禁止：
- 任何结构推断（标题、段落、章节、阅读顺序）
- 任何语义分类
- 对元素进行分组、合并或聚类
- 表格 / 公式 / 区域检测或边界推断
- OCR 后校正、重建或语义增强
- 任何对下游层（Layer 2/3/4）的考虑

状态：Layer 1 现已冻结。不允许进一步修改。
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
    Layer 1 - 纯感知层（已冻结）。

    本类已达到“感知完成状态”。

    它仅将 PDF 分解为原始视觉元素 + 基础页面几何。
    不理解文档结构或含义。

    它实现了步骤 3 中定义的 IngestionStub 协议。

    重要：本层现已冻结。不允许进一步增强。
    """

    def __init__(self, dpi: int = 200):
        """
        dpi：基于图像提取的渲染分辨率。
             更高的 DPI 提供更好的几何精度，但数据量更大。
        """
        self.dpi = dpi

    def process(self, pdf_source: Union[str, bytes, Path]) -> RawDocument:
        """
        Layer 1 的主入口（最终组装点）。

        本方法从原始感知结果执行 RawDocument 的最终结构组装。
        此处不创建新信息——仅组织已提取的事实。

        Layer 1 已冻结。本方法代表稳定边界。
        """
        # 感知 + 几何捕获（已在 _extract_raw_pages 中执行）
        raw_pages = self._extract_raw_pages(pdf_source)

        # 最终 RawDocument 组装（步骤 4-C）— 仅纯结构组合
        document_meta = self._build_document_meta(pdf_source)

        raw_document = RawDocument(
            meta=document_meta,
            pages=raw_pages,
        )

        return raw_document

    # ------------------------------------------------------------------
    # 内部感知方法（仅感知）
    # ------------------------------------------------------------------

    def _extract_raw_pages(self, pdf_source: Union[str, bytes, Path]) -> list[RawPage]:
        """逐页提取原始元素，不进行任何结构解释。"""
        doc = self._open_pdf(pdf_source)
        pages: list[RawPage] = []

        for page_index in range(len(doc)):
            page = doc[page_index]

            # 捕获纯页面几何（步骤 4-B：几何归一化）
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
        从单页提取原始视觉元素。

        本方法必须保持严格感知性质：
        - 报告视觉上存在的内容。
        - 不判断元素“意味着”什么。
        """
        elements: list[RawElement] = []

        # 1. 文本片段（原始，由提取器返回）
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
                        confidence=1.0,  # PyMuPDF 文本提取通常具有较高置信度
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

        # 2. 图像
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
                    content=None,  # 默认不在感知层嵌入图像字节
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

        # Layer 1 按设计保持严格最小化。
        # 不执行对象边界推断或区域检测。

        return elements

    def _build_document_meta(self, pdf_source: Union[str, bytes, Path]) -> DocumentMeta:
        """从 PDF 本身构建最小文档级元数据。"""
        doc = self._open_pdf(pdf_source)

        meta = DocumentMeta(
            source_filename=self._get_source_name(pdf_source),
            total_pages=len(doc),
            language="unknown",  # Layer 1 不执行语言检测
        )

        doc.close()
        return meta

    # ------------------------------------------------------------------
    # 辅助方法（纯工具）
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
