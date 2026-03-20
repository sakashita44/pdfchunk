from abc import ABC, abstractmethod


class Summarizer(ABC):
    @abstractmethod
    def summarize(self, text: str) -> str:
        """テキストの要約を返す。"""
        ...
