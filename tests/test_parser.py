from pathlib import Path

import pytest

from pdfchunk.exceptions import PdfChunkError
from pdfchunk.parsers import Pymupdf4llmParser


class TestPymupdf4llmParser:
    """Pymupdf4llmParser のテスト。"""

    def test_get_total_pages(self, sample_pdf_path: Path) -> None:
        """総ページ数が正の整数で返ること。"""
        parser = Pymupdf4llmParser()
        total = parser.get_total_pages(sample_pdf_path)
        assert isinstance(total, int)
        assert total > 0

    def test_parse_returns_markdown(self, sample_pdf_path: Path) -> None:
        """指定範囲のパース結果が空でないMarkdown文字列であること。"""
        parser = Pymupdf4llmParser()
        result = parser.parse(sample_pdf_path, start_page=1, end_page=1)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_parse_single_page(self, sample_pdf_path: Path) -> None:
        """1ページだけのパースが正常に動作すること。"""
        parser = Pymupdf4llmParser()
        result = parser.parse(sample_pdf_path, start_page=1, end_page=1)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_parse_page_range(self, sample_pdf_path: Path) -> None:
        """複数ページ範囲のパースが正常に動作すること。"""
        parser = Pymupdf4llmParser()
        total = parser.get_total_pages(sample_pdf_path)
        end = min(3, total)
        result = parser.parse(sample_pdf_path, start_page=1, end_page=end)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_nonexistent_pdf_raises(self, tmp_path: Path) -> None:
        """存在しないPDFパスで独自例外が発生すること。"""
        parser = Pymupdf4llmParser()
        with pytest.raises(PdfChunkError):
            parser.get_total_pages(tmp_path / "nonexistent.pdf")

    def test_parse_out_of_range_raises(self, sample_pdf_path: Path) -> None:
        """実際のページ数を超える範囲指定でエラーになること。"""
        parser = Pymupdf4llmParser()
        total = parser.get_total_pages(sample_pdf_path)
        with pytest.raises(PdfChunkError):
            parser.parse(sample_pdf_path, start_page=1, end_page=total + 1)
