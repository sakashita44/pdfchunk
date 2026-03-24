from pathlib import Path
from unittest.mock import patch

import frontmatter
import pytest
from click.testing import CliRunner

from pdfchunk.cli import main


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


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


def _mock_get_total_pages(_self: object, _pdf_path: Path) -> int:
    """テスト用: 総ページ数25を返す。"""
    return 25


def _mock_parse(_self: object, _pdf_path: Path, start_page: int, end_page: int) -> str:
    """テスト用: ページ範囲を示すMarkdownを返す。"""
    return f"# Pages {start_page}-{end_page}\n\nContent for pages {start_page} to {end_page}.\n"


class TestSplitCommand:
    """split コマンドの統合テスト。"""

    @patch(
        "pdfchunk.parsers.pymupdf4llm_parser.Pymupdf4llmParser.get_total_pages",
        _mock_get_total_pages,
    )
    @patch(
        "pdfchunk.parsers.pymupdf4llm_parser.Pymupdf4llmParser.parse",
        _mock_parse,
    )
    def test_split_creates_chunk_files(self, runner: CliRunner, tmp_path: Path) -> None:
        """チャンクファイルが生成されること。"""
        # click.Path(exists=True) のために仮ファイルを作成
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
        """--overwriteなしでoutput_dir内にmdが存在する場合エラーになること。"""
        out_dir = tmp_path / "output"
        out_dir.mkdir()
        (out_dir / "0001.md").write_text("existing", encoding="utf-8")

        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.touch()

        result = runner.invoke(main, ["split", str(dummy_pdf), str(out_dir)])
        assert result.exit_code != 0
        assert "--overwrite" in result.output

    @patch(
        "pdfchunk.parsers.pymupdf4llm_parser.Pymupdf4llmParser.get_total_pages",
        lambda _s, _p: 5,
    )
    @patch(
        "pdfchunk.parsers.pymupdf4llm_parser.Pymupdf4llmParser.parse",
        _mock_parse,
    )
    def test_split_overwrite_removes_old_files(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """--overwriteありで古いmdファイルが残らないこと。"""
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.touch()
        out_dir = tmp_path / "output"
        out_dir.mkdir()
        # 以前の実行で3チャンク生成されていたと仮定
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

    @patch(
        "pdfchunk.parsers.pymupdf4llm_parser.Pymupdf4llmParser.get_total_pages",
        lambda _s, _p: 1,
    )
    @patch(
        "pdfchunk.parsers.pymupdf4llm_parser.Pymupdf4llmParser.parse",
        _mock_parse,
    )
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

    @patch(
        "pdfchunk.parsers.pymupdf4llm_parser.Pymupdf4llmParser.get_total_pages",
        _mock_get_total_pages,
    )
    @patch(
        "pdfchunk.parsers.pymupdf4llm_parser.Pymupdf4llmParser.parse",
        _mock_parse,
    )
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

    @patch(
        "pdfchunk.parsers.pymupdf4llm_parser.Pymupdf4llmParser.get_total_pages",
        lambda _s, _p: 10000,
    )
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


@pytest.mark.skip(reason="indexコマンド実装待ち (#6)")
class TestIndexCommand:
    """index コマンドの統合テスト。"""

    def test_index_creates_index_file(self, runner: CliRunner, tmp_path: Path) -> None:
        """index.mdが生成されること。"""
        pytest.fail("未実装")

    def test_index_with_summarize(self, runner: CliRunner, tmp_path: Path) -> None:
        """--summarize-chunksオプションが動作すること。"""
        pytest.fail("未実装")

    def test_index_without_overwrite_fails_on_existing(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """--overwriteなしでindex.mdが既存の場合エラーになること。"""
        pytest.fail("未実装")

    def test_index_summarize_without_summarizer_raises(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Summarizer未設定で--summarize-chunks指定時にエラーメッセージが表示されること。"""
        pytest.fail("未実装")
