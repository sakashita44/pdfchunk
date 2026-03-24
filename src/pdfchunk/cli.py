import math
from pathlib import Path

import click
import frontmatter

from pdfchunk.exceptions import PdfChunkError
from pdfchunk.models import ChunkFileFormat
from pdfchunk.parsers.pymupdf4llm_parser import Pymupdf4llmParser

MAX_CHUNKS = 9999


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
    pdf = Path(pdf_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    existing_md = list(out.glob("*.md"))
    if existing_md and not overwrite:
        raise click.ClickException(
            f"出力先に既存のmdファイルがあります。--overwrite を指定してください: {out}"
        )
    if overwrite:
        for f in existing_md:
            f.unlink()

    parser = Pymupdf4llmParser()

    try:
        total_pages = parser.get_total_pages(pdf)
    except PdfChunkError as e:
        raise click.ClickException(str(e)) from e

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
        post = frontmatter.Post(
            content=md_content,
            source=meta.source,
            chunk=meta.chunk,
            page_start=meta.page_start,
            page_end=meta.page_end,
        )

        file_path = out / f"{chunk_num:04d}.md"
        file_path.write_text(frontmatter.dumps(post), encoding="utf-8")


@main.command()
@click.argument("output_dir", type=click.Path(exists=True))
@click.option(
    "--excerpt-lines",
    default=5,
    type=click.IntRange(min=0),
    help="各チャンクから抽出する抜粋行数。",
)
@click.option("--summarize-chunks", is_flag=True, help="各チャンクの要約を付加する。")
@click.option("--overwrite", is_flag=True, help="既存ファイルを上書きする。")
def index(
    output_dir: str, excerpt_lines: int, summarize_chunks: bool, overwrite: bool
) -> None:
    """チャンクファイル群からインデックスを生成する。"""
    raise click.ClickException("index: 未実装")
