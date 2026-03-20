from pathlib import Path

import pytest


@pytest.mark.skip(reason="Parser実装待ち (#3)")
class TestPymupdf4llmParser:
    """Pymupdf4llmParser のテスト。"""

    def test_get_total_pages(self, sample_pdf_path: Path) -> None:
        """総ページ数が正の整数で返ること。"""

        # parser = Pymupdf4llmParser()
        # total = parser.get_total_pages(sample_pdf_path)
        # assert total > 0

    def test_parse_returns_markdown(self, sample_pdf_path: Path) -> None:
        """指定範囲のパース結果が空でないMarkdown文字列であること。"""
        # parser = Pymupdf4llmParser()
        # result = parser.parse(sample_pdf_path, start_page=1, end_page=1)
        # assert isinstance(result, str)
        # assert len(result) > 0

    def test_parse_page_range(self, sample_pdf_path: Path) -> None:
        """複数ページ範囲のパースが正常に動作すること。"""
        # parser = Pymupdf4llmParser()
        # result = parser.parse(sample_pdf_path, start_page=1, end_page=3)
        # assert isinstance(result, str)
