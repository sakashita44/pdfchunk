from pathlib import Path

import frontmatter
import pytest

from pdfchunk.models import ChunkFileFormat

# テスト用PDFの配置ディレクトリ
PDF_FIXTURES_DIR = Path(__file__).parent / "fixtures" / "pdfs"


def _discover_pdfs() -> list[Path]:
    """fixtures/pdfs/ 内の全PDFファイルを検出する。"""
    if not PDF_FIXTURES_DIR.exists():
        return []
    return sorted(PDF_FIXTURES_DIR.glob("*.pdf"))


_pdf_files = _discover_pdfs()


@pytest.fixture(
    params=_pdf_files if _pdf_files else [None], ids=lambda p: p.name if p else "no-pdf"
)
def sample_pdf_path(request: pytest.FixtureRequest) -> Path:
    """テスト用PDFのパスを返す。

    tests/fixtures/pdfs/ 内の全PDFに対してパラメタライズされる。
    ファイルが存在しない場合はテストをスキップする。
    """
    if request.param is None:
        pytest.skip(f"テスト用PDFが未配置: {PDF_FIXTURES_DIR}")
    return request.param


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
        lines = "\n".join(f"チャンク{c.chunk}の行{i}" for i in range(3, 8))
        post = frontmatter.Post(
            content=f"# チャンク{c.chunk}の本文\n\nこれはチャンク{c.chunk}のテスト用本文です。\n{lines}\n",
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
