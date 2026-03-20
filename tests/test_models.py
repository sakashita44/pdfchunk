import pytest

from pdfchunk.models import ChunkFileFormat


class TestChunkFileFormat:
    """ChunkFileFormat のバリデーションテスト。"""

    def test_valid(self) -> None:
        chunk = ChunkFileFormat(source="a.pdf", chunk=1, page_start=1, page_end=10)
        assert chunk.source == "a.pdf"
        assert chunk.chunk == 1
        assert chunk.page_start == 1
        assert chunk.page_end == 10

    def test_single_page(self) -> None:
        chunk = ChunkFileFormat(source="a.pdf", chunk=1, page_start=5, page_end=5)
        assert chunk.page_start == chunk.page_end

    def test_chunk_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="chunk は1以上"):
            ChunkFileFormat(source="a.pdf", chunk=0, page_start=1, page_end=10)

    def test_page_start_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="page_start は1以上"):
            ChunkFileFormat(source="a.pdf", chunk=1, page_start=0, page_end=10)

    def test_page_end_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="page_end は1以上"):
            ChunkFileFormat(source="a.pdf", chunk=1, page_start=1, page_end=0)

    def test_negative_chunk_raises(self) -> None:
        with pytest.raises(ValueError, match="chunk は1以上"):
            ChunkFileFormat(source="a.pdf", chunk=-1, page_start=1, page_end=10)

    def test_negative_page_start_raises(self) -> None:
        with pytest.raises(ValueError, match="page_start は1以上"):
            ChunkFileFormat(source="a.pdf", chunk=1, page_start=-5, page_end=10)

    def test_negative_page_end_raises(self) -> None:
        with pytest.raises(ValueError, match="page_end は1以上"):
            ChunkFileFormat(source="a.pdf", chunk=1, page_start=1, page_end=-3)

    def test_start_greater_than_end_raises(self) -> None:
        with pytest.raises(ValueError, match="page_start <= page_end"):
            ChunkFileFormat(source="a.pdf", chunk=1, page_start=10, page_end=5)
