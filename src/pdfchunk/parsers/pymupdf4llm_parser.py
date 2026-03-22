from pathlib import Path

import pymupdf
import pymupdf4llm

from pdfchunk.exceptions import PdfChunkError
from pdfchunk.parser import Parser


class Pymupdf4llmParser(Parser):
    """pymupdf4llm を使った Parser 実装。"""

    def parse(self, pdf_path: Path, start_page: int, end_page: int) -> str:
        """指定ページ範囲をMarkdown文字列に変換する。

        start_page, end_page は 1-indexed, inclusive。
        """
        total = self.get_total_pages(pdf_path)
        if start_page < 1 or end_page > total or start_page > end_page:
            raise PdfChunkError(
                f"ページ範囲が不正です: start_page={start_page}, end_page={end_page}, total={total}"
            )

        # pymupdf4llm.to_markdown の pages は 0-indexed
        pages = list(range(start_page - 1, end_page))
        try:
            return pymupdf4llm.to_markdown(str(pdf_path), pages=pages)
        except Exception as e:
            raise PdfChunkError(f"PDF解析に失敗しました: {pdf_path}") from e

    def get_total_pages(self, pdf_path: Path) -> int:
        """PDFの総ページ数を返す。"""
        if not pdf_path.exists():
            raise PdfChunkError(f"PDFファイルが見つかりません: {pdf_path}")
        try:
            doc = pymupdf.open(str(pdf_path))
        except Exception as e:
            raise PdfChunkError(f"PDFを開けません: {pdf_path}") from e
        try:
            return len(doc)
        finally:
            doc.close()
