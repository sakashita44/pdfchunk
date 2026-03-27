from pathlib import Path
from unittest.mock import patch

import frontmatter
import pytest
from click.testing import CliRunner

from pdfchunk.cli import main
from pdfchunk.exceptions import PdfChunkError
from pdfchunk.parser import Parser


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


class FakeParser(Parser):
    """テスト用の Parser 実装。"""

    def __init__(self, total_pages: int = 25) -> None:
        self._total_pages = total_pages

    def get_total_pages(self, pdf_path: Path) -> int:
        return self._total_pages

    def parse(self, pdf_path: Path, start_page: int, end_page: int) -> str:
        return f"# Pages {start_page}-{end_page}\n\nContent for pages {start_page} to {end_page}.\n"


class ErrorParser(Parser):
    """get_total_pages / parse で PdfChunkError を送出する Parser。"""

    def __init__(self, *, fail_on: str) -> None:
        self._fail_on = fail_on

    def get_total_pages(self, pdf_path: Path) -> int:
        if self._fail_on == "get_total_pages":
            raise PdfChunkError(f"PDFを開けません: {pdf_path}")
        return 10

    def parse(self, pdf_path: Path, start_page: int, end_page: int) -> str:
        if self._fail_on == "parse":
            raise PdfChunkError(f"PDF解析に失敗しました: {pdf_path}")
        return "content"


