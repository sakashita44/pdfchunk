from pathlib import Path

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


@pytest.mark.skip(reason="splitコマンド実装待ち (#5)")
class TestSplitCommand:
    """split コマンドの統合テスト。"""

    def test_split_creates_chunk_files(
        self, runner: CliRunner, sample_pdf_path: Path, tmp_path: Path
    ) -> None:
        """チャンクファイルが生成されること。"""
        # result = runner.invoke(main, ["split", str(sample_pdf_path), str(tmp_path)])
        # assert result.exit_code == 0

    def test_split_without_overwrite_fails_on_existing(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """--overwriteなしでoutput_dir内にmdが存在する場合エラーになること。"""

    def test_split_overwrite_removes_old_files(
        self, runner: CliRunner, sample_pdf_path: Path, tmp_path: Path
    ) -> None:
        """--overwriteありで古いmdファイルが残らないこと。"""

    def test_split_single_page_pdf(
        self, runner: CliRunner, sample_pdf_path: Path, tmp_path: Path
    ) -> None:
        """1ページのPDFでチャンクが1つ生成されること。"""

    def test_split_fractional_last_chunk(
        self, runner: CliRunner, sample_pdf_path: Path, tmp_path: Path
    ) -> None:
        """端数ページの最終チャンクが正しい範囲になること（例: 55ページ, chunk_size=10 → 最終は51-55）。"""

    def test_split_exceeds_max_chunks_raises(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """総チャンク数が9999を超える場合エラーになること。"""


@pytest.mark.skip(reason="indexコマンド実装待ち (#6)")
class TestIndexCommand:
    """index コマンドの統合テスト。"""

    def test_index_creates_index_file(self, runner: CliRunner, tmp_path: Path) -> None:
        """index.mdが生成されること。"""

    def test_index_with_summarize(self, runner: CliRunner, tmp_path: Path) -> None:
        """--summarize-chunksオプションが動作すること。"""

    def test_index_without_overwrite_fails_on_existing(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """--overwriteなしでindex.mdが既存の場合エラーになること。"""

    def test_index_summarize_without_summarizer_raises(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Summarizer未設定で--summarize-chunks指定時にエラーメッセージが表示されること。"""
