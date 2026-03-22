from pathlib import Path

import pytest

from pdfchunk.exceptions import PdfChunkError
from pdfchunk.index_generators import DefaultIndexGenerator
from pdfchunk.summarizer import Summarizer


class DummySummarizer(Summarizer):
    """テスト用のダミー要約器。"""

    def summarize(self, text: str) -> str:
        return "ダミー要約"


class TestIndexGenerator:
    """IndexGenerator実装のテスト。"""

    def test_generate_without_summary(self, tmp_chunk_files: list[Path]) -> None:
        """要約なしでindex.md内容が生成されること。"""
        generator = DefaultIndexGenerator()
        result = generator.generate(
            chunk_files=tmp_chunk_files,
            excerpt_lines=5,
            summarize_chunks=False,
        )
        assert isinstance(result, str)
        assert "0001.md" in result

    def test_generate_contains_metadata(self, tmp_chunk_files: list[Path]) -> None:
        """生成されたindexにチャンクのメタ情報が含まれること。"""
        generator = DefaultIndexGenerator()
        result = generator.generate(
            chunk_files=tmp_chunk_files,
            excerpt_lines=5,
            summarize_chunks=False,
        )
        assert "test.pdf" in result
        assert "pages: 1-10" in result

    def test_generate_with_excerpt(self, tmp_chunk_files: list[Path]) -> None:
        """抜粋行が含まれること。"""
        generator = DefaultIndexGenerator()
        result = generator.generate(
            chunk_files=tmp_chunk_files,
            excerpt_lines=3,
            summarize_chunks=False,
        )
        assert "チャンク" in result
        assert "excerpt:" in result

    def test_generate_respects_excerpt_lines_zero(
        self, tmp_chunk_files: list[Path]
    ) -> None:
        """excerpt_lines=0で抜粋が含まれないこと。"""
        generator = DefaultIndexGenerator()
        result = generator.generate(
            chunk_files=tmp_chunk_files,
            excerpt_lines=0,
            summarize_chunks=False,
        )
        assert isinstance(result, str)
        assert "excerpt:" not in result

    def test_generate_sorts_by_filename(self, tmp_chunk_files: list[Path]) -> None:
        """ファイルを逆順で渡してもファイル名昇順でソートされること。"""
        generator = DefaultIndexGenerator()
        reversed_files = list(reversed(tmp_chunk_files))
        result = generator.generate(
            chunk_files=reversed_files,
            excerpt_lines=5,
            summarize_chunks=False,
        )
        # チャンク1がチャンク3より前に出現する
        idx1 = result.index("0001.md")
        idx3 = result.index("0003.md")
        assert idx1 < idx3

    def test_generate_empty_list(self) -> None:
        """空のチャンクファイルリストでも正常に動作すること。"""
        generator = DefaultIndexGenerator()
        result = generator.generate(
            chunk_files=[],
            excerpt_lines=5,
            summarize_chunks=False,
        )
        assert isinstance(result, str)

    def test_generate_summarize_without_summarizer_raises(
        self, tmp_chunk_files: list[Path]
    ) -> None:
        """Summarizer未注入でsummarize_chunks=Trueの場合に例外が発生すること。"""
        generator = DefaultIndexGenerator()  # Summarizer未注入
        with pytest.raises(PdfChunkError):
            generator.generate(
                chunk_files=tmp_chunk_files,
                excerpt_lines=5,
                summarize_chunks=True,
            )

    def test_generate_with_summarizer(self, tmp_chunk_files: list[Path]) -> None:
        """Summarizer注入時にsummarize_chunks=Trueで要約が含まれること。"""
        generator = DefaultIndexGenerator(summarizer=DummySummarizer())
        result = generator.generate(
            chunk_files=tmp_chunk_files,
            excerpt_lines=5,
            summarize_chunks=True,
        )
        assert "ダミー要約" in result
        assert "summary:" in result