class TestCLIHelp:
    """CLIヘルプが正常に表示されること。"""

    def test_main_help(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "split" in result.output
        assert "index" in result.output

    def test_split_help(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["split", "--help"])
        assert result.exit_code == 0
        assert "--chunk-size" in result.output
        assert "--overwrite" in result.output

    def test_index_help(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["index", "--help"])
        assert result.exit_code == 0
        assert "--excerpt-lines" in result.output
        assert "--summarize-chunks" in result.output
        assert "--overwrite" in result.output


class TestSplitCommand:
    """split コマンドの統合テスト。"""

    @patch("pdfchunk.cli.Pymupdf4llmParser", lambda: FakeParser(total_pages=25))
    def test_split_creates_chunk_files(self, runner: CliRunner, tmp_path: Path) -> None:
        """チャンクファイルが生成されること。"""
        dummy_pdf = tmp_path / "input" / "test.pdf"
        dummy_pdf.parent.mkdir()
        dummy_pdf.touch()
        out_dir = tmp_path / "output"

        result = runner.invoke(
            main, ["split", str(dummy_pdf), str(out_dir), "--chunk-size", "10"]
        )
        assert result.exit_code == 0, result.output

        md_files = sorted(out_dir.glob("*.md"))
        assert len(md_files) == 3
        assert [f.name for f in md_files] == ["0001.md", "0002.md", "0003.md"]

        # frontmatter の検証
        post = frontmatter.load(md_files[0], encoding="utf-8")
        assert post["source"] == "test.pdf"
        assert post["chunk"] == 1
        assert post["page_start"] == 1
        assert post["page_end"] == 10

        post_last = frontmatter.load(md_files[2], encoding="utf-8")
        assert post_last["page_start"] == 21
        assert post_last["page_end"] == 25

    def test_split_without_overwrite_fails_on_existing(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """--overwriteなしでoutput_dir内にチャンクファイルが存在する場合エラーになること。"""
        out_dir = tmp_path / "output"
        out_dir.mkdir()
        (out_dir / "0001.md").write_text("existing", encoding="utf-8")

        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.touch()

        result = runner.invoke(main, ["split", str(dummy_pdf), str(out_dir)])
        assert result.exit_code != 0
        assert "--overwrite" in result.output

    @patch("pdfchunk.cli.Pymupdf4llmParser", lambda: FakeParser(total_pages=5))
    def test_split_overwrite_removes_old_files(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """--overwriteありで古いチャンクファイルが残らないこと。"""
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.touch()
        out_dir = tmp_path / "output"
        out_dir.mkdir()
        for i in range(1, 4):
            (out_dir / f"{i:04d}.md").write_text("old", encoding="utf-8")

        # 5ページ, chunk_size=10 → 1チャンクのみ
        result = runner.invoke(
            main,
            [
                "split",
                str(dummy_pdf),
                str(out_dir),
                "--chunk-size",
                "10",
                "--overwrite",
            ],
        )
        assert result.exit_code == 0, result.output

        md_files = list(out_dir.glob("*.md"))
        assert len(md_files) == 1
        assert md_files[0].name == "0001.md"

    @patch("pdfchunk.cli.Pymupdf4llmParser", lambda: FakeParser(total_pages=5))
    def test_split_overwrite_preserves_index_md(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """--overwriteありでも index.md は削除されないこと。"""
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.touch()
        out_dir = tmp_path / "output"
        out_dir.mkdir()
        (out_dir / "0001.md").write_text("old chunk", encoding="utf-8")
        (out_dir / "index.md").write_text("index content", encoding="utf-8")

        result = runner.invoke(
            main,
            [
                "split",
                str(dummy_pdf),
                str(out_dir),
                "--chunk-size",
                "10",
                "--overwrite",
            ],
        )
        assert result.exit_code == 0, result.output
        assert (out_dir / "index.md").exists()
        assert (out_dir / "index.md").read_text(encoding="utf-8") == "index content"

    @patch("pdfchunk.cli.Pymupdf4llmParser", lambda: FakeParser(total_pages=1))
    def test_split_single_page_pdf(self, runner: CliRunner, tmp_path: Path) -> None:
        """1ページのPDFでチャンクが1つ生成されること。"""
        dummy_pdf = tmp_path / "single.pdf"
        dummy_pdf.touch()
        out_dir = tmp_path / "output"

        result = runner.invoke(main, ["split", str(dummy_pdf), str(out_dir)])
        assert result.exit_code == 0, result.output

        md_files = list(out_dir.glob("*.md"))
        assert len(md_files) == 1

        post = frontmatter.load(md_files[0], encoding="utf-8")
        assert post["page_start"] == 1
        assert post["page_end"] == 1

    @patch("pdfchunk.cli.Pymupdf4llmParser", lambda: FakeParser(total_pages=25))
    def test_split_fractional_last_chunk(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """端数ページの最終チャンクが正しい範囲になること（25ページ, chunk_size=10 → 最終は21-25）。"""
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.touch()
        out_dir = tmp_path / "output"

        result = runner.invoke(
            main, ["split", str(dummy_pdf), str(out_dir), "--chunk-size", "10"]
        )
        assert result.exit_code == 0, result.output

        post = frontmatter.load(out_dir / "0003.md", encoding="utf-8")
        assert post["page_start"] == 21
        assert post["page_end"] == 25

    @patch("pdfchunk.cli.Pymupdf4llmParser", lambda: FakeParser(total_pages=10000))
    def test_split_exceeds_max_chunks_raises(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """総チャンク数が9999を超える場合エラーになること。"""
        dummy_pdf = tmp_path / "big.pdf"
        dummy_pdf.touch()
        out_dir = tmp_path / "output"

        # 10000ページ, chunk_size=1 → 10000チャンク > 9999
        result = runner.invoke(
            main, ["split", str(dummy_pdf), str(out_dir), "--chunk-size", "1"]
        )
        assert result.exit_code != 0
        assert "9999" in result.output

    @patch("pdfchunk.cli.Pymupdf4llmParser", lambda: FakeParser(total_pages=0))
    def test_split_zero_pages_raises(self, runner: CliRunner, tmp_path: Path) -> None:
        """0ページのPDFの場合エラーになること。"""
        dummy_pdf = tmp_path / "empty.pdf"
        dummy_pdf.touch()
        out_dir = tmp_path / "output"

        result = runner.invoke(main, ["split", str(dummy_pdf), str(out_dir)])
        assert result.exit_code != 0
        assert "ページ数が0" in result.output

    @patch(
        "pdfchunk.cli.Pymupdf4llmParser",
        lambda: ErrorParser(fail_on="get_total_pages"),
    )
    def test_split_get_total_pages_error_message(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """get_total_pages が PdfChunkError を投げた場合、エラーメッセージが表示されること。"""
        dummy_pdf = tmp_path / "bad.pdf"
        dummy_pdf.touch()
        out_dir = tmp_path / "output"

        result = runner.invoke(main, ["split", str(dummy_pdf), str(out_dir)])
        assert result.exit_code != 0
        assert "PDFを開けません" in result.output

    @patch(
        "pdfchunk.cli.Pymupdf4llmParser",
        lambda: ErrorParser(fail_on="parse"),
    )
    def test_split_parse_error_message(self, runner: CliRunner, tmp_path: Path) -> None:
        """parse が PdfChunkError を投げた場合、エラーメッセージが表示されること。"""
        dummy_pdf = tmp_path / "bad.pdf"
        dummy_pdf.touch()
        out_dir = tmp_path / "output"

        result = runner.invoke(main, ["split", str(dummy_pdf), str(out_dir)])
        assert result.exit_code != 0
        assert "PDF解析に失敗しました" in result.output


class TestIndexCommand:
    """index コマンドの統合テスト。"""

    def test_index_creates_index_file(
        self, runner: CliRunner, tmp_chunk_files: list[Path]
    ) -> None:
        """index.mdが生成されること。"""
        out_dir = tmp_chunk_files[0].parent
        result = runner.invoke(main, ["index", str(out_dir)])
        assert result.exit_code == 0, result.output

        index_path = out_dir / "index.md"
        assert index_path.exists()

        content = index_path.read_text(encoding="utf-8")
        assert "test.pdf" in content
        assert "0001.md" in content
        assert "0002.md" in content
        assert "0003.md" in content

    def test_index_with_overwrite(
        self, runner: CliRunner, tmp_chunk_files: list[Path]
    ) -> None:
        """--overwriteありで既存index.mdを上書きできること。"""
        out_dir = tmp_chunk_files[0].parent
        (out_dir / "index.md").write_text("old index", encoding="utf-8")

        result = runner.invoke(main, ["index", str(out_dir), "--overwrite"])
        assert result.exit_code == 0, result.output

        content = (out_dir / "index.md").read_text(encoding="utf-8")
        assert content != "old index"
        assert "0001.md" in content

    def test_index_without_overwrite_fails_on_existing(
        self, runner: CliRunner, tmp_chunk_files: list[Path]
    ) -> None:
        """--overwriteなしでindex.mdが既存の場合エラーになること。"""
        out_dir = tmp_chunk_files[0].parent
        (out_dir / "index.md").write_text("existing", encoding="utf-8")

        result = runner.invoke(main, ["index", str(out_dir)])
        assert result.exit_code != 0
        assert "--overwrite" in result.output

    def test_index_summarize_without_summarizer_raises(
        self, runner: CliRunner, tmp_chunk_files: list[Path]
    ) -> None:
        """Summarizer未設定で--summarize-chunks指定時にエラーメッセージが表示されること。"""
        out_dir = tmp_chunk_files[0].parent
        result = runner.invoke(main, ["index", str(out_dir), "--summarize-chunks"])
        assert result.exit_code != 0
        assert "Summarizer" in result.output

    def test_index_no_chunk_files_raises(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """チャンクファイルがない場合エラーになること。"""
        result = runner.invoke(main, ["index", str(tmp_path)])
        assert result.exit_code != 0
        assert "チャンクファイルが見つかりません" in result.output
