# Changelog

[Keep a Changelog](https://keepachangelog.com/) 形式、[Semantic Versioning](https://semver.org/) 準拠。

## [Unreleased]

### Added

- `run` コマンド: split + index を一括実行
- `split` コマンド: PDFを固定ページ数ごとにMarkdownチャンクファイルへ分割
- `index` コマンド: チャンクファイル群からメタ情報・抜粋付きの `index.md` を生成
- YAML frontmatter 付きチャンクファイル出力（source, chunk, page_start, page_end）
- `--chunk-size`, `--excerpt-lines`, `--overwrite` オプション
- Pymupdf4llmParser による PDF→Markdown 変換
- DefaultIndexGenerator によるインデックス生成

[Unreleased]: https://github.com/sakashita44/pdfchunk/commits/main
