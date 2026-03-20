import click


@click.group()
def main() -> None:
    """PDFをページ単位でチャンク分割し、Markdown化・インデックス生成するCLIツール。"""


@main.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.argument("output_dir", type=click.Path())
@click.option("--chunk-size", default=10, help="チャンクあたりのページ数。")
@click.option("--overwrite", is_flag=True, help="既存ファイルを上書きする。")
def split(pdf_path: str, output_dir: str, chunk_size: int, overwrite: bool) -> None:
    """PDFをページ単位でチャンク分割する。"""
    click.echo("split: 未実装")


@main.command()
@click.argument("output_dir", type=click.Path(exists=True))
@click.option("--excerpt-lines", default=5, help="各チャンクから抽出する抜粋行数。")
@click.option("--summarize-chunks", is_flag=True, help="各チャンクの要約を付加する。")
@click.option("--overwrite", is_flag=True, help="既存ファイルを上書きする。")
def index(
    output_dir: str, excerpt_lines: int, summarize_chunks: bool, overwrite: bool
) -> None:
    """チャンクファイル群からインデックスを生成する。"""
    click.echo("index: 未実装")
