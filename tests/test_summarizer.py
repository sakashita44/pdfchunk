from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pdfchunk.exceptions import PdfChunkError
from pdfchunk.index_generators import DefaultIndexGenerator
from pdfchunk.summarizers import DummySummarizer


class TestDummySummarizer:
    """DummySummarizer のテスト。"""

    def test_returns_fixed_string(self) -> None:
        """固定文字列が返ること。"""
        summarizer = DummySummarizer()
        result = summarizer.summarize("任意のテキスト")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_same_for_different_inputs(self) -> None:
        """異なる入力に対して同じ固定文字列が返ること。"""
        summarizer = DummySummarizer()
        result1 = summarizer.summarize("テキスト1")
        result2 = summarizer.summarize("テキスト2")
        assert result1 == result2


class TestIndexGeneratorWithSummarizer:
    """DummySummarizerをDIしたIndexGeneratorの結合テスト。"""

    def test_generate_with_summary(self, tmp_chunk_files: list[Path]) -> None:
        """summarize_chunks=Trueで要約が含まれること。"""
        summarizer = DummySummarizer()
        generator = DefaultIndexGenerator(summarizer=summarizer)
        result = generator.generate(
            chunk_files=tmp_chunk_files,
            excerpt_lines=5,
            summarize_chunks=True,
        )
        assert isinstance(result, str)
        assert DummySummarizer.FIXED_SUMMARY in result
        assert "summary:" in result

    def test_summarizer_not_called_when_flag_off(
        self, tmp_chunk_files: list[Path]
    ) -> None:
        """summarize_chunks=FalseならSummarizerがDIされていても呼ばれないこと。"""
        summarizer = DummySummarizer()
        generator = DefaultIndexGenerator(summarizer=summarizer)
        result = generator.generate(
            chunk_files=tmp_chunk_files,
            excerpt_lines=5,
            summarize_chunks=False,
        )
        assert DummySummarizer.FIXED_SUMMARY not in result


class TestLitellmSummarizer:
    """LitellmSummarizer のテスト。"""

    def test_import_error_when_litellm_missing(self) -> None:
        """litellm 未インストール時に明確なエラーメッセージが出ること。"""
        with patch.dict("sys.modules", {"litellm": None}):
            with pytest.raises(ImportError, match="litellm が見つかりません"):
                from pdfchunk.summarizers.litellm import LitellmSummarizer

                LitellmSummarizer(model="gpt-4o")

    def test_summarize_returns_content(self) -> None:
        """モックしたLLM応答からテキストが返ること。"""
        with patch.dict("sys.modules", {"litellm": MagicMock()}):
            from pdfchunk.summarizers.litellm import LitellmSummarizer

            summarizer = LitellmSummarizer(model="gpt-4o")

            mock_response = MagicMock()
            mock_response.choices[0].message.content = "要約テキスト"
            summarizer._litellm.completion.return_value = mock_response

            result = summarizer.summarize("テスト入力")
            assert result == "要約テキスト"

    def test_summarize_raises_on_none_content(self) -> None:
        """LLM応答が None の場合に PdfChunkError が送出されること。"""
        with patch.dict("sys.modules", {"litellm": MagicMock()}):
            from pdfchunk.summarizers.litellm import LitellmSummarizer

            summarizer = LitellmSummarizer(model="gpt-4o")

            mock_response = MagicMock()
            mock_response.choices[0].message.content = None
            summarizer._litellm.completion.return_value = mock_response

            with pytest.raises(PdfChunkError, match="テキストが含まれていません"):
                summarizer.summarize("テスト入力")
