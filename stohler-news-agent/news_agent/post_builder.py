from __future__ import annotations

import re

from .models import Article, DraftPost

X_CHAR_LIMIT = 280


def _normalize_hashtag(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9]", "", value.title())
    return f"#{clean}" if clean else ""


def _hashtags(topic: str) -> str:
    words = [word for word in topic.split() if len(word) > 2]
    custom = _normalize_hashtag("".join(words[:2])) if words else ""
    tags = [tag for tag in [custom, "#Notícias", "#Internacional"] if tag]
    return " ".join(dict.fromkeys(tags))


def build_post_text(topic: str, article: Article, summary: str) -> str:
    topic_tag = _hashtags(topic)
    source = article.source
    base = f"{summary} ({source}) {article.link} {topic_tag}".strip()

    if len(base) <= X_CHAR_LIMIT:
        return base

    reserved = len(f" ({source}) {article.link} {topic_tag}")
    available = max(X_CHAR_LIMIT - reserved - 1, 40)
    short_summary = summary[: available - 1].rstrip() + "…"
    return f"{short_summary} ({source}) {article.link} {topic_tag}".strip()


def build_draft(topic: str, article: Article, summary: str) -> DraftPost:
    return DraftPost(article=article, text=build_post_text(topic=topic, article=article, summary=summary))

