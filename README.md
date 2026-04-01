# pdfchunk

PDFをページ単位でチャンク分割し、Markdown化・インデックス生成するCLIツール。
LLMのコンテキストウィンドウに収まるサイズでPDFの内容を供給する用途を想定。

## インストール

```bash
git clone https://github.com/sakashita44/pdfchunk.git
cd pdfchunk
pip install .
```

Python 3.13 以上が必要。

## 使い方

### 一括実行（run）

PDFのチャンク分割からインデックス生成までを一括実行する。

```bash
pdfchunk run <pdf_path> <output_dir>
```

```bash
# 例: 5ページごとに分割して一括処理
pdfchunk run report.pdf output/ --chunk-size 5

# 抜粋行数を変更
pdfchunk run report.pdf output/ --excerpt-lines 10

# 既存ファイルを上書き
pdfchunk run report.pdf output/ --overwrite
```

| オプション        | デフォルト | 説明                           |
| ----------------- | ---------- | ------------------------------ |
| `--chunk-size`    | 10         | チャンクあたりのページ数       |
| `--excerpt-lines` | 5          | 各チャンクから抽出する抜粋行数 |
| `--overwrite`     | off        | 既存ファイルを削除して再生成   |

### チャンク生成のみ（split）

チャンク分割だけを個別に実行する。

```bash
pdfchunk split <pdf_path> <output_dir>
```

```bash
pdfchunk split report.pdf output/ --chunk-size 5
pdfchunk split report.pdf output/ --overwrite
```

| オプション     | デフォルト | 説明                                 |
| -------------- | ---------- | ------------------------------------ |
| `--chunk-size` | 10         | チャンクあたりのページ数             |
| `--overwrite`  | off        | 既存チャンクファイルを削除して再生成 |

### インデックス生成のみ（index）

`split` が生成したチャンクファイル群から `index.md` を生成する。

```bash
pdfchunk index <output_dir>
```

```bash
pdfchunk index output/ --excerpt-lines 10
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
