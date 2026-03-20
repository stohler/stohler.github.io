from __future__ import annotations

import argparse
import logging
from typing import Sequence

from .ai_summarizer import AISummarizer
from .config import Settings, load_settings
from .news_fetcher import fetch_articles
from .post_builder import build_draft
from .rss_sources import TRUSTED_RSS_SOURCES
from .store import PostedStore
from .x_client import XCredentials, XPublisher

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def _publisher_from_settings(settings: Settings) -> XPublisher:
    missing = [
        name
        for name, value in {
            "X_API_KEY": settings.x_api_key,
            "X_API_SECRET": settings.x_api_secret,
            "X_ACCESS_TOKEN": settings.x_access_token,
            "X_ACCESS_TOKEN_SECRET": settings.x_access_token_secret,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Credenciais do X ausentes: {', '.join(missing)}")

    credentials = XCredentials(
        api_key=settings.x_api_key or "",
        api_secret=settings.x_api_secret or "",
        access_token=settings.x_access_token or "",
        access_token_secret=settings.x_access_token_secret or "",
    )
    return XPublisher(credentials)


def run(settings: Settings) -> int:
    store = PostedStore(settings.state_file)
    summarizer = AISummarizer(api_key=settings.gemini_api_key, model=settings.gemini_model)

    articles = fetch_articles(
        sources=TRUSTED_RSS_SOURCES,
        topic=settings.topic,
        keywords=settings.topic_keywords,
        lookback_hours=settings.lookback_hours,
        max_articles=settings.max_articles,
    )
    if not articles:
        logger.warning("Nenhuma notícia encontrada para o tema '%s'.", settings.topic)
        return 0

    selected = [article for article in articles if not store.has_link(article.link)]
    if not selected:
        logger.info("Sem novas notícias inéditas para publicar.")
        return 0

    posts_to_create = min(settings.posts_per_run, len(selected))
    selected = selected[:posts_to_create]
    publisher = None if settings.dry_run else _publisher_from_settings(settings)

    for article in selected:
        summary = summarizer.summarize_for_x(topic=settings.topic, article=article)
        draft = build_draft(topic=settings.topic, article=article, summary=summary)

        if settings.dry_run:
            logger.info("[DRY RUN] Post gerado:\n%s\n", draft.text)
        else:
            tweet_id = publisher.publish(text=draft.text, image_url=article.image_url) if publisher else ""
            logger.info("Post publicado no X com id=%s", tweet_id)

        store.add_link(article.link)

    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agente diário de notícias para X.")
    parser.add_argument(
        "--posts-per-run",
        type=int,
        default=None,
        help="Sobrescreve POSTS_PER_RUN no .env para este comando.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    configure_logging()
    args = parse_args(argv)
    settings = load_settings()

    if args.posts_per_run is not None:
        settings.posts_per_run = max(1, args.posts_per_run)

    raise SystemExit(run(settings))


if __name__ == "__main__":
    main()

