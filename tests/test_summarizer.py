from pathlib import Path

import pytest


@pytest.mark.skip(reason="Summarizer実装待ち (#7)")
class TestDummySummarizer:
    """DummySummarizer のテスト。"""

    def test_returns_fixed_string(self) -> None:
        """固定文字列が返ること。"""
        # summarizer = DummySummarizer()
        # result = summarizer.summarize("任意のテキスト")
        # assert isinstance(result, str)
        # assert len(result) > 0

    def test_returns_same_for_different_inputs(self) -> None:
        """異なる入力に対して同じ固定文字列が返ること。"""
        # summarizer = DummySummarizer()
        # result1 = summarizer.summarize("テキスト1")
        # result2 = summarizer.summarize("テキスト2")
        # assert result1 == result2


@pytest.mark.skip(reason="Summarizer + IndexGenerator実装待ち (#4, #7)")
class TestIndexGeneratorWithSummarizer:
    """DummySummarizerをDIしたIndexGeneratorの結合テスト。"""

    def test_generate_with_summary(self, tmp_chunk_files: list[Path]) -> None:
        """summarize_chunks=Trueで要約が含まれること。"""
        # summarizer = DummySummarizer()
        # generator = DefaultIndexGenerator(summarizer=summarizer)
        # result = generator.generate(
        #     chunk_files=tmp_chunk_files,
        #     excerpt_lines=5,
        #     summarize_chunks=True,
        # )
        # assert isinstance(result, str)
