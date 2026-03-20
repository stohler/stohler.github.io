from __future__ import annotations

import json

import requests

from .models import Article


class AISummarizer:
    def __init__(self, api_key: str | None, model: str) -> None:
        self.model = model
        self.enabled = bool(api_key)
        self._api_key = api_key or ""

    def summarize_for_x(self, topic: str, article: Article) -> str:
        if not self.enabled:
            return self._fallback_summary(topic, article)

        instruction = (
            "Você é um editor de notícias para redes sociais. "
            "Resuma em português uma notícia internacional sobre o tema informado, "
            "com linguagem objetiva, sem sensacionalismo e com no máximo 170 caracteres. "
            "Não inclua hashtags, links, @ ou emojis."
        )

        article_payload = {
            "tema": topic,
            "titulo": article.title,
            "fonte": article.source,
            "resumo_original": article.summary,
        }

        prompt = f"{instruction}\n\nDados da notícia:\n{json.dumps(article_payload, ensure_ascii=False)}"
        request_payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3},
        }

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                params={"key": self._api_key},
                json=request_payload,
                timeout=(8, 30),
            )
            response.raise_for_status()
            data = response.json()
            text = self._extract_text(data)
            if not text:
                return self._fallback_summary(topic, article)
            return text[:170].strip()
        except Exception:
            return self._fallback_summary(topic, article)

    @staticmethod
    def _extract_text(data: dict) -> str:
        candidates = data.get("candidates", []) or []
        for candidate in candidates:
            content = candidate.get("content", {}) or {}
            parts = content.get("parts", []) or []
            for part in parts:
                text = (part.get("text") or "").strip()
                if text:
                    return text
        return ""

    @staticmethod
    def _fallback_summary(topic: str, article: Article) -> str:
        if article.summary:
            return article.summary[:170].strip()
        return f"Atualização sobre {topic}: {article.title[:140].strip()}"

