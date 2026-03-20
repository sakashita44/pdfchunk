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


@pytest.mark.skip(reason="splitコマンド実装待ち (#5)")
class TestSplitCommand:
    """split コマンドの統合テスト。"""

    def test_split_creates_chunk_files(
        self, runner: CliRunner, sample_pdf_path: str, tmp_path: str
    ) -> None:
        """チャンクファイルが生成されること。"""
        # result = runner.invoke(main, ["split", str(sample_pdf_path), str(tmp_path)])
        # assert result.exit_code == 0

    def test_split_without_overwrite_fails_on_existing(
        self, runner: CliRunner, tmp_path: str
    ) -> None:
        """--overwriteなしで既存ディレクトリにファイルがある場合エラーになること。"""


@pytest.mark.skip(reason="indexコマンド実装待ち (#6)")
class TestIndexCommand:
    """index コマンドの統合テスト。"""

    def test_index_creates_index_file(self, runner: CliRunner, tmp_path: str) -> None:
        """index.mdが生成されること。"""

    def test_index_with_summarize(self, runner: CliRunner, tmp_path: str) -> None:
        """--summarize-chunksオプションが動作すること。"""
