from pathlib import Path

import pytest


@pytest.mark.skip(reason="IndexGenerator実装待ち (#4)")
class TestIndexGenerator:
    """IndexGenerator実装のテスト。"""

    def test_generate_without_summary(self, tmp_chunk_files: list[Path]) -> None:
        """要約なしでindex.md内容が生成されること。"""
        # generator = DefaultIndexGenerator()
        # result = generator.generate(
        #     chunk_files=tmp_chunk_files,
        #     excerpt_lines=5,
        #     summarize_chunks=False,
        # )
        # assert isinstance(result, str)
        # assert "0001.md" in result

    def test_generate_contains_metadata(self, tmp_chunk_files: list[Path]) -> None:
        """生成されたindexにチャンクのメタ情報が含まれること。"""
        # generator = DefaultIndexGenerator()
        # result = generator.generate(
        #     chunk_files=tmp_chunk_files,
        #     excerpt_lines=5,
        #     summarize_chunks=False,
        # )
        # assert "test.pdf" in result
        # assert "page_start" in result or "1" in result

    def test_generate_with_excerpt(self, tmp_chunk_files: list[Path]) -> None:
        """抜粋行が含まれること。"""
        # generator = DefaultIndexGenerator()
        # result = generator.generate(
        #     chunk_files=tmp_chunk_files,
        #     excerpt_lines=3,
        #     summarize_chunks=False,
        # )
        # assert "チャンク" in result

    def test_generate_respects_excerpt_lines_zero(
        self, tmp_chunk_files: list[Path]
    ) -> None:
        """excerpt_lines=0で抜粋が含まれないこと。"""
        # generator = DefaultIndexGenerator()
        # result = generator.generate(
        #     chunk_files=tmp_chunk_files,
        #     excerpt_lines=0,
        #     summarize_chunks=False,
        # )
        # assert isinstance(result, str)
