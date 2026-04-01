import math
from dataclasses import asdict
from pathlib import Path

import click
import frontmatter

from pdfchunk.exceptions import PdfChunkError
from pdfchunk.index_generator import IndexGenerator
from pdfchunk.index_generators.default_index_generator import DefaultIndexGenerator
from pdfchunk.models import ChunkFileFormat
from pdfchunk.parser import Parser
from pdfchunk.parsers.pymupdf4llm_parser import Pymupdf4llmParser

MAX_CHUNKS = 9999
CHUNK_FILE_PATTERN = "[0-9][0-9][0-9][0-9].md"


def run_split(
    pdf: Path, out: Path, chunk_size: int, overwrite: bool, parser: Parser
) -> None:
    """split コマンドのオーケストレーション。"""
    out.mkdir(parents=True, exist_ok=True)

    existing_chunks = list(out.glob(CHUNK_FILE_PATTERN))
    if existing_chunks and not overwrite:
        raise click.ClickException(
            f"出力先に既存のチャンクファイルがあります。--overwrite を指定してください: {out}"
        )
    if overwrite:
        for f in existing_chunks:
            f.unlink()

    try:
        total_pages = parser.get_total_pages(pdf)
    except PdfChunkError as e:
        raise click.ClickException(str(e)) from e

    if total_pages <= 0:
        raise click.ClickException(f"PDFのページ数が0です: {pdf}")

    total_chunks = math.ceil(total_pages / chunk_size)
    if total_chunks > MAX_CHUNKS:
        raise click.ClickException(
            f"チャンク数が上限({MAX_CHUNKS})を超えます: {total_chunks}"
        )

    for i in range(total_chunks):
        chunk_num = i + 1
        start_page = i * chunk_size + 1
        end_page = min(start_page + chunk_size - 1, total_pages)

        try:
            md_content = parser.parse(pdf, start_page, end_page)
        except PdfChunkError as e:
            raise click.ClickException(str(e)) from e

        meta = ChunkFileFormat(
            source=pdf.name,
            chunk=chunk_num,
            page_start=start_page,
            page_end=end_page,
        )
        post = frontmatter.Post(content=md_content, **asdict(meta))

        file_path = out / f"{chunk_num:04d}.md"
        file_path.write_text(frontmatter.dumps(post), encoding="utf-8")


INDEX_FILE = "index.md"


def run_index(
    out: Path,
    excerpt_lines: int,
    summarize_chunks: bool,
    overwrite: bool,
    generator: IndexGenerator,
) -> None:
    """index コマンドのオーケストレーション。"""
    if not out.is_dir():
        raise click.ClickException(f"出力ディレクトリが存在しません: {out}")

    index_path = out / INDEX_FILE
    if index_path.exists() and not overwrite:
        raise click.ClickException(
            f"既存の {INDEX_FILE} があります。--overwrite を指定してください: {out}"
        )

    chunk_files = list(out.glob(CHUNK_FILE_PATTERN))
    if not chunk_files:
        raise click.ClickException(f"チャンクファイルが見つかりません: {out}")

    try:
        content = generator.generate(chunk_files, excerpt_lines, summarize_chunks)
    except PdfChunkError as e:
        raise click.ClickException(str(e)) from e

    index_path.write_text(content, encoding="utf-8")


@click.group()
def main() -> None:
    """PDFをページ単位でチャンク分割し、Markdown化・インデックス生成するCLIツール。"""


@main.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.argument("output_dir", type=click.Path())
@click.option(
    "--chunk-size",
    default=10,
    type=click.IntRange(min=1),
    help="チャンクあたりのページ数。",
)
@click.option("--overwrite", is_flag=True, help="既存ファイルを上書きする。")
def split(pdf_path: str, output_dir: str, chunk_size: int, overwrite: bool) -> None:
    """PDFをページ単位でチャンク分割する。"""
    parser = Pymupdf4llmParser()
    run_split(Path(pdf_path), Path(output_dir), chunk_size, overwrite, parser)


@main.command()
@click.argument("output_dir", type=click.Path(exists=True))
@click.option(
    "--excerpt-lines",
    default=5,
    type=click.IntRange(min=0),
    help="各チャンクから抽出する抜粋行数。",
)
@click.option("--overwrite", is_flag=True, help="既存ファイルを上書きする。")
def index(output_dir: str, excerpt_lines: int, overwrite: bool) -> None:
    """チャンクファイル群からインデックスを生成する。"""
    generator = DefaultIndexGenerator()
    run_index(Path(output_dir), excerpt_lines, False, overwrite, generator)


@main.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.argument("output_dir", type=click.Path())
@click.option(
    "--chunk-size",
    default=10,
    type=click.IntRange(min=1),
    help="チャンクあたりのページ数。",
)
@click.option(
    "--excerpt-lines",
    default=5,
    type=click.IntRange(min=0),
    help="各チャンクから抽出する抜粋行数。",
)
@click.option("--overwrite", is_flag=True, help="既存ファイルを上書きする。")
def run(
    pdf_path: str,
    output_dir: str,
    chunk_size: int,
    excerpt_lines: int,
    overwrite: bool,
) -> None:
    """PDFのチャンク分割からインデックス生成までを一括実行する。"""
    out = Path(output_dir)

    # split + index 両方の事前条件を一括チェック（部分的な成果物の残存を防止）
    if not overwrite:
        existing_chunks = list(out.glob(CHUNK_FILE_PATTERN)) if out.exists() else []
        if existing_chunks:
            raise click.ClickException(
                f"出力先に既存のチャンクファイルがあります。--overwrite を指定してください: {out}"
            )
        index_path = out / INDEX_FILE
        if index_path.exists():
            raise click.ClickException(
                f"既存の {INDEX_FILE} があります。--overwrite を指定してください: {out}"
            )

    parser = Pymupdf4llmParser()
    run_split(Path(pdf_path), out, chunk_size, overwrite, parser)
    generator = DefaultIndexGenerator()
    run_index(out, excerpt_lines, False, overwrite, generator)
