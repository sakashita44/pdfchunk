# インタフェース定義

pdfchunk の全抽象インタフェース（ABC）とデータモデルの仕様。

## ChunkFileFormat

チャンクファイルのfrontmatter構造を表すデータクラス。

**モジュール:** `pdfchunk.models`

| フィールド   | 型    | 説明                               |
| ------------ | ----- | ---------------------------------- |
| `source`     | `str` | 元PDFファイル名（パスではない）    |
| `chunk`      | `int` | 1-indexed チャンク番号             |
| `page_start` | `int` | 開始ページ（1-indexed, inclusive） |
| `page_end`   | `int` | 終了ページ（1-indexed, inclusive） |

**バリデーション（`__post_init__`）:**

- `page_start >= 1`
- `page_end >= 1`
- `page_start <= page_end`

違反時は `ValueError` を送出する。

**frontmatter出力例:**

```yaml
---
source: "example.pdf"
chunk: 3
page_start: 21
page_end: 30
---
```

## Parser

PDF → Markdown変換の抽象インタフェース。

**モジュール:** `pdfchunk.parser`

```python
class Parser(ABC):
    @abstractmethod
    def parse(self, pdf_path: Path, start_page: int, end_page: int) -> str: ...

    @abstractmethod
    def get_total_pages(self, pdf_path: Path) -> int: ...
```

| メソッド          | 引数                                                 | 戻り値 | 説明                                                         |
| ----------------- | ---------------------------------------------------- | ------ | ------------------------------------------------------------ |
| `parse`           | `pdf_path: Path`, `start_page: int`, `end_page: int` | `str`  | 指定ページ範囲（1-indexed, inclusive）をMarkdown文字列に変換 |
| `get_total_pages` | `pdf_path: Path`                                     | `int`  | PDFの総ページ数を返す                                        |

**初期実装予定:** `Pymupdf4llmParser`（pymupdf4llm使用）

## IndexGenerator

チャンクファイル群からindex.mdを生成する抽象インタフェース。

**モジュール:** `pdfchunk.index_generator`

```python
class IndexGenerator(ABC):
    @abstractmethod
    def generate(
        self,
        chunk_files: list[Path],
        excerpt_lines: int,
        summarize_chunks: bool,
    ) -> str: ...
```

| メソッド   | 引数                                                                      | 戻り値 | 説明                                       |
| ---------- | ------------------------------------------------------------------------- | ------ | ------------------------------------------ |
| `generate` | `chunk_files: list[Path]`, `excerpt_lines: int`, `summarize_chunks: bool` | `str`  | チャンクファイル群からindex.mdの内容を生成 |

**仕様:**

- frontmatterからメタ情報（source, chunk, page_start, page_end）を構造的に取得する
- content部分からexcerpt_lines行を機械的に抽出する
- 出力フォーマットはリスト形式（テーブルではない）
- `summarize_chunks=True` 時はコンストラクタで注入された Summarizer を使用する

## Summarizer

テキスト要約の抽象インタフェース。IndexGeneratorにDIで注入する。

**モジュール:** `pdfchunk.summarizer`

```python
class Summarizer(ABC):
    @abstractmethod
    def summarize(self, text: str) -> str: ...
```

| メソッド    | 引数        | 戻り値 | 説明                 |
| ----------- | ----------- | ------ | -------------------- |
| `summarize` | `text: str` | `str`  | テキストの要約を返す |

**実装予定:**

- `LitellmSummarizer(model: str)` — litellm経由で任意のLLMプロバイダを統一呼び出し
- `DummySummarizer` — 固定文字列を返却（テスト・開発用）
