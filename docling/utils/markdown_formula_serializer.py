import base64
from io import BytesIO
from typing import Any, Optional

from docling_core.transforms.serializer.base import BaseDocSerializer
from docling_core.transforms.serializer.common import create_ser_result
from docling_core.transforms.serializer.markdown import (
    MarkdownTextSerializer,
    SerializationResult,
)
from docling_core.types.doc import DoclingDocument, TextItem
from docling_core.types.doc.labels import DocItemLabel


class FormulaImageTextSerializer(MarkdownTextSerializer):
    """Text serializer that renders FormulaItems as embedded base64 PNG images.

    When a formula's page image is available (requires generate_page_images=True
    on the pipeline), emits ![Formula](data:image/png;base64,...) instead of
    LaTeX math or the formula-not-decoded placeholder. Falls back to the
    standard serializer behaviour if no page image can be obtained.
    """

    @staticmethod
    def _encode_image(img: Any) -> str:
        buf = BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def serialize(
        self,
        *,
        item: TextItem,
        doc_serializer: BaseDocSerializer,
        doc: DoclingDocument,
        is_inline_scope: bool = False,
        visited: Optional[set[str]] = None,
        **kwargs: Any,
    ) -> SerializationResult:
        if isinstance(item, TextItem) and item.label == DocItemLabel.FORMULA:
            img = item.get_image(doc)
            if img is not None:
                b64 = self._encode_image(img)
                return create_ser_result(
                    text=f"![Formula](data:image/png;base64,{b64})",
                    span_source=item,
                )
        return super().serialize(
            item=item,
            doc_serializer=doc_serializer,
            doc=doc,
            is_inline_scope=is_inline_scope,
            visited=visited,
            **kwargs,
        )
