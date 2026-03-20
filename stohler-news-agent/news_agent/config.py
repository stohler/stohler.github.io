from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    topic: str
    topic_keywords: list[str]
    posts_per_run: int
    max_articles: int
    lookback_hours: int
    gemini_api_key: str | None
    gemini_model: str
    x_api_key: str | None
    x_api_secret: str | None
    x_access_token: str | None
    x_access_token_secret: str | None
    dry_run: bool
    state_file: Path


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    load_dotenv()

    topic = os.getenv("TOPIC", "").strip()
    if not topic:
        raise ValueError("Defina TOPIC no .env para escolher o tema.")

    keywords = _parse_csv(os.getenv("TOPIC_KEYWORDS"))
    if not keywords:
        keywords = [word for word in topic.lower().split() if word]

    state_file = Path(os.getenv("STATE_FILE", ".state/posted_articles.json")).resolve()

    return Settings(
        topic=topic,
        topic_keywords=keywords,
        posts_per_run=int(os.getenv("POSTS_PER_RUN", "1")),
        max_articles=int(os.getenv("MAX_ARTICLES", "40")),
        lookback_hours=int(os.getenv("LOOKBACK_HOURS", "48")),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        x_api_key=os.getenv("X_API_KEY"),
        x_api_secret=os.getenv("X_API_SECRET"),
        x_access_token=os.getenv("X_ACCESS_TOKEN"),
        x_access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
        dry_run=_bool_env("DRY_RUN", default=True),
        state_file=state_file,
    )

