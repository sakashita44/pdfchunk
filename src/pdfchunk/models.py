from dataclasses import dataclass


@dataclass
class ChunkFileFormat:
    """チャンクファイルのfrontmatter構造定義。"""

    source: str
    chunk: int
    page_start: int
    page_end: int

    def __post_init__(self) -> None:
        if self.chunk < 1:
            raise ValueError(f"chunk は1以上: {self.chunk}")
        if self.page_start < 1:
            raise ValueError(f"page_start は1以上: {self.page_start}")
        if self.page_end < 1:
            raise ValueError(f"page_end は1以上: {self.page_end}")
        if self.page_start > self.page_end:
            raise ValueError(
                f"page_start <= page_end が必要: {self.page_start} > {self.page_end}"
            )
