from pathlib import Path

import frontmatter
import pytest

from pdfchunk.models import ChunkFileFormat

# テスト用PDFの配置ディレクトリ
PDF_FIXTURES_DIR = Path(__file__).parent / "fixtures" / "pdfs"


@pytest.fixture()
def sample_pdf_path() -> Path:
    """テスト用PDFのパスを返す。

    tests/fixtures/pdfs/ にPDFを配置して使用する。
    ファイルが存在しない場合はテストをスキップする。
    """
    pdf_path = PDF_FIXTURES_DIR / "sample.pdf"
    if not pdf_path.exists():
        pytest.skip(f"テスト用PDFが未配置: {pdf_path}")
    return pdf_path


@pytest.fixture()
def tmp_chunk_files(tmp_path: Path) -> list[Path]:
    """frontmatter付きチャンクmdファイルを生成して返す。"""
    chunks = [
        ChunkFileFormat(source="test.pdf", chunk=1, page_start=1, page_end=10),
        ChunkFileFormat(source="test.pdf", chunk=2, page_start=11, page_end=20),
        ChunkFileFormat(source="test.pdf", chunk=3, page_start=21, page_end=25),
    ]
    files: list[Path] = []
    for c in chunks:
        post = frontmatter.Post(
            content=f"# チャンク{c.chunk}の本文\n\nこれはテスト用の本文です。\n行3\n行4\n行5\n行6\n",
            **{
                "source": c.source,
                "chunk": c.chunk,
                "page_start": c.page_start,
                "page_end": c.page_end,
            },
        )
        file_path = tmp_path / f"{c.chunk:04d}.md"
        file_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        files.append(file_path)
    return files
