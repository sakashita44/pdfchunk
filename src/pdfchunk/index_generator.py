from abc import ABC, abstractmethod
from pathlib import Path


class IndexGenerator(ABC):
    @abstractmethod
    def generate(
        self,
        chunk_files: list[Path],
        excerpt_lines: int,
        summarize_chunks: bool,
    ) -> str:
        """チャンクファイル群からindex.mdの内容を生成する。

        excerpt_lines: 各チャンクから抽出する抜粋行数。
        summarize_chunks: Trueの場合、Summarizer IFで各チャンクの要約を付加。
        """
        ...
