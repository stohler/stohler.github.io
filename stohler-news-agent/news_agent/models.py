from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Article:
    source: str
    title: str
    link: str
    published: datetime
    summary: str
    image_url: str | None = None
    score: float = 0.0


@dataclass(slots=True)
class DraftPost:
    article: Article
    text: str

