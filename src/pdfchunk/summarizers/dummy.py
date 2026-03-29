from pdfchunk.summarizer import Summarizer


class DummySummarizer(Summarizer):
    """固定文字列を返すダミー要約器。APIキー不要。テスト・開発用。"""

    FIXED_SUMMARY = "（要約は利用できません）"

    def summarize(self, text: str) -> str:
        """テキストに関わらず固定文字列を返す。"""
        return self.FIXED_SUMMARY
