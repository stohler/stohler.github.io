from __future__ import annotations

import json

from openai import OpenAI

from .models import Article


class AISummarizer:
    def __init__(self, api_key: str | None, model: str) -> None:
        self.model = model
        self.enabled = bool(api_key)
        self._client = OpenAI(api_key=api_key) if api_key else None

    def summarize_for_x(self, topic: str, article: Article) -> str:
        if not self.enabled or not self._client:
            return self._fallback_summary(topic, article)

        prompt = (
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

        try:
            response = self._client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": json.dumps(article_payload, ensure_ascii=False)},
                ],
                temperature=0.3,
            )
            text = (response.output_text or "").strip()
            if not text:
                return self._fallback_summary(topic, article)
            return text[:170].strip()
        except Exception:
            return self._fallback_summary(topic, article)

    @staticmethod
    def _fallback_summary(topic: str, article: Article) -> str:
        if article.summary:
            return article.summary[:170].strip()
        return f"Atualização sobre {topic}: {article.title[:140].strip()}"

