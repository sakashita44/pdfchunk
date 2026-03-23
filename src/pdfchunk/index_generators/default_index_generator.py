from pathlib import Path

import frontmatter

from pdfchunk.exceptions import PdfChunkError
from pdfchunk.index_generator import IndexGenerator
from pdfchunk.summarizer import Summarizer


class DefaultIndexGenerator(IndexGenerator):
    """IndexGeneratorのデフォルト実装。python-frontmatterでメタ情報を読み取る。"""

    def __init__(self, summarizer: Summarizer | None = None) -> None:
        self._summarizer = summarizer

    def generate(
        self,
        chunk_files: list[Path],
        excerpt_lines: int,
        summarize_chunks: bool,
    ) -> str:
        if summarize_chunks and self._summarizer is None:
            raise PdfChunkError(
                "Summarizerが設定されていません。--summarize-chunks を外してください"
            )

        sorted_files = sorted(chunk_files, key=lambda f: f.name)

        # sourceはすべてのチャンクで同一の前提。最初のチャンクから取得
        source = ""
        entries: list[str] = []

        for file_path in sorted_files:
            try:
                post = frontmatter.load(file_path, encoding="utf-8")
            except Exception as e:
                raise PdfChunkError(
                    f"チャンクファイルの読み込みに失敗しました: {file_path}"
                ) from e
            meta_source = post.get("source", "")
            if not source:
                source = meta_source
            chunk_num = post.get("chunk", 0)
            page_start = post.get("page_start", 0)
            page_end = post.get("page_end", 0)

            entry_lines = [f"- {file_path.name}"]
            entry_lines.append(f"  - chunk: {chunk_num}")
            entry_lines.append(f"  - pages: {page_start}-{page_end}")

            # 抜粋（空行・空白のみの行を除外して情報密度を高める）
            if excerpt_lines > 0:
                content_lines = post.content.splitlines()
                excerpt = [line for line in content_lines if line.strip()][
                    :excerpt_lines
                ]
                if excerpt:
                    entry_lines.append("  - excerpt:")
                    for line in excerpt:
                        entry_lines.append(f"    - {line}")

            # 要約
            if summarize_chunks and self._summarizer is not None:
                summary = self._summarizer.summarize(post.content)
                entry_lines.append(f"  - summary: {summary}")

            entries.append("\n".join(entry_lines))

        # Markdown組み立て
        parts = []
        if source:
            parts.append(f"# {source}")
        else:
            parts.append("# Index")
        parts.append("")
        parts.append("## Chunks")
        parts.append("")
        if entries:
            parts.append("\n".join(entries))

        return "\n".join(parts)
