from pydantic import BaseModel, Field, model_validator


class ChunkingConfig(BaseModel):
    """Parameters of the splitter. Sizes are in characters."""

    chunk_size: int = Field(default=800, ge=1)
    overlap: int = Field(default=100, ge=0)

    @model_validator(mode="after")
    def _overlap_smaller_than_size(self) -> "ChunkingConfig":
        if self.overlap >= self.chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        return self


class Chunk(BaseModel):
    """A piece of one page, ready to be embedded and cited."""

    chunk_id: str
    doc_id: str
    source: str
    page_number: int = Field(ge=1)
    chunk_index: int = Field(ge=0)  # position within the page
    text: str
    char_start: int = Field(ge=0)  # offsets inside the page text
    char_end: int = Field(ge=1)
    metadata: dict[str, str] = Field(default_factory=dict)
