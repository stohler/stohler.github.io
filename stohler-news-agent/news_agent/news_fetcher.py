from __future__ import annotations

import html
import re
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Any

import feedparser
import requests
from bs4 import BeautifulSoup

from .models import Article


def _clean_text(value: str) -> str:
    soup = BeautifulSoup(value or "", "html.parser")
    text = soup.get_text(" ", strip=True)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_image(entry: Any) -> str | None:
    media_content = getattr(entry, "media_content", None) or []
    for media in media_content:
        url = media.get("url")
        media_type = (media.get("type") or "").lower()
        if url and (not media_type or media_type.startswith("image/")):
            return url

    media_thumbnail = getattr(entry, "media_thumbnail", None) or []
    for media in media_thumbnail:
        url = media.get("url")
        if url:
            return url

    for link in getattr(entry, "links", []) or []:
        rel = (link.get("rel") or "").lower()
        media_type = (link.get("type") or "").lower()
        href = link.get("href")
        if href and rel == "enclosure" and media_type.startswith("image/"):
            return href

    return None


def _parse_published(entry: Any) -> datetime:
    for key in ("published", "updated", "created"):
        raw = getattr(entry, key, None)
        if not raw:
            continue
        try:
            parsed = parsedate_to_datetime(raw)
            return parsed.astimezone(UTC)
        except (TypeError, ValueError):
            continue
    return datetime.now(tz=UTC)


def _contains_term(text: str, term: str) -> bool:
    clean_term = term.strip().lower()
    if not clean_term:
        return False
    if " " in clean_term:
        return clean_term in text
    return bool(re.search(rf"\b{re.escape(clean_term)}\b", text))


def _topic_score(article: Article, topic: str, keywords: list[str]) -> float:
    haystack = f"{article.title} {article.summary}".lower()
    base = 0.0
    if _contains_term(haystack, topic.lower()):
        base += 4.0

    for keyword in keywords:
        if _contains_term(haystack, keyword):
            base += 1.2

    age_hours = max((datetime.now(tz=UTC) - article.published).total_seconds() / 3600.0, 0.0)
    recency_bonus = max(2.5 - (age_hours / 12.0), 0.0)
    return base + recency_bonus


def _matches_topic(article: Article, topic: str, keywords: list[str]) -> bool:
    haystack = f"{article.title} {article.summary}".lower()
    topic_terms = [term for term in re.split(r"\s+", topic.lower()) if len(term) >= 3]
    normalized_keywords = [keyword.lower() for keyword in keywords if len(keyword.strip()) >= 2]
    required_terms = list(dict.fromkeys(topic_terms + normalized_keywords))
    return any(_contains_term(haystack, term) for term in required_terms)


def fetch_articles(
    sources: dict[str, str],
    topic: str,
    keywords: list[str],
    lookback_hours: int,
    max_articles: int,
) -> list[Article]:
    cutoff = datetime.now(tz=UTC) - timedelta(hours=lookback_hours)
    all_articles: list[Article] = []
    for source_name, rss_url in sources.items():
        try:
            response = requests.get(rss_url, timeout=(8, 20), headers={"User-Agent": "stohler-news-agent/0.1"})
            response.raise_for_status()
            feed = feedparser.parse(response.content)
        except requests.RequestException:
            continue

        for entry in getattr(feed, "entries", []):
            title = _clean_text(getattr(entry, "title", ""))[:240]
            link = getattr(entry, "link", "")
            if not title or not link:
                continue

            published = _parse_published(entry)
            if published < cutoff:
                continue

            summary = _clean_text(getattr(entry, "summary", "") or getattr(entry, "description", ""))[:1200]
            article = Article(
                source=source_name,
                title=title,
                link=link,
                published=published,
                summary=summary,
                image_url=_extract_image(entry),
            )
            article.score = _topic_score(article, topic=topic, keywords=keywords)
            all_articles.append(article)

    all_articles.sort(key=lambda item: item.score, reverse=True)
    filtered = [
        article
        for article in all_articles
        if article.score >= 1.8 and _matches_topic(article, topic=topic, keywords=keywords)
    ]
    deduped: list[Article] = []
    seen_links: set[str] = set()

    for article in filtered:
        canonical = article.link.split("?")[0]
        if canonical in seen_links:
            continue
        seen_links.add(canonical)
        deduped.append(article)
        if len(deduped) >= max_articles:
            break

    return deduped

