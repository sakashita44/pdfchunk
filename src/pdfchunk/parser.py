from abc import ABC, abstractmethod
from pathlib import Path


class Parser(ABC):
    @abstractmethod
    def parse(self, pdf_path: Path, start_page: int, end_page: int) -> str:
        """指定ページ範囲をMarkdown文字列に変換する。

        start_page, end_page は 1-indexed, inclusive。
        """
        ...

    @abstractmethod
    def get_total_pages(self, pdf_path: Path) -> int:
        """PDFの総ページ数を返す。"""
        ...
