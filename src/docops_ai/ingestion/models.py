from pydantic import BaseModel, Field


class PageContent(BaseModel):
    """Text of one PDF page plus the information needed to cite it later"""

    doc_id: str
    source: str
    page_number: int = Field(ge=1)  # 1-based
    text: str
    metadata: dict[str, str] = Field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return not self.text
