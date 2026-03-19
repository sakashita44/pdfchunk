# pdfchunk

## プロジェクト概要

PDFをページ単位でチャンク分割し、Markdown化・インデックス生成するPython CLIツール。

- 入力: 1つのPDFファイル
- 出力: 1ディレクトリ内にチャンクmdファイル群 + [index.md](http://index.md)
- 用途: LLMコンテキストウィンドウに収まるサイズでPDFの内容を供給する（将来的に読み取りをMCP化計画）

## アーキテクチャ

```jsx
CLI (orchestrator)
├── Parser IF  ← Pymupdf4llmParser
├── IndexGenerator IF
│   └── Summarizer IF  ← LitellmSummarizer / DummySummarizer (summarize_chunks=True時のみ)
└── ChunkFileFormat (frontmatter構造定義, dataclass/TypedDict)
```

- 全外部依存はIF（Protocol/ABC）経由で差し替え可能にする
- DIパターン: コンストラクタインジェクション
- CLIがオーケストレータとして各IFを組み立てる

## データ契約

### チャンクファイル構造

YAML frontmatter + パーサ生出力のMarkdown本文。

```yaml
---
source: "example.pdf"
chunk: 3
pages: [21, 30]
---
（Markdown本文）
```

- `source` — 元PDFファイル名（パスではない）
- `chunk` — 1-indexed チャンク番号
- `pages` — [start, end] inclusive（1-indexed）
- バージョンフィールドは設けない

この構造を `ChunkFileFormat` として `dataclass` または `TypedDict` で型定義する。frontmatterの読み書きには適切なライブラリ（例: `python-frontmatter`）を使用してよい。

### 出力ディレクトリ構造

```jsx
output_dir/
├── 0001.md
├── 0002.md
├── ...
└── index.md
```

- 1 PDF → 1ディレクトリ、フラット構造
- ファイル命名: `NNNN.md`（ゼロパディング4桁）

## インタフェース定義

### Parser

```python
from abc import ABC, abstractmethod
from pathlib import Path

class Parser(ABC):
    @abstractmethod
    def parse(self, pdf_path: Path, start_page: int, end_page: int) -> str:
        """指定ページ範囲をMarkdown文字列に変換する。
        start_page, end_page は 1-indexed, inclusive。"""
        ...

    @abstractmethod
    def get_total_pages(self, pdf_path: Path) -> int:
        """PDFの総ページ数を返す。"""
        ...
```

初期実装: `Pymupdf4llmParser`（pymupdf4llmを使用）

### IndexGenerator

```python
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
        summarize_chunks: Trueの場合、Summarizer IFで各チャンクの要約を付加。"""
        ...
```

- frontmatterからメタ情報（source, chunk, pages）を構造的に取得する
- content部分（frontmatter以降）からexcerpt_lines行を機械的に抽出する
- 出力フォーマットはリスト形式（テーブルではない）
- `summarize_chunks=True` 時はコンストラクタで注入された Summarizer を使用する
- md生成ライブラリへの依存は許容

### Summarizer

```python
from abc import ABC, abstractmethod

class Summarizer(ABC):
    @abstractmethod
    def summarize(self, text: str) -> str:
        """テキストの要約を返す。"""
        ...
```

- IndexGeneratorにDIで注入する
- 粒度はチャンク単位のみ。文書全体の要約機能は不要
- 初期実装: `LitellmSummarizer(model: str)` — litellm経由で任意のLLMプロバイダを統一呼び出し。model名（例: `"gpt-4o"`, `"ollama/llama3"`）をコンストラクタで受け取る
- フォールバック実装: `DummySummarizer` — 固定文字列を返却。APIキー不要。テスト・開発用
- APIキーは環境変数で管理（litellmの規約に従う: `OPENAI_API_KEY` 等）
- LLM APIの統一IFは設けない。Summarizer IFが抽象境界であり、litellmは実装詳細

## CLI仕様

### コマンド体系

```bash
# チャンク生成
pdfchunk split <pdf_path> <output_dir> [options]

# インデックス生成
pdfchunk index <output_dir> [options]
```

### オプション

- `--chunk-size` — チャンクあたりのページ数（default: 10）
- `--excerpt-lines` — indexに含める各チャンクの抜粋行数（default: 5）
- `--summarize-chunks` — index生成時に各チャンクの要約を付加する（default: off）
- `--overwrite` — 既存ファイルを上書きする（default: off、既存時はエラー）

### オーケストレーション

`split` コマンドの処理フロー:

1. `Parser.get_total_pages()` で総ページ数を取得
1. `chunk_size` でページ範囲リストを生成（CLIの単純ロジック）
1. 各範囲に対して `Parser.parse()` を呼び出し
1. 返却されたMarkdownにYAML frontmatterを付与
1. `NNNN.md` として書き出し

`index` コマンドの処理フロー:

1. `output_dir` 内の `index.md` 以外の `*.md` を走査
1. `IndexGenerator.generate()` に渡す
1. 結果を `index.md` として書き出し

## 制約

- チャンク境界は純粋にページ数ベース。意味的な分割は行わない
- 文途中でチャンクが切れることを許容する
- AI要約はindex生成時のスイッチ方式。既存indexへの後追い追記ではない
- 人間によるメモの追加に構造的制約を課さない（CLI出力のみが構造規定対象）
- 再生成は `--overwrite` フラグによる全上書き。差分更新は行わない
- MCP対応は後日。現時点ではCLIのみ

## 依存ライブラリ

- `pymupdf4llm` — PDF→Markdown変換（Parser実装）
- `python-frontmatter` — YAML frontmatter読み書き
- `click` or `typer` — CLI フレームワーク
- `litellm` — Summarizer実装（summarize-chunks使用時のみ、optional dependency: `pip install pdfchunk[ai]`）

## テスト方針

- 各IFの実装に対してユニットテストを書く
- Parser: 既知のPDFに対するページ数取得・Markdown出力の検証
- IndexGenerator: frontmatter付きmdファイルのモックからindex生成を検証
- Summarizer: DummySummarizerを使ってIndexGeneratorとの結合を検証。LitellmSummarizerの単体テストはオプショナル
- CLI: サブプロセス呼び出しまたはClick/Typerのテストランナーで統合テスト
