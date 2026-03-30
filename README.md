# pdfchunk

PDFをページ単位でチャンク分割し、Markdown化・インデックス生成するCLIツール。
LLMのコンテキストウィンドウに収まるサイズでPDFの内容を供給する用途を想定。

## インストール

```bash
pip install pdfchunk
```

Python 3.13 以上が必要。

## 使い方

### チャンク生成（split）

PDFを固定ページ数ごとに分割し、Markdownファイルとして出力する。

```bash
pdfchunk split <pdf_path> <output_dir>
```

```bash
# 例: 5ページごとに分割
pdfchunk split report.pdf output/ --chunk-size 5

# 既存のチャンクファイルを上書き
pdfchunk split report.pdf output/ --overwrite
```

| オプション     | デフォルト | 説明                                 |
| -------------- | ---------- | ------------------------------------ |
| `--chunk-size` | 10         | チャンクあたりのページ数             |
| `--overwrite`  | off        | 既存チャンクファイルを削除して再生成 |

### インデックス生成（index）

チャンクファイル群から `index.md` を生成する。各チャンクのメタ情報と冒頭の抜粋を一覧化する。

```bash
pdfchunk index <output_dir>
```

```bash
# 抜粋行数を変更
pdfchunk index output/ --excerpt-lines 10

# 既存の index.md を上書き
pdfchunk index output/ --overwrite
```

| オプション        | デフォルト | 説明                           |
| ----------------- | ---------- | ------------------------------ |
| `--excerpt-lines` | 5          | 各チャンクから抽出する抜粋行数 |
| `--overwrite`     | off        | 既存の `index.md` を上書き     |

## 出力フォーマット

### チャンクファイル（`NNNN.md`）

YAML frontmatter + Markdown本文で構成される。

```yaml
---
source: "example.pdf"
chunk: 3
page_start: 21
page_end: 30
---
（PDFから変換されたMarkdown本文）
```

| フィールド   | 説明                             |
| ------------ | -------------------------------- |
| `source`     | 元PDFのファイル名                |
| `chunk`      | チャンク番号（1始まり）          |
| `page_start` | 開始ページ（1始まり、inclusive） |
| `page_end`   | 終了ページ（1始まり、inclusive） |

### ディレクトリ構造

```text
output_dir/
├── 0001.md
├── 0002.md
├── ...
└── index.md
```

## ライセンス

[MIT](LICENSE)
