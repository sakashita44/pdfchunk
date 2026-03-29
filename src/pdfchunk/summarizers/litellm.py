from pdfchunk.summarizer import Summarizer

_SYSTEM_PROMPT = (
    "あなたは文書の要約を行うアシスタントです。"
    "与えられたテキストを簡潔に要約してください。日本語で回答してください。"
)


class LitellmSummarizer(Summarizer):
    """litellm経由で任意のLLMプロバイダを使用する要約器。

    APIキーは環境変数で管理する（litellmの規約に従う: OPENAI_API_KEY 等）。
    litellm は optional dependency であり、このクラスのインスタンス化時にインポートされる。
    """

    def __init__(self, model: str) -> None:
        """LitellmSummarizerを初期化する。

        Args:
            model: litellmのモデル名（例: "gpt-4o", "ollama/llama3"）。
        """
        try:
            import litellm as _litellm
        except ImportError as e:
            raise ImportError(
                "litellm が見つかりません。`pip install pdfchunk[ai]` でインストールしてください。"
            ) from e
        self._litellm = _litellm
        self._model = model

    def summarize(self, text: str) -> str:
        """litellm経由でテキストの要約を生成する。"""
        response = self._litellm.completion(
            model=self._model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content
